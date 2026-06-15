import requests
from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCallResult,
    ToolCall,
    AgentStream,
)
from llama_index.core.workflow import Context
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

async def get_agent(tools: McpToolSpec, llm):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with fraudulent and non-fraudulent transaction data. \
            This agent also could interact with fraud manual documents.",
        tools=tools,
        llm=llm,
        system_prompt=config.SYSTEM_PROMPT,
    )
    return agent

async def get_agent_response(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

async def stream_agent_response(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if type(event) == ToolCall:
            if verbose:
                print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
            yield ('status', f'Calling tool: {event.tool_name}')
        elif type(event) == ToolCallResult:
            if verbose:
                print(f"Tool {event.tool_name} returned {event.tool_output}")
            yield ('status', f'Done: {event.tool_name}')
        elif type(event) == AgentStream:
            if event.thinking_delta:
                yield ('thinking', event.thinking_delta)
            if event.delta:
                yield ('token', event.delta)

    await handler
