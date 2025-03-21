import os
from flask import Flask, g
from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY  # Import Qdrant config

# Collection name for Qdrant
COLLECTION_NAME = "learning_portal_data"

def get_db():
    """
    Returns a Qdrant client instance, storing it in Flask's g object for reuse within the same request.
    """
    client = getattr(g, '_qdrant_client', None)
    if client is None:
        try:
            print(f"Connecting to Qdrant at {QDRANT_URL}")
            client = g._qdrant_client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
            print("Qdrant connection successful")
        except Exception as e:
            print(f"ERROR connecting to Qdrant: {str(e)}")
            # Return a dummy client or raise the error
            raise e
    return client

def close_db(e=None):
    """
    No need to explicitly close Qdrant client, but keeping the function for consistent API.
    """
    pass  # Qdrant client doesn't require explicit closing

def init_db():
    """
    Initializes the Qdrant collection for the learning portal.
    """
    print("Initializing Qdrant database...")
    client = get_db()

    try:
        # Check if collection exists
        existing_collections = client.get_collections().collections
        collection_exists = any(col.name == COLLECTION_NAME for col in existing_collections)
        
        if collection_exists:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
        else:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            # Define schema suitable for word data
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    "size": 768,  # Example dimension for text embeddings
                    "distance": "Cosine"
                }
            )
            
            # Create a payload index for efficient searching
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="english",
                field_schema="keyword"
            )
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="kanji",
                field_schema="keyword"
            )
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="romaji",
                field_schema="keyword"
            )
            
            # Populate with initial data (optional)
            populate_initial_data(client)
            
            print(f"Collection '{COLLECTION_NAME}' created successfully.")
    except Exception as e:
        print(f"Error during Qdrant initialization: {str(e)}")
    
    print("Qdrant database initialization complete.")

def populate_initial_data(client):
    """
    Populates the Qdrant collection with initial vocabulary data.
    """
    # Example data - these would be stored as payloads in Qdrant
    sample_words = [
        {
            "id": 1,
            "kanji": "山",
            "romaji": "yama",
            "english": "mountain",
            "parts": None
        },
        {
            "id": 2,
            "kanji": "川",
            "romaji": "kawa",
            "english": "river",
            "parts": None
        },
        {
            "id": 3,
            "kanji": "森",
            "romaji": "mori",
            "english": "forest",
            "parts": None
        },
        {
            "id": 4,
            "kanji": "空",
            "romaji": "sora",
            "english": "sky",
            "parts": None
        },
        {
            "id": 5,
            "kanji": "海",
            "romaji": "umi",
            "english": "sea",
            "parts": None
        }
    ]
    
    # Since Qdrant requires vectors, we'll generate dummy vectors for this example
    # In a real application, you would use an embedding model to generate meaningful vectors
    import numpy as np
    
    # Insert words as points in the collection
    points = []
    for word in sample_words:
        # Generate a random vector (in practice, this would be a semantic embedding)
        vector = np.random.rand(768).tolist()
        
        points.append({
            "id": word["id"],
            "vector": vector,
            "payload": word
        })
    
    # Batch insert the points
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print(f"Inserted {len(points)} initial vocabulary words.")

def init_app(app):
    """
    Initialize the Flask app with Qdrant database connection.
    """
    app.teardown_appcontext(close_db)

if __name__ == '__main__':
    # Create a Flask app instance for the context
    app = Flask(__name__)
    with app.app_context():
        # This will only run when this file is executed directly
        init_db()
        print("Qdrant database initialized (when run directly)") 