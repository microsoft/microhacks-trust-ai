"""Run safety evaluations using the new Foundry portal evals flow.

This script mirrors `05_safety_evals.py` simulation behavior, but submits the
evaluation through OpenAI evals APIs from AI Projects SDK so runs appear in the
new Foundry evaluation experience.
"""

import argparse
import asyncio
import contextlib
import json
import logging
import os
import time
from pathlib import Path

import requests
from azure.ai.evaluation.simulator import (
    AdversarialScenario,
    AdversarialSimulator,
    SupportedLanguages,
)
from azure.ai.projects import AIProjectClient
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv


# Setup logging
logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger("safety_eval_new_portal")
logger.setLevel(logging.INFO)

OUTPUT_DIR = Path(__file__).parent.parent / "evals" / "results" / "safety"


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


def get_azure_credential() -> AzureDeveloperCliCredential:
    """Get Azure credential for simulator execution."""
    tenant_id = os.getenv("AZURE_TENANT_ID")
    if tenant_id:
        return AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
    return AzureDeveloperCliCredential(process_timeout=60)


def call_target_application(backend_url: str, query: str, timeout_seconds: int = 120) -> str:
    """Call the target app `/chat` endpoint and return response text."""
    response = requests.post(
        f"{backend_url}/chat",
        json={
            "message": query,
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


def save_simulation_data(run_content: list[dict]) -> None:
    """Persist generated adversarial prompts and app outputs as JSONL."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    simulation_data_path = OUTPUT_DIR / "simulation_data_v2_new_portal.jsonl"
    with open(simulation_data_path, "w", encoding="utf-8") as f:
        for row in run_content:
            item = {
                "query": row["item"]["query"],
                "response": row["sample"]["output_text"],
            }
            f.write(json.dumps(item) + "\n")
    print(f"Saved simulation data: {simulation_data_path}")


async def build_adversarial_run_content(backend_url: str, max_simulations: int, azure_ai_project: str) -> list[dict]:
    """Generate adversarial prompts and collect target app responses."""
    credential = get_azure_credential()
    adversarial_simulator = AdversarialSimulator(
        azure_ai_project=azure_ai_project,
        credential=credential,
    )

    async def callback(messages: list[dict], stream: bool = False, session_state=None, context=None):
        del stream, session_state, context
        messages_list = messages["messages"]
        latest_message = messages_list[-1]
        query = latest_message["content"]

        try:
            response_text = call_target_application(backend_url, query)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Error calling target application: {exc}")
            response_text = "I cannot process that request."

        return {
            "messages": messages_list + [{"content": response_text, "role": "assistant"}],
        }

    print(f"Running adversarial simulation with {max_simulations} max simulations...")
    outputs = await adversarial_simulator(
        scenario=AdversarialScenario.ADVERSARIAL_QA,
        target=callback,
        max_simulation_results=max_simulations,
        language=SupportedLanguages.English,
        randomization_seed=1,
    )

    run_content = []
    for output in outputs:
        messages = output.get("messages", [])
        if len(messages) < 2:
            continue
        query = messages[0].get("content", "")
        response_text = messages[1].get("content", "")
        if not query:
            continue

        run_content.append(
            {
                "item": {"query": query},
                "sample": {"output_text": response_text or ""},
            }
        )

    return run_content


def main() -> None:
    parser = argparse.ArgumentParser(description="Run new-portal Foundry safety evals against adversarial prompts")
    parser.add_argument("--max_simulations", type=int, default=5, help="Max adversarial simulations")
    args = parser.parse_args()

    load_azd_env()

    backend_url = os.environ.get("AZURE_CONTAINER_APP_URL", "")
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")

    if not backend_url:
        raise ValueError("AZURE_CONTAINER_APP_URL not set")
    if not project_endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT not set")

    run_content = asyncio.run(
        build_adversarial_run_content(
            backend_url=backend_url,
            max_simulations=args.max_simulations,
            azure_ai_project=project_endpoint,
        )
    )

    if not run_content:
        raise RuntimeError("No simulation output generated. Try increasing --max_simulations.")

    save_simulation_data(run_content)

    print(f"Generated {len(run_content)} adversarial samples")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        eval_definition = openai_client.evals.create(
            name="microhack-safety-eval-new-portal",
            data_source_config={
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
                "include_sample_schema": True,
            },
            testing_criteria=[
                {
                    "type": "azure_ai_evaluator",
                    "name": "violence",
                    "evaluator_name": "builtin.violence",
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    },
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "sexual",
                    "evaluator_name": "builtin.sexual",
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    },
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "self_harm",
                    "evaluator_name": "builtin.self_harm",
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    },
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "hate_unfairness",
                    "evaluator_name": "builtin.hate_unfairness",
                    "data_mapping": {
                        "query": "{{item.query}}",
                        "response": "{{sample.output_text}}",
                    },
                },
            ],
        )

        print(f"Created eval definition: {eval_definition.id}")

        eval_run = openai_client.evals.runs.create(
            eval_id=eval_definition.id,
            name="microhack-safety-run-new-portal",
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
        print("\nOpen the Foundry portal and go to Evaluate to locate this run by ID.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        main()