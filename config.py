SERVICE_URL = 'http://localhost:5000'
MCP_SERVER_URL = 'http://localhost:4000/sse'
MODEL_URL = 'http://192.168.98.202:11434'

MODEL_NAME = 'qwen3:4b'
EMBEDDING_MODEL_NAME = 'qwen3-embedding:4b'

EMBEDDING_MODEL_FILENAME_MAPPER = {
    'qwen3-embedding:4b': 'qwen3',
}
SYSTEM_PROMPT = """
    You are an AI assistant for Question and Answering system.
    Before you help a user, you need to work with tools to interact with 
    our database which contains fraudulent and non-fraudulent transaction data, and 
    you also could interact with fraud manual documents.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
"""
