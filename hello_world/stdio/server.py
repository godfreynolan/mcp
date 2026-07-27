"""A minimal Hello World MCP server using the stdio transport."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-world")


@mcp.tool()
def hello(name: str = "World") -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
