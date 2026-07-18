"""Run evaluation using the new Foundry portal evals flow.

This script keeps the existing target-app test shape (question -> app response),
but submits results through OpenAI evals APIs from AI Projects SDK so runs are
tracked in the newer Foundry experience.
"""

import argparse
import contextlib
import json
import os
import time
from pathlib import Path

import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def load_azd_env() -> None:
    """Load values from .azure/<env>/.env into process environment."""
    azure_dir = Path(__file__).parent.parent / ".azure"
    env_name = os.environ.get("AZURE_ENV_NAME", "")
    if not env_name and (azure_dir / "config.json").exists():
        with open(azure_dir / "config.json", encoding="utf-8") as f:
            config = json.load(f)
            env_name = config.get("defaultEnvironment", "")

    env_path = azure_dir / env_name / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def call_target_application(backend_url: str, question: str, timeout_seconds: int = 120) -> str:
    """Call the deployed app `/chat` endpoint and return text response."""
    response = requests.post(
        f"{backend_url}/chat",
        json={
            "message": question,
            "conversation_history": [],
            "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
            "max_tokens": 2048,
        },
        headers={"Content-Type": "application/json"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("response", payload.get("message", ""))


def poll_eval_run(openai_client, eval_id: str, run_id: str, poll_seconds: int = 5, timeout_seconds: int = 1800):
    """Poll an eval run until it reaches terminal status."""
    terminal_states = {"completed", "failed", "canceled"}
    started = time.time()

    while True:
        run = openai_client.evals.runs.retrieve(run_id=run_id, eval_id=eval_id)
        status = getattr(run, "status", "unknown")
        print(f"Run status: {status}")

        if status in terminal_states:
            return run

        if time.time() - started > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for eval run {run_id} after {timeout_seconds} seconds")

        time.sleep(poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run new-portal Foundry evaluation against deployed app responses")
    parser.add_argument("--max-items", type=int, default=0, help="Optional limit of dataset rows to evaluate")
    args = parser.parse_args()

    load_azd_env()

    backend_url = os.environ.get("AZURE_CONTAINER_APP_URL", "")
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    judge_model = os.environ.get("AZURE_EVAL_MODEL", "gpt-5.1")

    if not backend_url:
        raise ValueError("AZURE_CONTAINER_APP_URL not set")
    if not project_endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT not set")

    data_path = Path(__file__).parent.parent / "evals" / "ground_truth_small.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent / "evals" / "ground_truth.jsonl"
    if not data_path.exists():
        raise FileNotFoundError("Expected evals/ground_truth_small.jsonl or evals/ground_truth.jsonl")

    # Build run content by executing the current app (same behavior as classic script).
    rows = []
    with open(data_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append(item)

    if args.max_items > 0:
        rows = rows[: args.max_items]

    print(f"Loaded {len(rows)} evaluation items from {data_path}")
    print(f"Collecting application responses from: {backend_url}")

    run_content = []
    for idx, row in enumerate(rows, start=1):
        query = row["question"]
        truth = row.get("truth", "")
        try:
            response_text = call_target_application(backend_url, query)
        except Exception as exc:  # noqa: BLE001
            response_text = f"Error calling app: {exc}"

        run_content.append(
            {
                "item": {"query": query, "truth": truth},
                "sample": {"output_text": response_text},
            }
        )
        print(f"  [{idx}/{len(rows)}] collected response")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        eval_definition = openai_client.evals.create(
            name="microhack-target-eval-new-portal",
            data_source_config={
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "truth": {"type": "string"},
                    },
                    "required": ["query", "truth"],
                },
                "include_sample_schema": True,
            },
            testing_criteria=[
                {
                    "type": "azure_ai_evaluator",
                    "name": "relevance",
                    "evaluator_name": "builtin.relevance",
                    "initialization_parameters": {"deployment_name": judge_model},
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    },
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "groundedness",
                    "evaluator_name": "builtin.groundedness",
                    "initialization_parameters": {"deployment_name": judge_model},
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                        "context": "{{item.truth}}",
                    },
                },
            ],
        )

        print(f"Created eval definition: {eval_definition.id}")

        eval_run = openai_client.evals.runs.create(
            eval_id=eval_definition.id,
            name="microhack-target-run-new-portal",
            data_source={
                "type": "jsonl",
                "source": {
                    "type": "file_content",
                    "content": run_content,
                },
            },
        )

        print(f"Created eval run: {eval_run.id}")
        final_run = poll_eval_run(openai_client, eval_definition.id, eval_run.id)

        print("\n=== Run Complete ===")
        print(f"Status: {final_run.status}")
        print(f"Eval ID: {eval_definition.id}")
        print(f"Run ID: {eval_run.id}")

        # Best-effort helper URL for portal navigation.
        print("\nOpen the Foundry portal and go to Evaluate to locate this run by ID.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()