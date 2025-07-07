from mcp.server.fastmcp import FastMCP

# Initialize a stateless FastMCP server
mcp = FastMCP(name="my-tools-server", stateless_http=True)

# --- Tool 1: A simple calculator tool ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b

# --- Tool 2: A simple greeter tool ---
@mcp.tool()
async def greet(name: str) -> str:
    """Provides a friendly greeting."""
    return f"Hello, {name}! Welcome to the world of MCP tools."

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()