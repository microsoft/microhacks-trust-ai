# Challenge 0: Environment Setup

If you’re running this workshop on your own, you'll need to deploy the workshop resources to your Azure subscription. Follow the instructions to deploy the workshop resources.

## Overview

We will set up the initial environment for you to build on top of during your Microhack. This comprehensive setup includes configuring essential Azure services and ensuring access to all necessary resources. Participants will familiarize themselves with the architecture, gaining insights into how various components interact to create a cohesive solution. With the foundational environment in place, the focus will shift seamlessly to the first Microhack Challenge endeavor.  
<br>
<br>
![Alt text](/media/architecture_ragchat.png "RAGCHAT Architecture")
<br>
<br>

## Prerequisites for Local Environments (Linux, Windows or Mac)

- A computer running Windows 11, macOS, or Linux.
- An Azure subscription. If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/free/).
- Install the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- Install [Powershell 7 (supported on Windows, macOS, and Linux)](https://learn.microsoft.com/powershell/scripting/install/installing-powershell).
- Install [Python 3.13](https://www.python.org/downloads/).
- Install the Git CLI. You can download it from the [Git website](https://git-scm.com/downloads).
- Install VS Code on your local PC if not using Codespaces.
<br>

## Support Software

* Azure Developer CLI: Download azd
* Ensure the correct OS is selected
* Powershell 7+ with AZ module (Windows only): Powershell, AZ Module
* Git: Download Git
* Python 3.13: Download Python
<br>

## Prerequisites for CodeSpaces

- An Azure subscription. If you don't have an Azure subscription, create a [free account](https://azure.microsoft.com/free/).
- Validate [Python 3.13](https://www.python.org/downloads/) is setup in your environment or lower
<br>

## Recommended Regions

* Sweden Central (swedencentral)
* France Central (francecentral)

- **Optimal Region** for availability should be Sweden Central (Optimal due to Azure OpenAI availability)
- **Alternative Region** for availability should be France Central for Azure OpenAI availability.
<br>

You can run this Microhack either on your local computer or in GitHub Codespaces. It is recommended that you use GitHub Codespaces. 

## Setup your Development Environment on Codespaces (recommended)

You first need to fork this repo into your GitHub account. Use the below button to do that.

[![Fork this repo](https://img.shields.io/badge/Fork%20this%20repo-blue?logo=github)](https://github.com/microsoft/microhacks-trust-ai/fork)

Create a Codespace from your fork:

- Your fork should have opened automatically after you clicked the above button, but if it didn't, go to your fork (e.g., `https://github.com/<your-username>/microhacks-trust-ai`).
- Click the green **<> Code** button, then select the **Codespaces** tab.
- Click **Create codespace on main** (use the default configuration).


At the terminal window confirm the home directory ```/microhacks-trust-ai```

- Activate Python Virtual Environment (Linux)

    ```bash
    source .evalenv/bin/activate
    ```
<br>

## Setup your Development Environment on your local workstation

***Note*** You can skip this section if you are using GitHub Codespaces
<details markdown=1>
<summary markdown="span"><strong>Click to expand/collapse Local Workstation instructions</strong></summary>

- Start the Microhack on a local environment.

    a. Open a terminal window for local deployments and confirm prerequisites are complete
        
    * <u>**Fork**</u> the [Microhack Trustworthy AI](https://github.com/microsoft/microhacks-trust-ai) repo into your GitHub account.  This is a requirement to fork the repo into your account for CH3 due to GitHub Actions.
        
    * Clone the <u>**FORKED REPO**</u> in your GitHub account to your local environment by running the following command:

        * ```git clone https://github.com/<GitHub username>/microhacks-trust-ai```

    * At the terminal window confirm the home directory ```/microhacks-trust-ai```

- Make a new Python virtual environment and activate it.  

    ```bash
    python -m venv .evalenv
    ```
- Activate the Python Virtual Environment

    **Mac OS X or Linux** 
    ```
    source .evalenv/bin/activate
    ```

    **Powershell** 
    ```
    .evalenv\Scripts\Activate.ps1
    ```

- Install UV to expediate the pip installation

    ```bash
    pip install uv
    ```

- PIP install the requirements into your virtual environment
    
    ```bash
    uv pip install -r ./scripts/requirements.txt
    ```

- Prep for postprovision hook
    
    **Mac OS X or Linux**

    Change permissions of shell script to deploy Container image
    ```bash
    chmod +x ./scripts/02_deploy_container_apps.sh
    ```
    **Windows**

    Use pwsh version for postprovision
    ```
    Rename-Item -Path "azure.yaml" -NewName "azure_bash.yaml"; Rename-Item -Path "azure_pwsh.yaml" -NewName "azure.yaml"
    ```

</details>
<br>

## Deploy the Azure Resources

A pre-requisite before running AZD UP is to activate your Python Virtual environment to ```.evalenv```.  This is step 3 in the local workstation section.

***Important: Click to expand one of the following sections depending on whether you have a Microsoft FDPO Internal or External (or non-Microsoft provided) Azure subscription***
<details markdown=1>
<summary markdown="span"><strong>Click to expand Microsoft FDPO Internal instructions</strong></summary>
- You will need your Azure tenant ID for your Microsoft FDPO Internal subscription. One way to get that is by going to the Azure portal, click your username in the upper right corner, and select Switch Directory. Your Tenant ID should be the Directory ID for the fdpo.onmicrosoft.com domain. 

- Visual Studio Code for the Web does not support logging into your FDPO internal Azure subscription. Once you open your Codespace, you will need to click the blue Codespaces text in the lower right corner of VS Code for the Web and select Open in VS Code Desktop. This will open the same GitHub Codespace but in your VS Code Desktop. 

- Login to your Azure Developer Account in the terminal window. This will open a browser window where you should login using your @microsoft.com credentials. 

    ```bash
    azd auth login --tenant-id <YOUR_TENANT_ID>
    ```

- Before you run login to the Azure CLI, this workaround is required. Enter this in the terminal window (**note**: this seems unintuitive but is required because device code authentication is not supported with FDPO internal)

    ```bash
    CODESPACES=false
    ```

- Login to your Azure Account in the terminal window

    ```bash
    az login --tenant <YOUR_TENANT_ID>
    ```

</details>

<details markdown=1>
<summary markdown="span"><strong>Click to expand Microsoft FDPO External or non-Microsoft employee provided Azure instructions</strong></summary>

- Login to your Azure Developer Account in the terminal window

    ```bash
    azd auth login
    ```

- Login to your Azure Account in the terminal window

    ```bash
    az login
    ```

</details>


<br>
Once you have logged into the Azure Developer CLI and Azure CLI using one of the methods above, create a new azd environment

- Create a new azd environment

    ```bash
    azd env new
    ```

    Enter a name that will be used for the resource group.  This will create a new `.azure` folder and set it as the active environment for any calls to azd going forward.

- Run the bicep scripts with the following command:

    ```bash
    azd up
    ```

    This will provision Azure resources and deploy this sample to those resources, including building the search index based on the files found in the `./data` folder.  

- Open URL for RAGCHAT application printed in the terminal console similar to the below picture. <br>

![Alt text](/media/ragchatterminal.png "RAGCHAT Terminal")

<br>

## Success Criteria

- Type this question into the prompt window, "What is the out-of-pocket maximum for the Northwind Standard plan?".  The returned answer should mention $6,000 per person per year.

- Open Foundry Project to see model deployments.  Search for 'gpt-5.4-mini' as a model name

- Click on Models icon and navigate to the ```text-embedding-3-large```  Model deployment. Then click on the Monitor tab. You should see numbers for Total requests and Total Token count
<br>

## Continue to Challenge 1

After you complete all the success criteria, follow the steps in the [Challenge 1 -- Responsible AI](/code/1_challenge/README.md) to run the workshop. 
<br>

## Related Azure Technology
* Application Insights
* Microsoft Foundry
* Container App & Registry
* Azure AI Search
* Azure Storage Account
<br>

## Resources
* Video series called, RAG Deep Dive https://aka.ms/ragdeepdive 
* Alternative RAGCHAT repo https://aka.ms/ragchat#guidance   
* RAG Resources from RAGCHAT Repo https://aka.ms/ragchat#resources

<br>
<br>

# CHALLENGE 0 COMPLETE!!!!! YAY!!

<br>
<br>

# Contributors to this Microhack

We are grateful to the hard-work and thought leadership done by Pamela Fox and Matt Gotteiner. We were inspired and informed by their work.  We have sampled from their https://aka.ms/ragchat repo and studied their podcast series RAG Deep dive http://aka.ms/ragdeepdive.  We highly recommend to watch this content when preparing your applications to move into production.


<!-- We have built our own code set for easier maintenance and to highlight Trustworthy AI principles than RAG based applications.  All data and code lives in this repo for the Microhack and don't need external data from other repos.  We share learning resources from RAGCHAT application since it does a great job of highlighting evaluation principles and code samples.  The repo leverages as of Jan 2026 Microsoft Foundry Classic since it is in GA.  When Foundry New Portal is moved into GA we will refactor the repo.  -->
