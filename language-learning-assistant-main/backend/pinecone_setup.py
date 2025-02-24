import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the Pinecone API key from the environment
api_key = os.getenv('PINECONE_API_KEY')

# Initialize Pinecone
pc = Pinecone(api_key=api_key)

# Create an index
index_name = 'language-learning'
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)  # Delete the existing index if it exists

pc.create_index(
    name=index_name,
    dimension=384,  # Update dimension to match the embedding model
    metric='cosine',  # Choose an appropriate metric
    spec=ServerlessSpec(cloud='aws', region='us-east-1')  # Adjust region as needed
)

# Access the index through the Pinecone client
index = pc.Index(index_name) 