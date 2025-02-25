from flask import Flask, request, jsonify
from rag import RAGAgent, SimpleRetrievalTool
from chat import BedrockChat

app = Flask(__name__)


# Initialize the retrieval tool and RAG agent
retrieval_tool = SimpleRetrievalTool()
rag_agent = RAGAgent(retrieval_tool, BedrockChat())

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response = rag_agent.generate_response(user_input)
    retrieval_tool.add_to_knowledge_base("User", user_input)
    retrieval_tool.add_to_knowledge_base("Bot", response)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5100) 