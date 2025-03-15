import boto3
from typing import Dict, Any, List
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat
from langchain.chains.conversation.memory import ConversationBufferMemory

from tools.extract_lyrics_tool import extract_lyrics
from tools.summarize_lyrics_tool import summarize_lyrics
from config import AWS_REGION, BEDROCK_MODEL_ID

class LyricAgent:
    def __init__(self):
        # Initialize AWS clients
        self.bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        
        # Initialize the LLM
        self.llm = BedrockChat(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            streaming=False
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._setup_tools()
        
        # Create the agent executor
        self.agent_executor = self._create_agent_executor()
    
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools for the lyric agent"""
        tools = [
            Tool(
                name="ExtractLyrics",
                func=extract_lyrics,
                description="Extracts lyrics for a given song title. Input should be the song title."
            ),
            Tool(
                name="SummarizeLyrics",
                func=summarize_lyrics,
                description="Summarizes the lyrics of a song. Input should be the complete lyrics text."
            )
        ]
        return tools
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with the React agent"""
        prompt = PromptTemplate.from_template(
            """You are a lyric extraction and analysis assistant.
            
            You have access to the following tools:
            
            {tool_names}
            {tools}
            
            Use these tools to help extract and analyze song lyrics.
            
            Chat History: {chat_history}
            
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
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def get_lyrics(self, song_title: str) -> str:
        """
        Retrieve lyrics for a given song title
        
        Args:
            song_title (str): The title of the song
            
        Returns:
            str: The lyrics of the song
        """
        # For simple tasks, call the tool directly
        return extract_lyrics(song_title)
    
    def summarize_lyrics(self, lyrics: str) -> str:
        """
        Summarize the lyrics of a song
        
        Args:
            lyrics (str): The lyrics to summarize
            
        Returns:
            str: A summary of the lyrics
        """
        # For simple tasks, call the tool directly
        return summarize_lyrics(lyrics)
    
    def analyze_lyrics(self, query: str) -> Dict[str, Any]:
        """
        Analyze lyrics based on a user query
        
        Args:
            query (str): The user's query about lyrics
            
        Returns:
            dict: Analysis results
        """
        # For complex tasks requiring reasoning, use the agent
        result = self.agent_executor.invoke({
            "input": query,
            "chat_history": self.memory.load(),
            "tool_names": [tool.name for tool in self.tools],
            "agent_scratchpad": ""
        })
        return {"analysis": result["output"]} 