# Planning Phase for Generative AI Applications

## Overview

In Microsoft’s Generative AI application lifecycle, the Planning phase is where you lay the groundwork for a trustworthy and effective solution before any code is committed. You define what the application will do, choose the right model, connect data sources, and establish how you will evaluate quality and safety. This early investment ensures the design aligns with your goals and Microsoft’s Responsible AI standards from the start. Below is a step-by-step guide through the Planning phase, with each step linked to relevant Microsoft Learn resources.

## Step-by-Step Guide for Planning Phase

1. **Define the Application’s Scenario and Objectives**
Clearly identify the scenario, user needs, and tasks your application will handle. Determine the scope: Will it answer FAQs? Generate summaries? Provide recommendations? A well-defined scenario guides all subsequent decisions and ensures you build the right solution. Also consider Responsible AI or compliance requirements (e.g., sensitive data rules or user safety concerns) early. **Learn more:** [Responsible AI for Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-use-of-ai-overview?view=foundry)

2. **Select an Appropriate AI Model**
Choosing the right foundation model is critical. In Azure AI Foundry, use the Model Catalog and benchmark leaderboards to compare models on quality and safety metrics. Review leaderboards for performance, cost, and robustness, and run benchmarks on your own data if needed. Once selected, deploy the model so it’s ready for use.
**Learn more:** [Model Benchmarks](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/model-benchmarks?view=foundry)

3. **Connect Relevant Knowledge Bases**
Attach the contextual data your application needs to provide accurate outputs. In Foundry, integrate sources like Azure AI Search indexes, files, or databases so the application retrieves factual information instead of relying solely on the model’s internal knowledge.
**Learn more:** [Knowledgebase](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/knowledge-retrieval)

4. **Plan Any Tools or Actions the Application Needs**
Beyond static knowledge, consider whether your application should perform actions via external APIs or tools. Foundry supports adding tools such as web search, code execution, or custom business APIs. Identify these requirements early and gather necessary credentials or endpoints.
**Learn more:** [Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog?view=foundry)

5. **Prototype and Test in the Foundry Playground**
Use the Foundry Playground for quick, no-code testing. Simulate interactions, validate responses, and check basic metrics like fluency, relevance, and safety risk. This helps catch issues early and refine prompts or data connections before formal evaluations.
**Learn more:** [Foundry Playground](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/concept-playgrounds?view=foundry)

6. **Identify Key Evaluation Criteria (Quality & Safety)**
Plan how you will measure success. Common quality metrics include Relevance, Fluency, and Completeness. Safety metrics include detecting harmful content, preventing jailbreak attempts, and ensuring grounded responses. Define these criteria now to set the bar for moving into development.
**Learn more:** [Manual Evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/concept-playgrounds?view=foundry)

7. **Run a Batch Evaluation on a Test Dataset**
Before committing to full development, perform a baseline evaluation using a representative dataset. Use Foundry’s Evaluation SDK or cloud evaluation workflows to score your application on defined metrics and analyze failures for improvement.
**Learn more:** [Automated Evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/cloud-evaluation?view=foundry&tabs=python)

# End of Planning Phase
With a validated design and baseline performance data, transition to the Development phase. In development, you’ll integrate evaluations into CI/CD pipelines, perform adversarial testing (e.g., AI Red Teaming), and prepare for production deployment—ensuring your generative AI application is secure, reliable, and aligned with Responsible AI principles.