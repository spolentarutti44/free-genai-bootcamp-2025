import boto3
from typing import Dict, Any, List
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat

from tools.generate_vocabulary_tool import generate_vocabulary_from_text
from config import AWS_REGION, BEDROCK_MODEL_ID, TARGET_LANGUAGE

class VocabularyAgent:
    def __init__(self):
        # Initialize AWS clients
        self.translate = boto3.client('translate', region_name=AWS_REGION)
        self.bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        
        # Initialize the LLM
        self.llm = BedrockChat(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            streaming=False
        )
        
        # Initialize tools
        self.tools = self._setup_tools()
        
        # Create the agent executor
        self.agent_executor = self._create_agent_executor()
    
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools for the vocabulary agent"""
        tools = [
            Tool(
                name="GenerateVocabulary",
                func=lambda text: generate_vocabulary_from_text(text, TARGET_LANGUAGE),
                description=f"Generates vocabulary for language learners of {TARGET_LANGUAGE} from text. Input should be the text to extract vocabulary from."
            )
        ]
        return tools
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with the React agent"""
        prompt = PromptTemplate.from_template(
            """You are a vocabulary generation assistant for language learners.
            
            You have access to the following tools:
            
            {tool_names}
            {tools}
            
            Use these tools to help generate vocabulary from text.
            
            {agent_scratchpad}
            
            Human: {input}
            AI Assistant: """
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def generate_vocabulary(self, lyrics: str) -> List[Dict[str, str]]:
        """
        Generate vocabulary items from lyrics
        
        Args:
            lyrics (str): The lyrics to extract vocabulary from
            
        Returns:
            list: A list of vocabulary items with definitions and examples
        """
        # For direct vocabulary generation, call the tool directly
        return generate_vocabulary_from_text(lyrics, TARGET_LANGUAGE)
    
    def customize_vocabulary(self, query: str, lyrics: str) -> Dict[str, Any]:
        """
        Generate customized vocabulary based on specific requirements
        
        Args:
            query (str): The customization requirements
            lyrics (str): The lyrics to extract vocabulary from
            
        Returns:
            dict: Customized vocabulary results
        """
        # For complex tasks requiring reasoning, use the agent
        result = self.agent_executor.invoke({
            "input": f"Generate vocabulary from these lyrics with the following requirements: {query}\n\nLyrics: {lyrics}",
            "agent_scratchpad": ""
        })
        return {"vocabulary": result["output"]} 