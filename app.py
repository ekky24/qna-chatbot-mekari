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
import asyncio
import threading
import queue as sync_queue
import json
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, Response
from utils.connect_llm import get_ollama_response, get_agent, get_agent_response, stream_agent_response

app = Flask(__name__)

agent = None
agent_context = None

# Single persistent event loop shared across all requests so that
# agent_context (and its internal asyncio primitives) always run in the
# same loop and are never invalidated by a closed loop from a prior request.
_async_loop = asyncio.new_event_loop()
threading.Thread(target=_async_loop.run_forever, daemon=True).start()

llm = Ollama(
    base_url=config.MODEL_URL,
    model=config.MODEL_NAME,
    request_timeout=120.0,
    streaming=True,
    thinking=True,
    additional_kwargs={
        "num_batch": 16,
        "num_ctx": 8196,
    },
)
Settings.llm = llm

mcp_client = BasicMCPClient(config.MCP_SERVER_URL)
mcp_tool = McpToolSpec(client=mcp_client)

@app.route("/init")
def init():
    global agent, agent_context

    async def _init():
        a = await get_agent(mcp_tool, llm=llm)
        return a, Context(a)

    future = asyncio.run_coroutine_threadsafe(_init(), _async_loop)
    agent, agent_context = future.result(timeout=60)
    return jsonify(success=True)

@app.route('/list_tools')
def list_tools():
    async def _list():
        tools = await mcp_tool.to_tool_list_async()
        return [t.metadata.name for t in tools]

    future = asyncio.run_coroutine_threadsafe(_list(), _async_loop)
    return jsonify(future.result(timeout=30))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get('msg') if data else None

    future = asyncio.run_coroutine_threadsafe(
        get_agent_response(msg, agent, agent_context, verbose=True),
        _async_loop,
    )
    return jsonify({'response': future.result(timeout=120)})

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    msg = data.get('msg') if data else None

    if agent is None:
        return jsonify({'error': 'Agent not initialized. Call /init first.'}), 503

    q = sync_queue.Queue()

    async def _stream():
        try:
            async for event_type, content in stream_agent_response(msg, agent, agent_context, verbose=True):
                q.put(json.dumps({'type': event_type, 'content': content}))
        finally:
            q.put(None)

    asyncio.run_coroutine_threadsafe(_stream(), _async_loop)

    def generate():
        while True:
            try:
                item = q.get(timeout=120)
            except sync_queue.Empty:
                yield "data: [DONE]\n\n"
                break
            if item is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {item}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000', threaded=True)
