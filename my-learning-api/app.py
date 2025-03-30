from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from qdrant_client.http import models
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
        client.create_collection(
            collection_name="words",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
    except Exception:
        pass  # Collection already exists

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
def get_paginated_results_qdrant(collection, page=1, per_page=10, sort_by=None, order=None):
    """
    Get paginated results from a Qdrant collection.
    """
    # Calculate offset
    offset = (page - 1) * per_page
    
    try:
        # Get total count
        count_result = client.count(collection_name=collection)
        total_count = count_result.count
        
        # Get records with pagination
        search_result = client.scroll(
            collection_name=collection,
            limit=per_page,
            offset=offset,
            with_payload=True
        )
        
        # Extract payloads
        results = []
        for point in search_result[0]:
            results.append(point.payload)
        
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

    if not salish or not english:
        abort(400, description="salish and english are required")

    try:
        # Insert into Qdrant
        client.upsert(
            collection_name="words",
            points=[
                models.PointStruct(
                    id=str(datetime.now().timestamp()),  # Use timestamp as ID
                    payload={
                        "salish": salish,
                        "english": english,
                        "created_at": datetime.now().isoformat()
                    },
                    vector=[0.0] * 384  # Placeholder vector
                )
            ]
        )
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        print(f"Error inserting word: {e}")
        abort(500, description="Failed to insert word")

@app.route('/words', methods=['GET'])
def get_words():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    try:
        result = get_paginated_results_qdrant(
            collection="words",
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order
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