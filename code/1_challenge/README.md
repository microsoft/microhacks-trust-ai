# Challenge 1: Responsible AI - Designing a Reliable & Ethical Approach

## Overview
Contoso Electronics is piloting an internal HR Q&A applications where employees can ask about benefits and policies. The bot retrieves answers from policy documents with citations. Before full deployment, the team must ensure the AI behaves responsibly. In this challenge, participants act as AI developers conducting an AI Impact Assessment and initial testing using Azure AI FoundryIQ, Control Plane, and Chat Playground. 

## Tools & Config Needed
Azure AI FoundryIQ (agent creation + evaluation) 

Control Plane (deployment governance and monitoring) 

Azure AI Search (indexed data) 

Azure OpenAI model deployment 

Ground truth Q&A list (spreadsheet or FoundryIQ evaluation feature) 

---
## Lab Activities

## Lab 1 – Microsoft Foundry Setup

### Objective

Set up your environment in Microsoft Foundry, create your first AI Agent, connect it to Azure AI Search, configure monitoring and guardrails, and prepare the agent for evaluation and responsible AI review.
By the end of this lab, you will have a fully functional AI Agent with a search tool, knowledge base, monitoring, compliance controls, and evaluation pipeline enabled.

### Key Tasks

Set up your Foundry Agent workspace by creating a new Agent in the Microsoft Foundry portal.
Review and manage available models, including inspecting deployed models and optionally deploying additional base models from the catalog.
Integrate Azure AI Search as a tool within the Agent to enable grounded retrieval capabilities.
Configure or create a search index linked to your storage account to support document grounding.
Enable RBAC and permissions for the Foundry project identity on Azure AI Search to allow index access and queries.
Define system instructions for the Agent to guide tool usage and retrieval behavior.
Enable monitoring and observability by connecting the Agent to Application Insights.
Create and attach a Knowledge Base through Foundry IQ, backed by your Azure AI Search index.

---

### Lab 1 – Instructions

Once you are on the Foundry portal, click on "Start building" and that switches you to the New Microsoft Foundry portal - 
<br>

![Alt text](/media/CH1_FoundryHome.png "FoundryHome")
<br>


On the next page, expand the Start building dropdown, and click on "Create Agent"-

<br>

![Alt text](/media/CH1_CreateAgent.png "CreateAgent")
<br>

Give a name and create the agent-

<br>

![Alt text](/media/CH1_AgentName.png "Agentname")
<br>

Go to the Models tab, you should be able to see all the deployed models under the 'Deployed' tab.

<br>

![Alt text](/media/CH1_Models.png "Models")
<br>


If you want to deploy any additional model of your choice, click on 'Deploy base model' and you should be able to explore all the available models and deploy any model of your choice -

<br>

![Alt text](/media/CH1_ModelCatalog.png "Model Catalog")
<br>

Explore model details:

<br>

![Alt text](/media/CH1_ModelDetails.png "Model Details")
<br>


In the Agent playground, Connect your Agent to Tools, select Azure AI search and Add tool-

<br>

![Alt text](/media/CH1_AddTool.png "AddTool")
<br>


On the "Create a new connection" page, Select the already created Azure AI Search resource from the dropdown and Connect-

<br>

![Alt text](/media/CH1_CreateConnection.png "CreateConnection")
<br>


Add search index - 


<br>

![Alt text](/media/CH1_AddIndex.png "AddIndex")
<br>


If you want to create a new index on the Azure AI Search resource, select the "Storage account" that is already created in your resource group in CH0 and select the 'content' container

Before hitting the "Create index" button, go to your Azure AI Search resource, to Enable AI Search RBAC with Foundry project identity

To enable RBAC:
From the left pane, select Settings > Keys. 
Select Both to enable both key-based and keyless authentication, which is recommended for most scenarios. 

<br>

![Alt text](/media/CH1_keys.png "Keys")
<br>


2. To assign the necessary roles: 

From the left pane, select Access control (IAM). 
Select Add > Add role assignment. 
Assign the Search Index Data Contributor role to the managed identity of your project. 
Repeat the role assignment for Search Service Contributor. 

<br>

![Alt text](/media/CH1_RoleAssignment.png "RoleAssignment")
<br>


Add instructions to your agent to help it invoke the right tools. 

Save the agent configurations, go to the Monitor tab and Connect the agent to the App Insights resource created in CH0. 
<br>

![Alt text](/media/CH1_monitor.png "Monitor")
<br>


Go back to the Foundry agent, under Knowledge, click on "Connect to Foundry IQ"
<br>

![Alt text](/media/CH1_FoundryIQ.png "FoundryIQ")
<br>

Create a new base on the Azure AI Search and save your agent
<br>

![Alt text](/media/CH1_knowledgebase.png "knowledgebase")
<br>


