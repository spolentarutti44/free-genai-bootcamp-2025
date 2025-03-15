from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseLanguageModel

def create_agent_executor(
    llm: BaseLanguageModel, 
    tools: List[Tool], 
    system_message: str, 
    memory=None,
    verbose: bool = True
) -> AgentExecutor:
    """
    Create an agent executor with the React agent that handles the expected variables
    
    Args:
        llm: The language model to use
        tools: The tools available to the agent
        system_message: The system message to include in the prompt
        memory: Optional memory to use for the agent
        verbose: Whether to print agent steps
        
    Returns:
        An AgentExecutor instance
    """
    prompt = PromptTemplate.from_template(
        f"""{system_message}
        
        You have access to the following tools:
        
        {{tools}}
        
        {{agent_scratchpad}}
        
        Human: {{input}}
        AI Assistant: """
    )
    
    # Create the agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create and return the agent executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True
    ) 