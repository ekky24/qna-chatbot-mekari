SERVICE_URL = 'http://localhost:5000'
MCP_SERVER_URL = 'http://localhost:4000/sse'
MODEL_URL = 'http://192.168.98.202:11434'

MODEL_NAME = 'qwen3:4b'
SYSTEM_PROMPT = """
    You are an AI assistant for Tool Calling.
    Before you help a user, you need to work with tools to interact with 
    our database which contains fraudulent and non-fraudulent transaction data. 
    You also could interact with fraud manual documents.
"""
