from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})

if __name__ == '__main__':
    print("Starting simple test Flask server on port 5001...")
    app.run(debug=True, port=5001) 