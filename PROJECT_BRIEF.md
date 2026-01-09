# PROJECT BRIEF

This project combines the best of all my previous projects - llmCouncil, agentsParliament and superAI + seedgpt into 1 project that allows the user to interact with 1 god agent which controls all the other agents and propegates their actions.

It uses principals and architecture from llmCouncil and possibly agentsParliament and extends it with the capabilities of superAI and seedgpt.

The project tries to be as full-mesh as possible, with all agents interacting with each other. so for start we will provision the folder structure such that all agnets can do so, and each agent will be able to call the others and use their capabilities. It uses LLM council to choose the starting agent that will be used to be the god agent.


so once we choose the agent (and user possibaly approved, or has it configured to auto mode) - the direct agent should be used, not any other sub-project... e.g if claude is choosen then we will call claude with the exact syste and user prompts that we were called with, and the llmcouncil/agentsparliament/superai/seedgot projectgs are just a REFERENCE of how to do it and we want to take it and use thier code (copy paoased if needed) in our app. 
the godagent itself is completely independed of the other projects and only uses thier ideas and code

# SEEDGPT
See .seedgpt folder for high level management and planning of the project.

