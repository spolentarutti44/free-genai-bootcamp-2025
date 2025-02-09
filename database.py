import sqlite3
from flask import g, Flask, current_app
import os

# DATABASE = 'learning_portal.db'  # Remove the hardcoded DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Get the database path from the Flask app's configuration
        DATABASE = current_app.config['DATABASE']
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    print("Initializing database...")
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)

if __name__ == '__main__':
    # Create a Flask app instance for the context
    app = Flask(__name__)
    # Configure the database path for the app
    app.config['DATABASE'] = 'learning_portal.db'
    with app.app_context():
        # This will only run when this file is executed directly
        # It's useful for initializing the database
        if os.path.exists(app.config['DATABASE']):
            os.remove(app.config['DATABASE'])  # Remove existing database
        init_db()
        print("Database initialized") 