Test your agent-
Ask some sample questions, available here - (https://github.com/Azure-Samples/azure-search-openai-demo/blob/main/evals/ground_truth.jsonl)

---

## Lab 2 – Responsible AI Impact Assessment

### Objective

Identify and assess the Responsible AI risks associated with your HR Agent, document their severity and likelihood, define mitigation strategies, assign ownership, and ensure alignment with Responsible AI principles before the agent is approved for deployment.

### Key Tasks
Validate knowledge quality by confirming HR policy documents are correctly indexed and searchable.
Identify responsible AI risks such as outdated information, biased responses, privacy/PII exposure, or unsafe/misuse attempts.
Assess severity and likelihood for each identified risk.
Define mitigation strategies including update workflows, inclusive language reviews, safety refusals, PII protection, and guardrail enforcement.
Assign owners accountable for addressing each mitigation (HR, AI engineering, privacy/compliance, etc.).
Align the solution with Microsoft Responsible AI principles (fairness, privacy, transparency, safety, inclusiveness, accountability).
Review the assessment with stakeholders such as HR, Legal, Privacy, and AI Ethics teams.
Incorporate feedback and update the assessment to reflect organizational expectations.
Obtain formal sign-off on the Impact Assessment before proceeding to evaluation and deployment readiness.

---

### Lab 2 – Instructions

After validating HR documents are searchable, open the Responsible AI Impact Assessment template, list potential risks (e.g., outdated info, bias, privacy leaks), assess severity and likelihood, define mitigations for each risk (like update workflows, inclusive language, refusal for personal data), assign owners, confirm alignment with Responsible AI principles (fairness, transparency, privacy), review with HR, Legal, and AI ethics stakeholders, incorporate feedback, and obtain formal sign-off before deployment.

Impact Assessment -

1.Identified Risk	

Outdated or incorrect policy info (agent might give obsolete answers if documents aren’t updated)

Mitigation Strategy:	
– Schedule regular updates of the HR policy index (e.g., after any HR policy change).
– Implement a content update checklist with HR team for new/changed policies.– Include policy last-updated timestamps in answers, if feasible, to flag potentially old info.

Owner Accountable:
	HR Knowledge Manager (ensures documents & index stay current)	

2. Identified Risk:
Biased or uneven answers (e.g., gendered language or differing info for different groups)

Mitigation Strategy:
– Review and revise policy wording for inclusive language (e.g., use “primary caregiver” instead of “mother”).
– Add system prompt guidance to use neutral tone and equal detail for all users.– Test with diverse query phrasing (male vs female perspective, etc.) and verify consistent responses.

Owner Accountable:
	AI Developer (updates prompts & tests); HR Policy Analyst (reviews content for bias)	

3. Identified Risk:
Personal data exposure (user asks for individual’s info or system reveals PII)

Mitigation Strategy:	
– Restrict knowledge sources to non-PII documents only (no personal files indexed).
– Model instructed to refuse requests for personal/sensitive data.
– Enable content filter/DLP for PII (e.g., detect patterns like SSN, phone # in outputs).– Test queries asking for private data to ensure the agent safely refuses.

Owner Accountable:
	Solution Architect / Privacy Officer (ensures data scope and compliance)

4. Identified Risk:	
Misuse or unsafe requests (attempts to get the bot to violate policies or produce harmful content)

Mitigation Strategy:	
– Employ Azure AI Content Safety and Foundry guardrails (already active) ] to block disallowed content.
– Keep system and safety prompts in place to enforce refusals for out-of-scope questions.
– Conduct red-team testing (prompt injections, extreme inputs) and adjust safeguards if any gap is found.– Log and review misuse attempts to continuously improve defenses.

Owner Accountable:
AI Engineering Lead (sets guardrail configs and reviews security logs)	


Conducting this Responsible AI Impact Assessment not only mitigates risks but also builds confidence among stakeholders and users. Employees will trust the HR assistant more knowing it’s been thoughtfully vetted, and your organization can deploy it knowing that ethical and legal considerations have been addressed up front. This thorough, proactive approach exemplifies Responsible AI in practice – delivering the benefits of AI (quick HR answers and improved productivity) while minimizing potential downsides through careful planning and oversight.
Now that the Impact Assessment is drafted with risks and mitigations, it needs to be reviewed and signed off by the appropriate stakeholders before the HR assistant goes live. 
Once the Impact Assessment is approved, the next step is to validate the agent’s real-world performance through manual evaluation.


<br>

![Alt text](/media/CH1_testAgent.png "testAgent")
<br>


At this point, you should be able to see some Monitoring data -
<br>

![Alt text](/media/CH1_MonitorAgent.png "MonitorAgent")
<br>

---

## Lab 3 – Guardrails and Evaluations

### Objective

Configure guardrail policies and run automated evaluations in Microsoft Foundry to ensure your Agent operates safely, complies with organizational standards, and delivers accurate, grounded, and reliable responses before deployment.

### Key Tasks

Create a Guardrail Policy using Foundry’s Compliance workspace to enforce content safety filters, prompt shields, and groundedness checks.
Configure policy scope and exceptions at the subscription or resource group level to control which model deployments must comply.
Review and finalize the guardrail configuration, ensuring controls align with responsible AI requirements and organizational governance.
Upload the ground_truth dataset to the Evaluations workspace for accuracy and groundedness testing.
Run an automated evaluation job to measure relevance, groundedness, safety, and policy compliance of the Agent’s responses.
Analyze evaluation metrics and results, including failed cases, reasoning traces, and quality indicators.
Validate monitoring signals in Application Insights to ensure observability during evaluation.
Confirm evaluation readiness for deployment, ensuring guardrails, safety checks, and performance metrics meet the required thresholds.

---

### Lab 3 – Instructions

Create a guardrail policy- 

Refer - https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/quickstart-create-guardrail-policy?view=foundry

<br>

![Alt text](/media/CH1_Operate.png "Operate")
<br>


Select Operate from the upper-right navigation.
Select Compliance in the left pane.
Select Create policy.
Select the controls to be added to the policy. Guardrail controls include content safety filters, prompt shields, and groundedness checks that help ensure your AI models operate safely and responsibly. These controls represent the minimum settings required for a model deployment to be considered compliant with the policy. As you configure each control, select Add control to add it to the policy.
Select Next to move to scope selection. You can scope your policy to a single subscription or a resource group. Select the desired scope and then select a subscription or resource group from a list of resources that you have access to. We are selecting the scope at our resource level.
Pick the desired subscription or resource group to apply to the policy and select Select.
Select Next to add exceptions to the policy. The exception options depend on your scope selection:If you scoped to a subscription, you can create exceptions for entire resource groups or individual model deployments within that subscription.
If you scoped to a resource group, you can only create exceptions for individual model deployments.
Once all exceptions have been added, select Next to move to the review stage. Here, you name your policy and review the scope, exceptions, and controls that define the policy. Once ready, select Submit to create the policy.

<br>

![Alt text](/media/CH1_Compliance.png "Compliance")
<br>


Go back to the agent, and to the Evaluations tab. upload the ground_truth dataset.
<br>

![Alt text](/media/CH1_truth.png "Truth")
<br>


Review and run the evaluation.
Wait for the evaluation to be completed.
<br>

![Alt text](/media/CH1_Evaluation.png "Evaluation")
<br>


See all metrics in the Evaluations tab -
<br>

![Alt text](/media/CH1_EvaluationMetrics.png "EvaluationMetrics")
<br>


## Success Criteria

To successfully complete this lab, you must meet all of the following criteria:

1. Successfully Migrate Azure OpenAI to Microsoft Foundry

Open the CH0 Azure OpenAI resource in Microsoft Foundry
Complete the Azure OpenAI → Foundry migration
Confirm Foundry project creation


2. Create a New Agent in Foundry

From the Foundry portal, create an agent in the Foundry project and open the agent workspace to verify it is active.


3. Verify & Deploy Models

Navigate to the Models tab
Verify deployed Azure OpenAI models appear under Deployed
(Optional) Deploy an additional model from the Model Catalog


4. Connect the Agent to Azure AI Search (Tools Integration)

Add Azure AI Search from Tools
Select the correct Azure AI Search resource and create or choose an index from the storage content container
Enable Search RBAC with key and keyless auth and assign required roles to the Foundry managed identity
Verify the tool appears in the agent with no configuration errors


5. Add Instructions to the Agent

Write clear system instructions defining when to use Azure AI Search
Save the agent configuration with no validation errors


6. Configure Monitoring

Open the Monitor tab, connect the agent to the Application Insights resource from CH0, and confirm telemetry is active


7. Connect Knowledge via Foundry IQ

Open the Knowledge tab and connect to Foundry IQ
Create a new Knowledge Base using the Azure AI Search index
Save the agent successfully


8. Test the Agent

Test the agent in the playground using sample questions from ground_truth.jsonl
Verify correct search retrieval, grounded responses, and no hallucinations
Observe monitoring/traces appearing in the Monitor tab.


9. Create a Guardrail Policy

Navigate to Operate → Compliance and create a Guardrail Policy with safety filters, prompt shields, and groundedness controls
Assign the policy scope to the correct subscription/resource group and submit successfully


10. Run Evaluations

Upload ground_truth.jsonl under Evaluations
Run an evaluation job and review accuracy, groundedness, citation validity, and safety

## Continue to Challenge 2 and 3

Since Microsoft Foundry is still in preview, please switch back to the classic (old) Foundry experience to complete Challenge 2 (Well-Architected & Trustworthy Foundation) and Challenge 3 (Observability & Operations).

## Learning Resources

https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry
 
https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry?view=foundry-classic
 
https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search?tabs=indexing%2Cquickstarts
https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2

 

#  CHALLENGE 1 COMPLETE !!!