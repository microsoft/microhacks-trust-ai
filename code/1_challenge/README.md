# Challenge 1: Responsible AI - Designing a Reliable & Ethical Approach

## Overview
Contoso Electronics is piloting an internal HR Q&A applications where employees can ask about benefits and policies. The bot retrieves answers from policy documents with citations. Before full deployment, the team must ensure the AI behaves responsibly. In this challenge, participants act as AI developers conducting an AI Impact Assessment and initial testing using Azure AI FoundryIQ, Control Plane, and Chat Playground. 

## Tools & Config Needed
Azure AI FoundryIQ (agent creation + evaluation) 

Control Plane (deployment governance and monitoring) 

Azure AI Search (indexed data) 

Azure OpenAI model deployment 

Ground truth Q&A list (spreadsheet or FoundryIQ evaluation feature) 

## Lab Activities

From Azure Portal, go to resource group just created in CH0, find and go to Azure OpenAI service . 

<br>

![Alt text](/media/CH1_Resources.png "Resources")
<br>

Open the Azure Open AI resource in Foundry.

<br>

![Alt text](/media/CH1_Foundry.png "Foundry")
<br>
 

Go to Home, and then click on the "Get Started" button to get to the 'Azure OpenAI Service' to 'Microsoft Foundry' migration wizard.

<br>

![Alt text](/media/CH1_AzureOpenAI.png "AzureOpenAI")
<br>


Click on Next.

<br>

![Alt text](/media/CH1_Migration.png "Migration")
<br>


Click on "Confirm" and create a project-

<br>

![Alt text](/media/CH1_CreateProject.png "CreateProject")
<br>

Refer this documentation :
 https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/upgrade-azure-openai?view=foundry-classic&tabs=portal#how-to-upgrade

 
With the 2026 Foundry project rollout, enterprises get far more than just models.
You’ll now have access to agentic workflows, a broader model catalog, the Foundry SDK, and enhanced monitoring, observability, and evaluation capabilities - all designed to support multi‑agent architectures at scale. 
Your Azure OpenAI resource will be upgraded to the Microsoft Foundry resource

<br>

![Alt text](/media/CH1_Upgrade.png "Upgrade")
<br>


See your Foundry endpoint here, click on "Start building" - 
<br>

![Alt text](/media/CH1_FoundryHome.png "FoundryHome")
<br>


On the next page, expand the Start building dropdown, and click on "Create Agent"-

<br>

![Alt text](/media/CH1_CreateAgent.png "CreateAgent")
<br>

Give a name and create the agent-

<br>

![Alt text](/media/CH1_Agentname.png "Agentname")
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

![Alt text](/media/CH1_Monitor.png "Monitor")
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

<br>

![Alt text](/media/CH1_testAgent.png "testAgent")
<br>


At this point, you should be able to see some Monitoring data -
<br>

![Alt text](/media/CH1_MonitorAgent.png "MonitorAgent")
<br>


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



## Learning Resources

https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry
 
https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry?view=foundry-classic
 
https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search?tabs=indexing%2Cquickstarts
https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2

 

#  CHALLENGE 1 COMPLETE !!!