import asyncio
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp


async def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        prompt = input("Ask about a customer's calls: ").strip()
    if not prompt:
        print("No question provided.")
        return

    async with MCPServerStreamableHttp(
        params={
            "url": "http://127.0.0.1:8000/mcp",
        },
    ) as server:
        agent = Agent(
            name="Assistant",
            model="gpt-5.6-sol",
            mcp_servers=[server],
            instructions=(
                "Use the r-mobile MCP tools to answer questions about customer calls. "
                "If a customer reference is ambiguous, ask the user to choose from "
                "the returned matches."
            ),
        )
        response = await Runner.run(agent, prompt)
        print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
