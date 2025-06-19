import asyncio
from langchain_ollama import ChatOllama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent



llm = ChatOllama(model="qwen3", temperature=0)


async def main():
    print(llm)
    server_params = StdioServerParameters(
        command="/Users/b0n00pr/.local/bin/uvx",
        args=[
            "mcp-neo4j-cypher",
            "--db-url",
            "bolt://localhost",
            "--username",
            "neo4j",
            "--password",
            "password",
        ],
    )

    prompt = """
Get all containers and all information
"""

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            msg = {"messages": prompt}
            result = await agent.ainvoke(msg)
            for m in result["messages"]:
                m.pretty_print()


if __name__ == "__main__":
    print("1. Main starting...")
    asyncio.run(main())
    print("12. The end.")
