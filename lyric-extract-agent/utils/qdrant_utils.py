from qdrant_client import QdrantClient
from qdrant_client.http import models
from config import QDRANT_URL, QDRANT_API_KEY

def get_qdrant_client():
    """
    Get a Qdrant client
    
    Returns:
        QdrantClient: A configured Qdrant client
    """
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def init_qdrant():
    """
    Initialize the Qdrant collections
    """
    client = get_qdrant_client()
    
    # Check if the conversation history collection exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if "conversation_history" not in collection_names:
        # Create the conversation history collection
        client.create_collection(
            collection_name="conversation_history",
            vectors_config=models.VectorParams(
                size=1536,  # Dimensions for the vector
                distance=models.Distance.COSINE
            )
        )
        print("Created 'conversation_history' collection") 