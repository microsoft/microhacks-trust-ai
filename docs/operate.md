#Operate Phase for Generative AI Applications

## Overview
Once your generative AI application is deployed, the Operate phase ensures ongoing reliability, safety, and compliance. This phase focuses on observability, alerts, and governance controls so you can detect issues early and maintain Trustworthy AI standards throughout the lifecycle.

## Step by Step Guide
1. Enable Continuous Monitoring
Set up real-time observability for your application using Azure AI Foundry and Azure Monitor. Monitor key metrics such as latency, token usage, and evaluation scores (e.g., relevance, fluency, safety) at a sampled rate.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/monitor

2. Configure Evaluation Sampling
Run continuous evaluations on live traffic or sampled queries to detect drift and regressions. For example, configure Foundry to evaluate 10 queries per hour for relevance and safety checks.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/cloud-evaluation

3. Use Tracing for Root-Cause Analysis
Enable tracing to capture detailed execution flows, including prompts, responses, and tool calls. This helps diagnose why a response failed and supports governance reviews.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/monitor#tracing

4. Set Up Alerts and Automated Actions
Integrate with Azure Monitor Alerts to notify teams when evaluation scores dip below thresholds or when anomalies occur. Configure automated actions (e.g., pause unsafe features) to maintain compliance.
Learn more: https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview

5. Maintain Governance and Compliance
Use Foundry’s governance integrations to log evaluations, trace decisions, and enforce Responsible AI policies. Align with Microsoft’s Discover, Protect, Govern framework for ongoing risk management.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-use-of-ai-overview

6. Iterate and Optimize
Review monitoring dashboards and evaluation trends regularly. Identify patterns (e.g., relevance dips or latency spikes) and feed insights back into your development cycle for continuous improvement.
Learn more: https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/concept-playgrounds