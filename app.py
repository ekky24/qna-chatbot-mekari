from flask import Flask, request, jsonify
import config
from utils.connect_llm import get_ollama_response

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get('msg') if data else None

    response = get_ollama_response(msg)

    return jsonify({
        'response': response,
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
