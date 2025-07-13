#!/usr/bin/env python3
"""
MCP Server with dynamic tool registration and proper list_changed notifications.
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("Dynamic Tool Server")

# Define an initial tool
@mcp.tool()
async def hello(ctx: Context) -> str:
    """
    A simple greeting tool.
    """
    await ctx.info("hello tool invoked")
    return "👋 Hello!"

# Background task to add/remove tools at runtime
async def dynamic_tool_manager():
    """Add a new tool dynamically after a delay"""
    # Wait so clients can connect and list the initial "hello" tool
    await asyncio.sleep(10)
    
    logger.info("Adding dynamic tool 'goodbye'...")
    
    # Dynamically register a new tool
    @mcp.tool()
    async def goodbye(ctx: Context) -> str:
        """
        A farewell tool added dynamically.
        """
        await ctx.info("goodbye tool invoked") 
        return "👋 Goodbye!"
    
    # Send notification about tool list change
    try:
        await mcp.broadcast_notification(
            method="notifications/tools/list_changed",
            params={}
        )
        logger.info("✅ notifications/tools/list_changed sent: added 'goodbye'")
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")

# Run the server
if __name__ == "__main__":
    # Run with streamable HTTP transport for better notification support
    logger.info("Starting MCP server with streamable HTTP transport...")
    
    # Get the streamable HTTP app
    mcp_app = mcp.streamable_http_app()
    
    # Start the dynamic tool manager in the background
    asyncio.create_task(dynamic_tool_manager())
    
    # Run the server with uvicorn
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
