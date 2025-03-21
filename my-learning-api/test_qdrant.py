from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY

print(f"Attempting to connect to Qdrant at: {QDRANT_URL}")
print(f"Using API key: {QDRANT_API_KEY[:5]}...{QDRANT_API_KEY[-5:] if QDRANT_API_KEY else None}")

try:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    collections = client.get_collections()
    print(f"Connection successful! Found collections: {collections}")
except Exception as e:
    print(f"ERROR: {str(e)}")
    
print("Test complete.") 