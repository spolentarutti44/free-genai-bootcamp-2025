from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY # Import Qdrant config from config.py

def get_qdrant_client():
    """
    Returns a Qdrant client instance using configuration from config.py.
    """
    client = QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    return client

def init_qdrant():
    """
    Initializes Qdrant client and performs any necessary setup.
    (Currently this function is empty, but you can add setup steps here if needed)
    """
    pass # Placeholder for future Qdrant initialization steps 