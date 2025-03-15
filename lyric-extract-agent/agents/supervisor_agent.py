from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_community.chat_models import BedrockChat
from typing import List, Dict, Any

from agents.lyric_agent import LyricAgent
from agents.song_agent import SongAgent
from agents.vocabulary_agent import VocabularyAgent
from agents.history_agent import HistoryAgent
from config import AWS_REGION, BEDROCK_MODEL_ID

class SupervisorAgent:
    def __init__(self):
        # Initialize specialized agents
        self.lyric_agent = LyricAgent()
        self.song_agent = SongAgent()
        self.vocabulary_agent = VocabularyAgent()
        self.history_agent = HistoryAgent()
        
        # Initialize the LLM
        self.llm = BedrockChat(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            streaming=False
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._setup_tools()
        
        # Create the agent executor
        self.agent_executor = self._create_agent_executor()
    
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools for the supervisor agent"""
        tools = [
            Tool(
                name="GetLyrics",
                func=self.lyric_agent.get_lyrics,
                description="Retrieve lyrics for a given song title. Input should be the song title."
            ),
            Tool(
                name="SummarizeLyrics",
                func=self.lyric_agent.summarize_lyrics,
                description="Summarizes the lyrics of a song. Input should be the complete lyrics text."
            ),
            Tool(
                name="GenerateVocabulary",
                func=self.vocabulary_agent.generate_vocabulary,
                description=f"Generates vocabulary for language learners of Salish from text. Input should be the text to extract vocabulary from."
            ),
            Tool(
                name="SearchSongs",
                func=self.song_agent.search_songs,
                description="Searches for songs based on a query. Input should be the search query."
            )
        ]
        return tools
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with the React agent"""
        prompt = PromptTemplate.from_template(
            """You are a comprehensive lyric assistant.
            
            You have access to the following tools:
            
            {tool_names}
            {tools}
            
            Use these tools to help users with their requests about lyrics, songs, and vocabulary.
            
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
    
    def process_request(self, query: str) -> Dict[str, Any]:
        """
        Process a user request through the supervisor agent
        
        Args:
            query (str): The user query
            
        Returns:
            dict: The agent's response
        """
        try:
            result = self.agent_executor.invoke({
                "input": query,
                "chat_history": self.memory.load(),
                "agent_scratchpad": ""
            })
            
            # Log the interaction
            self.history_agent.log_interaction(
                action="process_request",
                input_data=query,
                output_data=result["output"]
            )
            
            return {"response": result["output"], "success": True}
        except Exception as e:
            error_message = f"Error processing request: {str(e)}"
            return {"response": error_message, "success": False} 