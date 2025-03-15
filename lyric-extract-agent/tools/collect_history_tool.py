from utils.qdrant_utils import get_qdrant_client

def save_to_history(interaction_data):
    """
    Save an interaction to the history collection in Qdrant
    
    Args:
        interaction_data (dict): The interaction data to save
    """
    client = get_qdrant_client()
    
    # Convert the interaction data to a format suitable for Qdrant
    point_id = interaction_data["id"]
    vector = [0.1] * 1536  # Placeholder vector; in a real implementation, you would generate this
    payload = interaction_data
    
    # Insert the point into the collection
    client.upsert(
        collection_name="conversation_history",
        points=[
            {
                "id": point_id,
                "vector": vector,
                "payload": payload
            }
        ]
    ) 