from flask import Flask, request, jsonify, abort
import sqlite3
import json
from database import init_db, get_db, init_app
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            # Add any other origins you need
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Add OPTIONS method handler to ensure preflight requests work
@app.route('/words', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'status': 'ok'})
    return response

# Configure the database path
app.config['DATABASE'] = 'learning_portal.db'

init_app(app)

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

# Pagination function
def get_paginated_results(query, page, per_page, sort_by, order):
    db = get_db()
    cursor = db.cursor()

    # Calculate offset
    offset = (page - 1) * per_page

    # Validate sort_by and order
    valid_sort_fields = ['id', 'kanji', 'romaji', 'english', 'correct_count', 'wrong_count', 'name', 'words_count', 'created_at']  # Extend with all valid fields
    if sort_by not in valid_sort_fields:
        raise ValueError(f"Invalid sort_by field: {sort_by}")
    if order not in ['asc', 'desc']:
        raise ValueError("Order must be 'asc' or 'desc'")

    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM ({query})")
    total_count = cursor.fetchone()[0]

    # Apply sorting, limit, and offset
    sql_query = f"{query} ORDER BY {sort_by} {order} LIMIT {per_page} OFFSET {offset}"
    cursor.execute(sql_query)
    results = [dict(row) for row in cursor.fetchall()]

    return {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'items': results
    }

# Add this function to handle Qdrant queries (replace the existing get_paginated_results)
def get_paginated_results_qdrant(collection, page=1, per_page=10, sort_by=None, order=None):
    """
    Get paginated results from a Qdrant collection.
    """
    db = get_db()
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    # In Qdrant, we can use count() method
    count_result = db.count(collection_name=collection)
    total_count = count_result.count
    
    # Setup ordering
    # Qdrant has different ordering mechanisms than SQL
    # For this example, we'll implement a simple client-side sorting
    
    # Get records with pagination
    search_result = db.scroll(
        collection_name=collection,
        limit=per_page,
        offset=offset,
        with_payload=True
    )
    
    # Extract payloads
    results = []
    for scored_point in search_result.points:
        item = scored_point.payload
        results.append(item)
    
    # Client-side sorting (if needed)
    if sort_by and results:
        reverse = order.lower() == 'desc' if order else False
        try:
            results = sorted(results, key=lambda x: x.get(sort_by, ''), reverse=reverse)
        except:
            # If sorting fails (e.g., mixed types), we'll just return unsorted
            pass
    
    return {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'items': results
    }

# New route for inserting words
@app.route('/words', methods=['POST'])
def insert_word():
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        abort(400, description="No JSON data provided")

    kanji = data.get('kanji')
    romaji = data.get('romaji')
    english = data.get('english')
    parts = data.get('parts', None)  # parts is optional

    if not kanji or not romaji or not english:
        abort(400, description="kanji, romaji, and english are required")

    try:
        # Optionally parse parts as JSON
        if parts:
            json.dumps(parts) #Check if parts is valid json
    except json.JSONDecodeError:
        abort(400, description="parts must be a valid JSON string")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO words (kanji, romaji, english, parts) VALUES (?, ?, ?, ?)", (kanji, romaji, english, parts))
        db.commit()
        word_id = cursor.lastrowid
        return jsonify({'id': word_id}), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        abort(400, description="Integrity error during insert")

# Routes
@app.route('/words', methods=['GET'])
def get_words():
    # Mock data for testing
    sample_words = [
        {"id": 1, "kanji": "山", "romaji": "yama", "english": "mountain"},
        {"id": 2, "kanji": "川", "romaji": "kawa", "english": "river"},
        {"id": 3, "kanji": "森", "romaji": "mori", "english": "forest"},
        {"id": 4, "kanji": "空", "romaji": "sora", "english": "sky"},
        {"id": 5, "kanji": "海", "romaji": "umi", "english": "sea"}
    ]
    
    response = jsonify({
        "page": 1,
        "per_page": 10,
        "total": len(sample_words),
        "items": sample_words
    })
    
    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    return response

@app.route('/groups', methods=['GET'])
def get_groups():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'name', type=str)
    order = request.args.get('order', 'asc', type=str)
    per_page = 10  # You can make this configurable

    query = "SELECT * FROM groups"
    try:
        return jsonify(get_paginated_results(query, page, per_page, sort_by, order))
    except ValueError as e:
        abort(400, description=str(e))

@app.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'name', type=str)
    order = request.args.get('order', 'asc', type=str)
    per_page = 10

    query = f"SELECT w.*, g.name FROM words w JOIN word_groups wg ON w.id = wg.word_id JOIN groups g ON wg.group_id = g.id WHERE wg.group_id = {group_id}"
    try:
        return jsonify(get_paginated_results(query, page, per_page, sort_by, order))
    except ValueError as e:
        abort(400, description=str(e))

@app.route('/study_sessions', methods=['POST'])
def create_study_session():
    group_id = request.form.get('group_id', type=int)
    study_activity_id = request.form.get('study_activity_id', type=int)

    if not group_id or not study_activity_id:
        abort(400, description="group_id and study_activity_id are required")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO study_sessions (group_id, study_activity_id) VALUES (?, ?)", (group_id, study_activity_id))
        db.commit()
        study_session_id = cursor.lastrowid
        return jsonify({'id': study_session_id}), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        abort(400, description="Foreign key constraint failed")

@app.route('/study_sessions/<int:session_id>/review', methods=['POST'])
def log_review(session_id):
    word_id = request.form.get('word_id', type=int)
    correct = request.form.get('correct', type=bool)

    if not word_id or correct is None:
        abort(400, description="word_id and correct are required")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO word_review_items (word_id, study_session_id, correct) VALUES (?, ?, ?)", (word_id, session_id, correct))
        db.commit()
        review_item_id = cursor.lastrowid
        return jsonify({'id': review_item_id}), 201
    except sqlite3.IntegrityError as e:
        db.rollback()
        abort(400, description="Foreign key constraint failed")

@app.route('/ping', methods=['GET'])
def ping():
    response = jsonify({"message": "pong"})
    # Add CORS headers explicitly
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001) 