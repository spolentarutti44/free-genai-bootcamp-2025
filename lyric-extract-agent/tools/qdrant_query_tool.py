from utils.qdrant_utils import get_qdrant_client

def query_history(query=None, limit=20):
    """
    Query the history collection in Qdrant
    
    Args:
        query (str, optional): Query text. Defaults to None.
        limit (int, optional): Number of results to return. Defaults to 20.
        
    Returns:
        list: A list of history entries
    """
    client = get_qdrant_client()
    collection_name = "conversation_history"
    
    try:
        if query:
            # Vectorize the query if needed and perform vector search
            # (Vectorization step would be needed here if you want to search by content similarity)
            results = client.search(
                collection_name=collection_name,
                query_vector=[0.0] * 1536,  # Placeholder vector - replace with actual query vector
                query_filter=None,  # Add filters if needed
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
        else:
            # Retrieve the latest history entries
            results = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

        # Access payload using attribute access: point.payload
        return [point.payload for point in results[0]]

    except Exception as e:
        print(f"Error querying history from Qdrant: {e}")
        return [] 