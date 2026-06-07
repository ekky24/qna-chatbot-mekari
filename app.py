# pyrefly: ignore [missing-import]
import nest_asyncio
nest_asyncio.apply()
# pyrefly: ignore [missing-import]
from llama_index.llms.ollama import Ollama
# pyrefly: ignore [missing-import]
from llama_index.core import Settings
# pyrefly: ignore [missing-import]
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# pyrefly: ignore [missing-import]
from llama_index.core.agent.workflow import FunctionAgent
# pyrefly: ignore [missing-import]
from llama_index.core.agent.workflow import (
    FunctionAgent, 
    ToolCallResult, 
    ToolCall)
# pyrefly: ignore [missing-import]
from llama_index.core.workflow import Context
import config
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from utils.connect_llm import get_ollama_response, get_agent, get_agent_response

app = Flask(__name__)

agent = None
agent_context = None

llm = Ollama(
    base_url=config.MODEL_URL,
    model=config.MODEL_NAME, 
    request_timeout=120.0,
    additional_kwargs={
        "num_batch": 16,
        "num_ctx": 8196,
    },
)
Settings.llm = llm

mcp_client = BasicMCPClient(config.MCP_SERVER_URL)
mcp_tool = McpToolSpec(client=mcp_client)

@app.route("/init")
async def init():
    global agent
    global agent_context
    global llm
    agent = await get_agent(mcp_tool, llm=llm)
    agent_context = Context(agent)

    return jsonify(success=True)

@app.route('/list_tools')
async def list_tools():
    rets = []
    tools = await mcp_tool.to_tool_list_async()
    for tool in tools:
        rets.append(tool.metadata.name)

    return jsonify(rets)

@app.route("/chat", methods=["POST"])
async def chat():
    data = request.get_json()
    msg = data.get('msg') if data else None

    # response = get_ollama_response(msg)
    response = await get_agent_response(msg, agent, agent_context, verbose=True)

    return jsonify({
        'response': response,
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
