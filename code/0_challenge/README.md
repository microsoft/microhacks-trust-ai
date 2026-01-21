# Challenge 0: Environment Setup

If you’re running this workshop on your own, you'll need to deploy the workshop resources to your Azure subscription. Follow the instructions to deploy the workshop resources.

## Overview
We will set up the initial environment for you to build on top of during your Microhack. This comprehensive setup includes configuring essential Azure services and ensuring access to all necessary resources. Participants will familiarize themselves with the architecture, gaining insights into how various components interact to create a cohesive solution. With the foundational environment in place, the focus will shift seamlessly to the first Microhack Challenge endeavor.  
<br>
<br>
![Alt text](/media/architecture_ragchat.png "RAGCHAT Architecture")
<br>
<br>

## Prerequisites for Local Environment
1. A computer running Windows 11, macOS, or Linux.  Running on your local PC.
1. An Azure subscription. If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/free/).
1. Install the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).
1. Install [Powershell 7 (supported on Windows, macOS, and Linux)](https://learn.microsoft.com/powershell/scripting/install/installing-powershell).
1. Install [Python 3.13+](https://www.python.org/downloads/).
1. Install the Git CLI. You can download it from the [Git website](https://git-scm.com/downloads).
1. Install VS Code on your local PC if not using Codespaces.
<br>

## Support Software
* Azure Developer CLI: Download azd
* Ensure the correct OS is selected
* Powershell 7+ with AZ module (Windows only): Powershell, AZ Module
* Git: Download Git
* Python 3.13: Download Python
<br>

## Recommended Regions
* North Central US (northcentralus)
* South Central US (southcentralus)
* Sweden Central (swedencentral)
* West US (westus)
* West US 3 (westus3)
* East US (eastus)
* East US 2 (eastus2)

<br>

* Optimal Region for availability should be WestEurope for Document Intelligence and Sweden Central for Infrastructure and Sweden Central for OpenAiLocation (Optimal due to OpenAI Availability)
<br>

* Alternative Region for availability should be West US 2 for Document Intelligence and West US 2 for Infrastructure and West US 3 for OpenAiLocation

<br>

## Deploy the Azure Resources

1. Open a terminal window and confirm prerequisites are complete
1. Clone the ```azure-search-openai-demo``` repo into your local environment by running the following command:

    ```bash
    git clone https://github.com/Azure-Samples/azure-search-openai-demo.git
    ```

1. Login to your Azure Account in the terminal window

    ```bash
    azd auth login
    ```

1. Go into the repo you cloned for azure-search-openai-demo.

   ```bash
    cd ./azure-search-openai-demo
    ```

1. Create a new azd environment

    ```bash
    azd env new
    ```

    Enter a name that will be used for the resource group.  This will create a new `.azure` folder and set it as the active environment for any calls to azd going forward.

1. Configure the environment variables to setup the AI Judge or LLM evaluation model in your project.

    ```bash
    azd env set USE_EVAL true
    ```

1.  Provision its capacity.

    ```bash
    azd env set AZURE_OPENAI_EVAL_DEPLOYMENT_CAPACITY 100 
    ```
1.  Setup Microsoft Foundry Project Endpoint in Environment file

    ```bash
    azd env set AZURE_AI_PROJECT_ENDPOINT abc
    ```

1. Run the bicep scripts with the following command:

    ```bash
    azd up
    ```

    This will provision Azure resources and deploy this sample to those resources, including building the search index based on the files found in the `./data` folder.  

1. Open URL for RAGCHAT application printed in the terminal console similar to the below picture. Ask it a few questions per cards to ensure it return results.<br>
<br>
<br>

![Alt text](/media/ragchatterminal.png "RAGCHAT Terminal")
<br>
<br>

## Deploy the Evaluation environment

1. Make a new Python virtual environment and activate it.  

    ```bash
    python -m venv .evalenv
    ```
1. Activate Python Virtual Environment 
    ```bash
    source .evalenv/bin/activate
    ```
1. Upload requirements file from Microhack repo to Azure-Search-OpenAI-Demo repo.  Microhack directory is ```/code/0_challenge/requirements.txt``` to ```/evals``` directory in RAGCHAT repo.  It is critical this file is in the evals directory and replace existing file.
    
    ```bash
    pip install -r evals/requirements.txt
    ```

## Upgrade your Azure OpenAI resources to Foundry

1. From Azure Portal, find and go to Azure OpenAI service created in CH0.

    ![Alt text](/media/aoirg.png "Azure OpenAI Resource Group")

1. From Azure OpenAI service, open in Foundry.
    
    ![Alt text](/media/aoiportal.png "Foundry portal")

1. From Foundry, migrate Azure OpenAI Service to Foundry.  Click on home icon.

    ![Alt text](/media/portalhome.png "AOI Home Screen")

1. Click Next on the migration wizard.

    ![Alt text](/media/aoiupgradesnapshot.png "Foundry portal")

1. Click confirm to create your new Foundry project

    ![Alt text](/media/Foundryproject.png "Project")

## Setup Project Connections

1. Setup Project Connections for these four resources; Foundry models, Azure AI Search, Azure Storage Account and App Insights.  All connections should use Entra ID except for AppInsights which uses an API Key.  


    ![Alt text](/media/Project_Connections.jpg "Project Connections")

1. Setup your Foundry Project to have access rights to the storage account thru the Foundry managed identitiy.  First go into storage account and open Access Control (IAM) tab.  Click on Add button and select Add role assignment

    ![Alt text](/media/storageIAM.jpg "Storage Assignment")

1. Type into Job Function Roles search bar ```Storage Blob Data Contributor``` and highlight role name in menu

    ![Alt text](/media/StorageBlobContributor.jpg "Contributor role")

1. Select Managed Identity for Assign access to and click on Select Members.  You will want to select all System Managed Identities from the drop down menu for your subscription.  Find the Foundry project you've created and select it.  Click on Review & Assign twice to assign the Foundry Project Managed Identity to the Storage account.

    ![Alt text](/media/StorageMI.jpg "Contributor role")

<br>
<br>

## Upload delta files for Microhack to Azure-Search-OpenAI-Demo Application repo

1. There are three python scripts for evaluations in the 0_challenge directory.  They are ```evaluatemh.py```, ```safety_evaluationmh.py``` and ```redteammh.py```.  Upload these files into the ```/evals``` directory in the Azure-Search-OpenAI-Demo repo.  These scripts will use the Azure Evaluation SDK and post the results into the Azure Foundry.  The scripts without the mh suffix are the original files and required for continuous evaluations.  We want to keep both files

1. There is one test file ```ground_truth_test.jsonl``` data set with two questions in the 0_challenge directory.  Upload this file into the ```/evals``` directory in the Azure-Search-OpenAI-Demo repo.  It is critical you upload this file since the python scripts are hard-coded with this file name and uploading it will shorten the runtime of the evaluations.

1. Open the environment files in the /.azure/<resource-group> directory and open the file.  Find the parameter called, ```AZURE_AI_PROJECT_ENDPOINT```.  Insert the Foundry project endpoint from the portal into this environment variable.

1. Replace the ```evaluate.yaml``` in the 0_challenge directory with the same file in the Azure-Search-OpenAI-Demo repo.  The file directory in the Azure-Search-OpenAI-Demo repo is ```./.github/workflow```

<br>
<br>


## Success Criteria
1. Click on prompt cards to see if it returns answers to these questions. 
1. Open Foundry Project to see model deployments.  Search for 'eval' as a model name
1. Review Project Connections for right permissions per above screenshot
1. Click on Monitor icon and click on the Resource Usage Tab.  For Model deployment, select ```text-embedding-3-large```.  You should see numbers for Total requests and Total Token count
<br>

## Run the workshop

After you complete all the success criteria, follow the steps in the [Challenge 1 -- Responsible AI](/code/1_challenge/README.md) to run the workshop. 
<br>


## Related Azure Technology
* Application Insights
* Azure OpenAI
* Container App & Registry
* Document Intelligence
* Microsoft Foundry
* Azure AI Search
* Azure Storage Account
<br>

## Resources
* Video series called, RAG Deep Dive https://aka.ms/ragdeepdive 
* Deployment Guidance https://aka.ms/ragchat#guidance   
* RAG Resources from Repo https://aka.ms/ragchat#resources
<br>
<br>
<br>
<br>

# CHALLENGE 0 COMPLETE!!!!!


<!-- These instructions assume there is no net new code for the actual challenges outside of the RAGCHAT application.  If there is no net code we can clone https://aka.ms/ragchat repo.  If there is net new code/scripts we will have to modify the environment setup instructions and copy necessary code to this repo. CH1 is manual data entry and challenge two reuses external repos with no new code set.  The one exception might be red teaming and observability.  We will refactor once each person's readme file is update to validate assumption.  -->
