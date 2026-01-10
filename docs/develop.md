# Development Phase for Generative AI Applications

The Development phase focuses on scaling evaluations, automating quality checks, and strengthening safety before production deployment. This ensures your application meets enterprise standards for reliability and Trustworthy AI.

## Step by Step Guide
1. Version and Configure Your Application
Create a stable version of your generative AI application in Azure AI Foundry or your chosen environment so changes can be tracked and compared. Finalize system prompts, attach any required tools or connectors, and save versions for controlled iteration.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/development-lifecycle

2. Integrate Evaluation Pipelines into CI/CD
Move from manual testing to automated evaluations. Use GitHub Actions or Azure DevOps workflows to run batch evaluations whenever code changes occur. This ensures regressions are caught early and quality remains consistent.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/cloud-evaluation

3. Apply Built-in Evaluators for Quality and Safety
Leverage the Azure AI Evaluation SDK to run comprehensive checks on metrics like Relevance, Fluency, Completeness, and safety indicators (e.g., harmful content, jailbreak attempts).
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk

4. Add Scenario-Specific Evaluators
For complex workflows or domain-specific use cases, include evaluators that measure critical aspects of your application, such as intent handling, response groundedness, and task adherence.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/agent-evaluate-sdk

5. Perform Adversarial Testing (Red Teaming)
Before production, run AI Red Teaming to simulate attacks and uncover vulnerabilities like prompt injection or unsafe outputs. This step is essential for governance and compliance.
Learn more: Responsible AI Practices

6. Validate at Scale
Use cloud-based evaluations to test large datasets and compare application versions statistically. This provides confidence that improvements are real and performance is stable.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/cloud-evaluation?view=foundry&tabs=python
