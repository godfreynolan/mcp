import asyncio
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio


async def main() -> None:
    async with MCPServerStdio(
        params={
            "command": sys.executable,
            "args": [str(Path(__file__).with_name("server.py"))],
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
