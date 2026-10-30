"""
MCP-powered Q&A agent for OmniVerse.

Launches mcp_server.py over stdio, gives its tools to the chat LLM
configured in _config.py, and lets the model choose which tool to call.
Tool results are sent back to the model so it can write the final reply
(needed for search_documents, which returns raw chunks).

    python mcp_agent.py
"""
import asyncio
import json

from openai import OpenAI
from google import genai
from mcp import Client, StdioServerParameters

import _config

if _config.LLM_PROVIDER == "nvidia":
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=_config.NVIDIA_API_KEY,
    )
elif _config.LLM_PROVIDER == "gemini":
    client = genai.Client(api_key=_config.GEMINI_API_KEY)

elif _config.LLM_PROVIDER == "openai":
    client = OpenAI(api_key=_config.OPENAI_API_KEY)
else:
    raise ValueError(
        f"mcp_agent.py supports LLM_PROVIDER 'nvidia' or 'openai', got {_config.LLM_PROVIDER!r}"
    )

server = StdioServerParameters(command="python", args=["mcp_server.py"])

SYSTEM_PROMPT = (
    "You answer questions about the user's ingested documents using the tools provided. "
    "Prefer ask_documents for questions about document content, list_documents for "
    "'what files do I have', and search_documents when you need raw source text. "
    "Base answers only on tool results and keep the [file § chunk] citations. "
    "If the tools return nothing relevant, say \"I don't know\"."
)

MAX_STEPS = 4  # safety cap on tool-call rounds per question


async def run():
    async with Client(server) as session:
        tools = await session.list_tools()
        print("🔌 Connected to MCP server. Available tools:")

        openai_tools = []
        for tool in tools.tools:
            print(f"   - {tool.name}")
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,  # v2: snake_case
                },
            })

        print("\n🤖 Type 'exit' to quit.")
        while True:
            user_input = input("\nAsk? ")
            if user_input.strip().lower() == "exit":
                print("Agent: Cya! 👋")
                return

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ]

            final = None
            for _ in range(MAX_STEPS):
                resp = client.chat.completions.create(
                    model=_config.CHAT_MODELS,
                    messages=messages,
                    tools=openai_tools,
                )
                msg = resp.choices[0].message

                if not msg.tool_calls:
                    final = msg.content
                    break

                messages.append(msg.model_dump(exclude_none=True))
                for call in msg.tool_calls:
                    args = json.loads(call.function.arguments or "{}")
                    print(f"   → tool: {call.function.name}({args})")
                    result = await session.call_tool(call.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result.content[0].text,
                    })

            print("\nAgent:")
            print(final or "I couldn't finish that request. Please try rephrasing.")


if __name__ == "__main__":
    asyncio.run(run())
