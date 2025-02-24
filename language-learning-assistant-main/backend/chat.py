# Create BedrockChat
# bedrock_chat.py
import boto3
import streamlit as st
from typing import Optional, Dict, Any
from rag import RAGAgent, SimpleRetrievalTool
from database import initialize_db


# Model ID
MODEL_ID = "amazon.nova-micro-v1:0"



class BedrockChat:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Bedrock chat client"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id = model_id

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Amazon Bedrock"""
        if inference_config is None:
            inference_config = {"temperature": 0.7}

        messages = [{
            "role": "user",
            "content": [{"text": message}]
        }]

        try:
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig=inference_config
            )
            return response['output']['message']['content'][0]['text']
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None


if __name__ == "__main__":
    # Initialize the database
    initialize_db()

    # Path to your SQLite3 database
    db_path = './database.db'

    # Initialize the retrieval tool and RAG agent
    retrieval_tool = SimpleRetrievalTool(db_path)
    rag_agent = RAGAgent(retrieval_tool, BedrockChat())

    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = rag_agent.generate_response(user_input)
        print("Bot:", response)

        # Add user input and bot response to the knowledge base
        retrieval_tool.add_to_knowledge_base("User", user_input)
        retrieval_tool.add_to_knowledge_base("Bot", response)
