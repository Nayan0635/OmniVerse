import asyncio
import json

from mcp import Client, StdioServerParameters

import _config

if _config.LLM_PROVIDER == "gemini":
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=_config.CHAT_MODELS,
        google_api_key=_config.GEMINI_API_KEY,
    )
elif _config.LLM_PROVIDER == "nvidia":
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    llm = ChatNVIDIA(
        model=_config.CHAT_MODELS,
        api_key=_config.NVIDIA_API_KEY,
    )
elif _config.LLM_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model=_config.CHAT_MODELS,
        api_key=_config.OPENAI_API_KEY,
    )
else:
    raise ValueError(f"don't support {_config.LLM_PROVIDER!r}")

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

        client = llm.bind_tools(openai_tools)

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
                resp = client.invoke(messages)

                if not resp.tool_calls:
                    final = resp.content
                    break

                messages.append(resp)
                for call in resp.tool_calls:
                    args = call["args"]
                    print(f"   → tool: {call['name']}({args})")
                    result = await session.call_tool(call["name"], args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result.content[0].text,
                    })

            print("\nAgent:")
            print(final or "I couldn't finish that request. Please try rephrasing.")


if __name__ == "__main__":
    asyncio.run(run())
