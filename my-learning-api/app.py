from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from qdrant_client.http import models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import json
from datetime import datetime
from utils.qdrant_utils import get_qdrant_client
app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Get Qdrant client from utilities
client = get_qdrant_client()

# Initialize collections
def init_collections():
    try:
        # Collection for words
        client.recreate_collection(
            collection_name="words",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        # Create payload index for language filtering
        client.create_payload_index(
            collection_name="words",
            field_name="language",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        # Optional: Re-index other fields if needed or if recreate_collection clears them
        client.create_payload_index(
            collection_name="words",
            field_name="salish",
            field_schema=models.PayloadSchemaType.TEXT
        )
        client.create_payload_index(
            collection_name="words",
            field_name="english",
            field_schema=models.PayloadSchemaType.TEXT
        )
        print("Collection 'words' recreated/initialized with language index.")
    except Exception as e:
        # Check if it's a connection error or other issue
        print(f"Could not initialize collection 'words': {e}")
        # Depending on the error, you might want to raise it or handle differently
        # For now, let's assume if it fails, it might already exist in a usable state,
        # but log the error.
        pass

# Initialize collections on startup
init_collections()

# Error handling
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error="Internal server error"), 500

# Add OPTIONS method handler for CORS
@app.route('/words', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'status': 'ok'})
    return response

# Get paginated results from Qdrant
def get_paginated_results_qdrant(collection, page=1, per_page=10, sort_by=None, order=None, language=None):
    """
    Get paginated results from a Qdrant collection, optionally filtering by language.
    """
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Build filter based on language
    query_filter = None
    if language:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="language",
                    match=MatchValue(value=language)
                )
            ]
        )
        print(f"Applying filter for language: {language}") # Debug log

    try:
        # Get total count with filter
        count_result = client.count(
            collection_name=collection,
            count_filter=query_filter, # Use count_filter here
            exact=True # Use exact=True for potentially better accuracy with filters
        )
        total_count = count_result.count
        print(f"Total count for language '{language}': {total_count}") # Debug log

        # Get records with pagination and filter
        search_result, next_offset = client.scroll( # scroll now returns a tuple
            collection_name=collection,
            scroll_filter=query_filter, # Use scroll_filter here
            limit=per_page,
            offset=offset,
            with_payload=True,
            with_vectors=False # No need for vectors if just displaying words
        )

        # Extract payloads
        results = [point.payload for point in search_result] # Directly iterate search_result
        print(f"Retrieved {len(results)} items for page {page}, language '{language}'") # Debug log

        # Client-side sorting (if needed)
        if sort_by and results:
            reverse = order.lower() == 'desc' if order else False
            try:
                results = sorted(results, key=lambda x: x.get(sort_by, ''), reverse=reverse)
            except:
                # If sorting fails, return unsorted
                pass
        
        return {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'items': results
        }
    except Exception as e:
        print(f"Error fetching from Qdrant: {e}")
        return {
            'page': page,
            'per_page': per_page,
            'total': 0,
            'items': []
        }

@app.route('/words', methods=['POST'])
def insert_word():
    data = request.get_json()
    if not data:
        abort(400, description="No JSON data provided")

    salish = data.get('salish')
    english = data.get('english')
    language = data.get('language')

    if not salish or not english or not language:
        abort(400, description="salish, english, and language are required")

    if language not in ["salish", "italian"]:
        abort(400, description="language must be either 'salish' or 'italian'")

    try:
        point_id = str(datetime.now().timestamp()) + "-" + language

        client.upsert(
            collection_name="words",
            points=[
                models.PointStruct(
                    id=point_id,
                    payload={
                        "salish": salish,
                        "english": english,
                        "language": language,
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384
                )
            ]
        )
        print(f"Inserted word: {{'salish': '{salish}', 'english': '{english}', 'language': '{language}'}}")
        return jsonify({'status': 'success', 'id': point_id}), 201
    except Exception as e:
        print(f"Error inserting word: {e}")
        abort(500, description="Failed to insert word")

@app.route('/words', methods=['GET'])
def get_words():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    language = request.args.get('language', None, type=str)

    if language and language not in ["salish", "italian"]:
        print(f"Invalid language filter requested: {language}. Returning empty results.")
        return jsonify({
            'page': page,
            'per_page': per_page,
            'total': 0,
            'items': []
        })

    print(f"Fetching words: page={page}, per_page={per_page}, sort_by={sort_by}, order={order}, language={language}")

    try:
        result = get_paginated_results_qdrant(
            collection="words",
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order,
            language=language
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching words: {e}")
        return jsonify({"error": "Failed to fetch words"}), 500

@app.route('/ping', methods=['GET'])
def ping():
    response = jsonify({"message": "pong"})
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001) 