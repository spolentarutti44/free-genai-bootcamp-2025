import pytest
from app import app, get_db
import json
import sqlite3
from database import init_db
import os

# DATABASE = 'learning_portal.db'  # Remove the hardcoded DATABASE

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Configure the database path for testing
    app.config['DATABASE'] = 'test_learning_portal.db'  # Use a different database for testing

    with app.test_client() as client:
        with app.app_context():
            # Initialize the database for testing
            if os.path.exists(app.config['DATABASE']):
                os.remove(app.config['DATABASE'])
            try:
                init_db()
                # Populate with some test data
                db = get_db()
                cursor = db.cursor()

                # Check if the 'words' table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='words';")
                result = cursor.fetchone()
                if result:
                    print("The 'words' table exists.")
                else:
                    print("The 'words' table does NOT exist.")

                cursor.execute("INSERT INTO groups (name, words_count) VALUES ('N5', 10)")
                cursor.execute("INSERT INTO study_activities (name, url) VALUES ('Anki', 'http://example.com')")
                cursor.execute("INSERT INTO words (kanji, romaji, english) VALUES ('猫', 'neko', 'cat')")
                cursor.execute("INSERT INTO words (kanji, romaji, english) VALUES ('犬', 'inu', 'dog')")
                cursor.execute("INSERT INTO word_groups (word_id, group_id) VALUES (1, 1)")
                cursor.execute("INSERT INTO word_groups (word_id, group_id) VALUES (2, 1)")
                db.commit()
            except Exception as e:
                print(f"Error during database initialization: {e}")
                raise  # Re-raise the exception to fail the test

        yield client
        # Clean up the database after testing
        with app.app_context():
            db = get_db()
            db.close()
        if os.path.exists(app.config['DATABASE']):
            os.remove(app.config['DATABASE'])

def test_get_words(client):
    response = client.get('/words')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0

def test_get_words_pagination(client):
    response = client.get('/words?page=1&sort_by=kanji&order=asc')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['page'] == 1
    assert data['per_page'] == 10

def test_get_groups(client):
    response = client.get('/groups')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0

def test_get_groups_pagination(client):
    response = client.get('/groups?page=1&sort_by=name&order=asc')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['page'] == 1
    assert data['per_page'] == 10

def test_get_group(client):
    response = client.get('/groups/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['items']) > 0

def test_create_study_session(client):
    response = client.post('/study_sessions', data={'group_id': 1, 'study_activity_id': 1})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

def test_create_study_session_missing_data(client):
    response = client.post('/study_sessions', data={'group_id': 1})
    assert response.status_code == 400

def test_log_review(client):
    # First create a study session
    session_response = client.post('/study_sessions', data={'group_id': 1, 'study_activity_id': 1})
    assert session_response.status_code == 201
    session_data = json.loads(session_response.data)
    session_id = session_data['id']

    # Then log a review
    response = client.post(f'/study_sessions/{session_id}/review', data={'word_id': 1, 'correct': True})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

def test_log_review_missing_data(client):
    # First create a study session
    session_response = client.post('/study_sessions', data={'group_id': 1, 'study_activity_id': 1})
    assert session_response.status_code == 201
    session_data = json.loads(session_response.data)
    session_id = session_data['id']

    # Then try to log a review with missing data
    response = client.post(f'/study_sessions/{session_id}/review', data={'word_id': 1})
    assert response.status_code == 400

def test_insert_word(client):
    response = client.post(
        '/words',
        data=json.dumps({
            'kanji': '新',
            'romaji': 'shin',
            'english': 'new',
            'parts': '{"part_of_speech": "adj."}'
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

def test_insert_word_missing_data(client):
    response = client.post(
        '/words',
        data=json.dumps({
            'kanji': '新',
            'romaji': 'shin',
        }),
        content_type='application/json'
    )
    assert response.status_code == 400 