# Challenge 2: Well-Architected & Trustworthy Foundation

## Overview
Contoso Electronics has vetted their HR Q&A application.  The governance committee wants the development team to ensure the application and environment meet enterprise security and compliance standards before deployment to production.  These standards need to ensure the application meets production requirements, the Generative AI application is trustworthy and red team exercises are conducted.

In Challenge 2, participants take the role of a DevOps/AI engineer in charge of UAT (User Acceptance Testing) for the Contoso Electronics solution. Microsoft’s guidance (via the Secure AI Framework and Azure Well-Architected Framework) emphasizes reviewing AI systems for security, privacy, and quality issues early in the deployment cycle. These steps correspond to the “Measure & Mitigate” stages of responsible AI, ensuring both the model outputs and the infrastructure are robust and secure.


** The repository itself cautions that the sample code is for demo purposes and should not be used in production without additional security hardening.
<br>
<br>

## Tools & Config Needed
1.	WAF & Security Compliance: The [Azure Review Checklist Spreadsheet](https://github.com/Azure/review-checklists/blob/main/spreadsheet/README.md) and [Azure Review Checklist Script](https://github.com/Azure/review-checklists/blob/main/scripts/checklist_graph.sh) on GitHub.
1. Automated Quality & Safety evaluation python scripts will run on the local compute environment and save the results in the Microsoft Foundry Portal.  A GPT-4o model will be our AI Judge to help us score each metric and provide a reason code for the rating.  These results are viewable in the portal.
1.	[Azure AI Foundry Red Teaming Agent](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic). The goal is to simulate a "red team" attack by programmatically running an agent to break the rules on the local development environment.
<br>

## Lab Activities

### Lab 1 - WAF & Security Compliance

Microsoft has developed Azure Review Checklists available to allow customers an automated way to validate that their infrastructure is aligned with the Secure Foundation Initiative and the Well Architected Framework (WAF).

1. Download the [Review Checklist script](https://github.com/Azure/review-checklists/blob/main/scripts/checklist_graph.sh)
<br>

2. Open up Cloud Shell and switch to Bash mode.
<br>

   ![Alt text](/media/bashmode.jpg "CloudShell Bash Mode")
<br>

3. From the Shell, go to Manage Files and upload the script.
<br>

   ![Alt text](/media/managefiles.jpg "Manage Files")
<br>

4. Run this command in the bash terminal for CloudShell to change the file permissions
    
    ```bash
     chmod +xr ./checklist_graph.sh
     ```

5. Run this command in the terminal
    
    ```bash
    ./checklist_graph.sh --technology=ai_lz --format=json > ./graph_results.json
    ```

6. Download the graph results file to be imported into the Checklist spreadsheet.
<br>

   ![Alt text](/media/downloadjson.jpg "Download File")

<br>

7. Download the [Azure Review Checklist](https://github.com/Azure/review-checklists/releases/latest/download/review_checklist.xlsm).  Go into the File properties for the downloaded file and "unblock" the execution of macros.

   ![Alt text](/media/unblockmacro.jpg "Unblock Macros")
<br>

8. Click the control button "Import latest" in the Azure Review Checklist box. After you accept the verification message, the spreadsheet will load the latest version of the _AI Landing Zone Checklist_.

   ![Alt text](/media/spreadsheet_screenshot.png "Spreadsheet Screenshot")

<br>

9. In the spreadsheet, use the Advanced command "Import Graph Results" to import the previously downloaded file in Step #6.
<br>

   ![Alt text](/media/advanced_commands.png "Advanced Commands Screenshot")
   
<br>

10. Review the checklist items and their status to see which ones are out of compliance.  The "Comments" column of the spreadsheet will fill in with the results of the Azure Graph Queries, and display resource IDs that are compliant or non-compliant with the recommendation.  Discuss the potential changes you would need to make but don't actually implement them.

      ![Alt text](/media/alz_checklist.png "ALZ Review Checklist")
<br>
<br>

WAF & Security Compliance are now complete and the infrastructure is ready for production.  We will need to run application testing to evaluate if our application is safe and high quality.
<br>
<br>

### Lab 2 - Automated Quality & Safety Evaluations
<br>

In Challenge 1, we tested our application with a small subset of questions and had a human judge gauge their accuracy. (Manual Evaluations) We want to scale these tests from a handful of questions to 100s of questions to measure the quality and safety of the application.  Automated evaluation scripts leveraging the Azure AI Evaluation SDK will enable us to use a predefined list of questions, answers, context and ground truth to submit into these models.  The results returned by these models will be evaluated by an “AI-Judge” (LLM model) to rate their quality, safety and reason for their scores.  These results will be saved into Microsoft Foundry.

1. Review the [list of questions](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/evals/ground_truth.jsonl) to assess whether these questions are representative of the questions users will ask the HR Q&A application.  There are open-source frameworks that can generate a list of question and answer pairs.  In this repo, there is a [Generate Ground Truth data script](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/evaluation.md#generate-ground-truth-data) that generates questions/answer pairs that humans should review to ensure their quality.  Due to time/costs, we will only leverage the pre-defined list and will not generate any new questions.

1. Based on CH1 Impact Assessment, you should have a list of evaluation metrics to measure quality and safety.  This application generates text responses in a Q&A format.  Due to this, we plan to leverage the ["General Purpose" Evaluators](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/general-purpose-evaluators?view=foundry-classic) for quality.  Based on your use case, you will need to determine which evaluation metrics are best suited for your application.  Due to time/cost, we leverage relevance & groundedness for simplicity.  Each one of the evaluation scripts (quality & safety) defines the metrics and maps the results from the [target application to the ground truth data file](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk?view=foundry-classic&viewFallbackFrom=foundry#local-evaluation-on-a-target).

     ![Alt text](/media/quality_metrics.png "ALZ Review Checklist")

1. Go to the command line terminal in codespaces and submit this script to run quality metrics.  

    ```bash
    python evals/evaluatemh.py
    ```

   If you are using the default settings it will take approximately 1 minute for this to complete. The Target application is running in a container and might need you to rerun this script multiple times when it times-out.  Go into the Microsoft Foundry and review the Automated Evaluations.  Review each Q&A pair for these scores and reason.  

1. For each metric, review the number of success and failures in the Foundry portal to see overall success rate.  

   ![Alt text](/media/ai-quality-ai-assisted-chart.png "AI Quality Metrics")

1. For more information on quality evaluation scripts, read the [Quality Evaluation](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/evaluation.md) file for RAGCHAT application.

1. The second set of evaluations will be for the safety metrics.  Safety evaluations will ensure the answers are appropriate and do not contain harmful or sensitive content. Run this command in the terminal.

   ```bash
   python evals/safety_evaluationmh.py --target_url <TARGET_URL> --max_simulations <MAX_RESULTS>
   ```
   The parameters are:
   * `--target_url`: The target URL for the callback. Default is `http://localhost:50505/chat`.  The TARGET_URL is the Application URL in the Azure Container App.
   * `--max_simulations`: The maximum number of simulated user queries. Default is `200`. The higher the number, the longer the evaluation will take. The default of `200` simulations will take about 25 minutes to run, which includes both the time to generate the simulated data and the time to evaluate it.  

   We recommend keeping the max simulations at '2' for the number of times the script will ask follow-up questions from the main question in your question & answer pair.  For time/cost reasons, we are only using five simulations, but it is recommended for production workloads to test a larger number of simulations. For further instructions on [safety evaluations](https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/docs/safety_evaluation.md), review this file for guidance.
 
 1. Evaluate the Safety metrics and share with the team to determine if they are acceptable.  

    ![Alt text](/media/risk-and-safety-chart.png "AI Safety Metrics")

<br>
Automated Quality & Safety evaluations have validated our application meets our governance rules.  The last step is to determine if the application can handle adversarial attacks.

<br>

### Lab 3- Run Red Teaming Agent in Microsoft Foundry

The AI Red Team Agent will be able to assess risk categories and attack strategies to assess the Attack Success Rate of your application.  The lower the score, the more secure your application.  The justification for these tests is to run simulations of attacks based on known threats.  It is recommended to conduct both automated and human red teaming to cover the known and unknown attack strategies before you roll out to production. 

1. Execute the Red Team agent script.  The Red Teaming agent will use a library of [attack prompts across categories](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic#supported-risk-categories) (privacy, toxicity, jailbreak attempts, etc.) as defined by RiskCategories in PyRIT.

   ```bash
   python evals/redteammh.py
   ```

1. The [AI Red teaming results](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent?view=foundry-classic#results-from-your-automated-scans) typically categorizes findings like: number of attempts where the LLM gave a policy-violating response vs. how many it safely refused. Focus on critical categories: Did the LLM ever reveal the content of its system prompt or internal knowledge (a sign of prompt injection success)? Did it produce disallowed content (e.g., instructions to do something harmful) when provoked?  

1. After the scan, review the results carefully. If any serious red team findings appear, this is a fail. For instance, if the report shows the LLM gave out the full text of one of the confidential source documents when asked in a tricky way (data leakage), or it complied with an instruction like “ignore previous rules”, then you’ve got a major issue to fix.

    ![Alt text](/media/ai-red-team-data.png "AI Red Team Results")
<br>
<br>

## Success Criteria
1.	WAF Compliance exceeds 70 to 80% (varies by intensity).  Review the spreadsheet and open the dashboard tab.  Find the Review status and see if the number of open items is less than 30%.  If this is not the case, you’ll need to review the checklist until you mitigate enough open issues that allows you to reach this threshold.
1.	Automated Quality evaluations are no more than 90% for each metric and the safety scores are at 100% for all metrics.  Review the list of quality metrics; groundedness and relevance for quality while safety metrics are hate, sexual, violence and self-harm.  Review the summary score of these four metrics and ensure it is at 100%.
1.	Red Team Security testing should have a result category of "Conditional".  This means most criteria are met with minor issues.  There are eight attack categories tested with advanced evasion techniques.  Review the results as a learning opportunity but do not attempt to mitigate the issues to improve the scores due to time constraints of the Microhack.

After you complete all the success criteria, follow the steps in the [Challenge 3 -- Observability & Operations](/code/3_challenge/README.md) to run the workshop. 
<br>
<br>

## Best Practices
Azure Well-Architected Framework (WAF) and Azure AI Landing Zones are a guidebook on how to deploy any Generative AI application to production.  The reference Azure OpenAI landing zone architecture emphasizes network isolation, key management, and monitoring for enterprise deployments. Always review demo code deployments (like this GitHub sample) for settings that are left open for convenience and tighten them for production.

Automated Evaluations: It’s important to continuously test AI systems, not just once. Evaluation SDK lets you turn manual test cases into automated ones, ensuring you can run regression tests quickly. Our use of quality, safety and red teaming tests reflects a practice of establishing metrics and experiments to measure compliance. According to Microsoft’s Responsible AI guidance, after identifying risks you should “establish clear metrics” and do systematic testing, both manual and automated. 

AI Red Teaming: Using PyRIT and AI Red Team agent via the Microsoft Foundry are a state-of-the-art way to simulate adversaries. Microsoft highlights that their AI engineering teams follow a pattern of “iterative red-teaming and stress-testing” during development. By employing the same, we uncovered any vulnerabilities while still in UAT. The fact that our chatbot (hopefully) withstood the PyRIT onslaught without critical failures means it’s robust against known attack patterns.

After Challenge 2, the AI system is much more trustworthy: not only does it answer correctly (Challenge 1) but it also runs in a locked-down environment and resists misuse. This sets the stage for deployment – which we handle in Challenge 3 with a focus on operational monitoring and DevOps.
<br>
<br>

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

<br>
<br>

#  CHALLENGE 2 COMPLETE !!!
