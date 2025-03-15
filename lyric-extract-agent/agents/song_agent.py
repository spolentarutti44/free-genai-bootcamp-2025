import boto3
from typing import Dict, Any, List
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import BedrockChat

from tools.duckduckgo_tool import search_duckduckgo
from tools.youtube_tool import search_youtube
from config import AWS_REGION, BEDROCK_MODEL_ID

class SongAgent:
    def __init__(self):
        # Initialize AWS clients
        self.comprehend = boto3.client('comprehend', region_name=AWS_REGION)
        
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
        """Set up the tools for the song agent"""
        tools = [
            Tool(
                name="SearchWeb",
                func=lambda query: search_duckduckgo(f"{query} song lyrics"),
                description="Searches the web for song information. Input should be the search query."
            ),
            Tool(
                name="SearchYouTube",
                func=lambda query: search_youtube(f"{query} song"),
                description="Searches YouTube for songs. Input should be the search query."
            )
        ]
        return tools
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with the React agent"""
        prompt = PromptTemplate.from_template(
            """You are a song search assistant.
            
            You have access to the following tools:
            
            
            {tool_names}
            {tools}
            
            Use these tools to help find songs based on user queries.
            
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
    
    def search_songs(self, query: str) -> List[Dict[str, str]]:
        """
        Search for songs based on a query
        
        Args:
            query (str): The search query
            
        Returns:
            list: A list of songs matching the query
        """
        # For simple searches, use the direct approach
        web_results = search_duckduckgo(f"{query} song lyrics")
        youtube_results = search_youtube(f"{query} song")
        
        # Combine and process results
        results = []
        
        # Process web results
        for result in web_results[:5]:  # Limit to top 5 results
            results.append({
                "title": self._extract_song_title(result["title"]),
                "artist": self._extract_artist(result["title"]),
                "source": "web",
                "url": result["link"]
            })
        
        # Process YouTube results
        for result in youtube_results[:5]:  # Limit to top 5 results
            results.append({
                "title": self._extract_song_title(result["title"]),
                "artist": self._extract_artist(result["title"]),
                "source": "youtube",
                "url": result["link"]
            })
        
        return results
    
    def advanced_song_search(self, query: str) -> Dict[str, Any]:
        """
        Perform an advanced search for songs using the agent
        
        Args:
            query (str): The advanced search query
            
        Returns:
            dict: Search results with analysis
        """
        # For complex searches requiring reasoning, use the agent
        result = self.agent_executor.invoke({
            "input": query,
            "agent_scratchpad": ""
        })
        return {"search_results": result["output"]}
    
    def _extract_song_title(self, text: str) -> str:
        """Extract song title from text using simple heuristics"""
        # This is a placeholder for more advanced extraction logic
        if " - " in text:
            return text.split(" - ")[1].strip()
        return text.strip()
    
    def _extract_artist(self, text: str) -> str:
        """Extract artist name from text using simple heuristics"""
        # This is a placeholder for more advanced extraction logic
        if " - " in text:
            return text.split(" - ")[0].strip()
        return "Unknown Artist" 