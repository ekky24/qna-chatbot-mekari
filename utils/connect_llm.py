import requests
import config

def get_ollama_response(message: str) -> str:
    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {"role": "user", "content": message}
        ],
        "stream": False,
    }
    response = requests.post(f"{config.MODEL_URL}/api/chat", json=payload)
    response_json = response.json()

    return response_json['message']['content']