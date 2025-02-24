from pinecone_setup import index
from sentence_transformers import SentenceTransformer
from typing import List
import random
from database import add_chat_entry

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

class SimpleRetrievalTool:
    def __init__(self):
        pass

    def retrieve(self, query: str) -> str:
        query_vector = model.encode(query).tolist()
        results = index.query(
            vector=query_vector,
            top_k=1,
            include_metadata=True
        )
        if results['matches']:
            return results['matches'][0]['metadata']['content']
        return "No relevant information found."

    def add_to_knowledge_base(self, role: str, content: str):
        add_chat_entry(role, content)


class RAGAgent:
    def __init__(self, retrieval_tool: SimpleRetrievalTool, model):
        self.retrieval_tool = retrieval_tool
        self.model = model

    def generate_response(self, query: str) -> str:
        # Step 1: Retrieve relevant information
        retrieved_info = self.retrieval_tool.retrieve(query)
        
        # Step 2: Generate a response using the retrieved information
        response = self.model.generate_response(f"{query} {retrieved_info}")
        print(response)
        return response
