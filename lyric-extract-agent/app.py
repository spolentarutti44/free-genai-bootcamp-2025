from flask import Flask, jsonify, request
import os
import logging  # Import the logging module
from agents.supervisor_agent import SupervisorAgent
from utils.qdrant_utils import init_qdrant

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG to see detailed logs

# Initialize the supervisor agent
supervisor_agent = SupervisorAgent()

# Initialize Qdrant collection for history
init_qdrant()

@app.route('/lyrics/<song_title>', methods=['GET'])
def get_lyrics(song_title):
    """Retrieve lyrics for a specific song."""
    try:
        # Direct call to the specialized agent
        lyrics = supervisor_agent.lyric_agent.get_lyrics(song_title)
        
        # Log interaction
        supervisor_agent.history_agent.log_interaction("get_lyrics", song_title, lyrics)
        
        return jsonify({"lyrics": lyrics, "song_title": song_title})
    except Exception as e:
        logging.error(f"Error in get_lyrics: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e)}), 500

@app.route('/lyrics/search', methods=['GET'])
def search_lyrics():
    """Search for lyrics by title or phrase."""
    query = request.args.get('query', '')
    try:
        # Direct call to the specialized agent
        results = supervisor_agent.song_agent.search_songs(query)
        
        # Log interaction
        supervisor_agent.history_agent.log_interaction("search_lyrics", query, results)
        
        return jsonify({"results": results})
    except Exception as e:
        logging.error(f"Error in search_lyrics: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e)}), 500

@app.route('/lyrics/summary', methods=['GET'])
def summarize_lyrics():
    """Summarize the lyrics of a song."""
    song_title = request.args.get('song_title', '')
    try:
        # Get lyrics and then summarize
        lyrics = supervisor_agent.lyric_agent.get_lyrics(song_title)
        summary = supervisor_agent.lyric_agent.summarize_lyrics(lyrics)
        
        # Log interaction
        supervisor_agent.history_agent.log_interaction("summarize_lyrics", song_title, summary)
        
        return jsonify({"summary": summary, "song_title": song_title})
    except Exception as e:
        logging.error(f"Error in summarize_lyrics: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e)}), 500

@app.route('/lyrics/vocabulary', methods=['GET'])
def generate_vocabulary():
    """Generate vocabulary from the lyrics."""
    song_title = request.args.get('song_title', '')
    try:
        # Get lyrics and then generate vocabulary
        lyrics = supervisor_agent.lyric_agent.get_lyrics(song_title)
        vocabulary = supervisor_agent.vocabulary_agent.generate_vocabulary(lyrics)
        
        # Log interaction
        supervisor_agent.history_agent.log_interaction("generate_vocabulary", song_title, vocabulary)
        
        return jsonify({"vocabulary": vocabulary, "song_title": song_title})
    except Exception as e:
        logging.error(f"Error in generate_vocabulary: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e)}), 500

@app.route('/lyrics/history', methods=['GET'])
def get_history():
    """Retrieve the history of the conversation."""
    try:
        # Get history
        history = supervisor_agent.history_agent.get_history()
        
        return jsonify({"history": history})
    except Exception as e:
        logging.error(f"Error in get_history: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_agent():
    """Ask the supervisor agent a question."""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Use the supervisor agent to process the request
        response = supervisor_agent.process_request(query)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in ask_agent: {e}", exc_info=True) # Log detailed error
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 