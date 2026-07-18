# Challenge 2: Well-Architected & Trustworthy Foundation

## Overview

Contoso Electronics has vetted their HR Q&A application.  The governance committee wants the development team to ensure the application and environment meet enterprise security and compliance standards before deployment to production.  These standards need to ensure the application meets production requirements, the Generative AI application is trustworthy and red team exercises are conducted.

In Challenge 2, participants take the role of a DevOps/AI engineer in charge of UAT (User Acceptance Testing) for the Contoso Electronics solution. Microsoft’s guidance (via the Secure AI Framework and Azure Well-Architected Framework) emphasizes reviewing AI systems for security, privacy, and quality issues early in the deployment cycle. These steps correspond to the “Measure & Mitigate” stages of responsible AI, ensuring both the model outputs and the infrastructure are robust and secure.

** The repository itself cautions that the sample code is for demo purposes and should not be used in production without additional security hardening.

</br>

## Tools & Config Needed

1. WAF & Security Compliance: The [Azure Review Checklist Spreadsheet](https://github.com/Azure/review-checklists/blob/main/spreadsheet/README.md) and [Azure Review Checklist Script](https://github.com/Azure/review-checklists/blob/main/scripts/checklist_graph.sh) on GitHub.

1. Automated Quality & Safety evaluation python scripts will run on the local compute environment and save the results in the Microsoft Foundry Portal.  A gpt-4o model will be our AI Judge to help us score each metric and provide a reason code for the rating.  These results are viewable in the portal.


1. [Azure AI Foundry Red Teaming Agent](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic). The goal is to simulate a "red team" attack by programmatically running an agent to break the rules on the local development environment.

1. Ensure the New Foundry Control Switch in the header of the Foundry Portal is switched "ON". 

</br>

## Lab Activities

### Lab 2.1 - WAF & Security Compliance

Microsoft has developed Azure Review Checklists available to allow customers an automated way to validate that their infrastructure is aligned with the Secure Foundation Initiative and the Well Architected Framework (WAF).

1. Open the [AI Landing Zone Checklist](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fgithub.com%2Fmicrosoft%2Fmicrohacks-trust-ai%2Fraw%2Fmain%2Fdocs%2Fch2_tai_review_checklist.xlsx) from this repo for your review.  The spreadsheet is prebuilt to reduce setup time for the Microhack.  There is a repo that contains instruction on how to implement it for your Generative AI Application.  [Azure Review Checklist](https://github.com/Azure/review-checklists/blob/main/spreadsheet/README.md).  We suggest for this hack to use the existing spreadsheet but for production deployments leverage the checklist to audit your system.

2. Review the AI Landing Zone checklist items and their status to see which ones are Open, Fulfilled, Not Verified or Not required.  Go to the tab called, "Dashboard" and review the overall status by Design areas.  Review the list for familiarity and discuss with the team any potential gaps.  This spreadsheet was built using a [private network](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/deploy_private.md) but was not 100% compliant with Azure AI Landing Zones.

      ![Alt text](/media/AILZ%20Dashboard.png "ALZ Review Checklist")
</br>

WAF & Security Compliance are now complete and the infrastructure is ready for production.  We will need to run application testing to evaluate if the application is safe and high quality.
</br>


### Lab 2.2 - Automated Quality & Safety Evaluations

</br>

In Challenge 1, we tested our application with a small subset of questions and had a human judge to gauge their accuracy (Manual Evaluations). We want to scale these tests from a handful of questions to hundreds of questions to measure the quality and safety of the application.  Automated evaluation scripts leveraging the Azure AI Evaluation SDK will enable us to use a predefined list of questions, answers, context and ground truth to submit into these models.  The results returned by these models will be evaluated by an “AI-Judge” (LLM model) to rate their quality, safety and reason for their scores.  These results will be saved into Microsoft Foundry.

1. Review the [list of questions](/evals/ground_truth.jsonl) to assess whether these questions are representative of the questions users will ask the HR Q&A application.  There are open-source frameworks that can generate a list of question and answer pairs.  In this repo, there is a [Generate Ground Truth data script](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/evaluation.md#generate-ground-truth-data) that generates questions/answer pairs that humans should review to ensure their quality.  Due to time/costs, we will only leverage the pre-defined list and will not generate any new questions.

1. Based on CH1 Impact Assessment, you should have a list of evaluation metrics to measure quality and safety.  This application generates text responses in a Q&A format.  Due to this, we plan to leverage the ["General Purpose" Evaluators](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/general-purpose-evaluators?view=foundry-classic) for quality.  Based on your use case, you will need to determine which evaluation metrics are best suited for your application.  Due to time/cost, we leverage relevance & groundedness for simplicity.  Each one of the evaluation scripts (quality & safety) defines the metrics and maps the results from the [target application to the ground truth data file](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk?view=foundry-classic&viewFallbackFrom=foundry#local-evaluation-on-a-target).

     ![Alt text](/media/quality_metrics.png "Quality Metrics")

1. Go to the command line terminal in codespaces and submit the following script to run quality metrics.  

### Updated Evaluation Commands (New vs Classic Foundry)

For the **new Foundry experience**, use:

```bash
python ./scripts/07_run_evaltarget_new_portal.py
```

   This evaluation will take approximately 20 seconds to complete. The Target application is running in a container and might need you to rerun this script multiple times when it times-out.  Go into the Microsoft Foundry and review the Automated Evaluations.  Review each Q&A pair for these scores and reason.  The script submits just 11 question & answer pairs to shorten execution time.

1. For each metric, review the number of success and failures in the Foundry portal to see overall success rate.  There is one question which fails due to the ground truth data having a typo.  This is intentional but demonstrates the need to review your questoins & ground truth data before running evaluations.  The correct value should be $2,000.  Due to time skip any fixes but sharing for guidance.

   ![Alt text](/media/ai-quality-ai-assisted-chart.png "AI Quality Metrics")

1. For more information on quality evaluation scripts, read the [Quality Evaluation](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/evaluation.md) file for RAGCHAT application.

1. The second set of evaluations will be for the safety metrics.  This scripts will generate by default 5 simulations which are adversarial questions to submit to the target application.  Safety evaluations will ensure the answers are appropriate and do not contain harmful or sensitive content. Run this command in the terminal.

   For the **new Foundry experience**, use:

   ```bash
   python ./scripts/08_safety_evals_new_portal.py
   ```

   The parameters are:
   * `--max_simulations`: The maximum number of simulated user queries. Default is `5`. The higher the number, the longer the evaluation will take. The default of `5` simulations will take about 1 minutes to run, which includes both the time to generate the simulated adversarial questions and the time to evaluate it.  

   We recommend keeping the max simulations at '5'.  For time/cost reasons, we are only using five simulations, but it is recommended for production workloads to test a larger number of simulations. For further instructions on [safety evaluations](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/safety_evaluation.md), review this file for guidance.
 
1. Evaluate the Safety metrics and share with the team to determine if they are acceptable.  

    ![Alt text](/media/risk-and-safety-chart.png "AI Safety Metrics")

Automated Quality & Safety evaluations have validated our application meets our governance rules.  The last step is to determine if the application can handle adversarial attacks.

</br>

### Lab 2.3- Run Red Teaming Agent in Microsoft Foundry

The AI Red Team Agent will be able to assess risk categories and attack strategies to assess the Attack Success Rate of your application.  The lower the score, the more secure your application.  The justification for these tests is to run simulations of attacks based on known threats.  It is recommended to conduct both automated and human red teaming to cover the known and unknown attack strategies before you roll out to production.

1. Execute the Red Team agent script.  The Red Teaming agent will use a library of [attack prompts across categories](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic#supported-risk-categories) By default, the script runs a baseline scan with no attack transformations. An advanced scan with multiple attack strategies (e.g., MODERATE, Base64, ROT13) is available but commented out in the script.

   For the **new Foundry experience**, use:

   ```bash
   python ./scripts/09_redteameval_new_portal.py
   ```

   * **New Foundry flow (`09_redteameval_new_portal.py`)**: Uses cloud Red Team runs in the new portal. The result schema and presentation differ from classic and may emphasize evaluator outcomes and run-level summaries instead of the same classic attack-technique layout.

1. The [AI Red teaming results](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic#results-from-your-automated-scans) typically categorizes findings like: number of attempts where the LLM gave a policy-violating response vs. how many it safely refused. Focus on critical categories: Did the LLM ever reveal the content of its system prompt or internal knowledge (a sign of prompt injection success)? Did it produce disallowed content (e.g., instructions to do something harmful) when provoked?  

1. After the scan, review the results carefully. The baseline "Basic" scan will typically have an ASR (Attack Success Rate) of 0%, meaning the Red Team agent was unable to elicit harmful responses. If you enable the advanced scan (commented out in the script), you may see a higher ASR as more sophisticated attack strategies are applied. This demonstrates the importance of Red Teaming to ensure you run a thorough evaluation of your Generative AI application, giving you greater confidence that it is ready for a production environment.

    ![Alt text](/media/ai-red-team-data.png "AI Red Team Results")

</br>

## Success Criteria

1.	Review the checklist of items and see which ones are "Open" and "Not Verified".  Peform a gap analysis and determine what needs to be done to ensure compliance.  This exercise is to help you gain familiarity with the Azure AI Landing Zones for future reference.  The exercise is not meant for you to complete/resolve these issues in your Azure Tenant.  For reference, we leveraged this deployment [private network](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/deploy_private.md) as our baseline if you like to understand the final deployment.

1. Review the list of quality metrics; groundedness and relevance for quality while safety metrics are hate, sexual, violence and self-harm.  Review the summary score of these six metrics and ensure it is above 90%.

1. Red Team Security testing measures the Attack Success Rate percentage.  0% means the red team agent was unable to successfully attack your application which is a win.  For this test, make sure your scores are lower than 20%.  Review the results as a learning opportunity but do not attempt to mitigate the issues to improve the scores due to time constraints of the Microhack.

</br>

## Continue to Challenge 3

After you complete all the success criteria, follow the steps in the [Challenge 3 -- Observability & Operations](/code/3_challenge/README.md) to run the workshop.

</br>

## Best Practices

Azure Well-Architected Framework (WAF) and Azure AI Landing Zones are a guidebook on how to deploy any Generative AI application to production.  The reference Azure OpenAI landing zone architecture emphasizes network isolation, key management, and monitoring for enterprise deployments. Always review demo code deployments (like this GitHub sample) for settings that are left open for convenience and tighten them for production.

Automated Evaluations: It’s important to continuously test AI systems, not just once. Evaluation SDK lets you turn manual test cases into automated ones, ensuring you can run regression tests quickly. Our use of quality, safety and red teaming tests reflects a practice of establishing metrics and experiments to measure compliance. According to Microsoft’s Responsible AI guidance, after identifying risks you should “establish clear metrics” and do systematic testing, both manual and automated. 

AI Red Teaming: Using PyRIT and AI Red Team agent via the Microsoft Foundry are a state-of-the-art way to simulate adversaries. Microsoft highlights that their AI engineering teams follow a pattern of “iterative red-teaming and stress-testing” during development. By employing the same, we uncovered any vulnerabilities while still in UAT. The fact that our chatbot (hopefully) withstood the PyRIT onslaught without critical failures means it’s robust against known attack patterns.

After Challenge 2, the AI system is much more trustworthy: not only does it answer correctly (Challenge 1) but it also runs in a locked-down environment and resists misuse. This sets the stage for deployment – which we handle in Challenge 3 with a focus on operational monitoring and DevOps.
</br>

## Learning Resources

### WAF & SFI

* [What is an Azure landing zone?](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
* [AI Ready - Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/ready)
* [Azure Review checklist](https://github.com/Azure/review-checklists)

### Quality & Safety Evaluations

* [RAGChat: Evaluating RAG answer quality video](https://www.youtube.com/watch?v=lyCLu53fb3g)
* [RAGChat: Slides for RAG answer quality slide](https://aka.ms/ragdeepdive/evaluation/slides)
* [Generate Synthetic and Simulated Data for Evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/simulator-interaction-data?view=foundry-classic)
* [See Evaluation Results in Microsoft Foundry portal](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/evaluate-results?view=foundry-classic)
* [Cloud Evaluation with the Microsoft Foundry SDK](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/cloud-evaluation?view=foundry-classic&source=recommendations&tabs=python)

### AI Red Teaming

* [AI Red Teaming Agent - Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent?view=foundry-classic)
* [Planning red teaming for large language models (LLMs) and their applications](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/red-teaming?view=foundry-classic)
* [Run AI Red Teaming Agent in the cloud (Microsoft Foundry SDK)](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-ai-red-teaming-cloud?view=foundry-classic&tabs=python)

</br>
</br>

# CHALLENGE 2 COMPLETE !!!
