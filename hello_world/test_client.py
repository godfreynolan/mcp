import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp


async def main() -> None:
    async with MCPServerStreamableHttp(
        params={
            "url": "http://127.0.0.1:8000/mcp",
        },
    ) as server:
        agent = Agent(
            name="Assistant",
            model="gpt-5.6-sol",
            mcp_servers=[server],
        )
        response = await Runner.run(agent, "Use the hello tool to greet Ada.")
        print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
