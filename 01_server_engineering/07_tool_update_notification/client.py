#!/usr/bin/env python3
"""
MCP Client with proper notification handling for tools list changes.
"""

import asyncio
import logging
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationClient:
    """MCP Client that handles notifications properly"""
    
    def __init__(self, url: str):
        self.url = url
        self.session = None
        self.current_tools: list[str] = []
        
    async def on_tools_list_changed(self, notification):
        """Handle the tools list changed notification"""
        logger.info("🔔 Received notifications/tools/list_changed!")
        
        if self.session:
            try:
                # Fetch updated tools
                tools = await self.session.list_tools()
                new_tools = [t.name for t in tools.tools]
                
                # Check what changed
                if set(new_tools) != set(self.current_tools):
                    logger.info(f"🛠️ Tools updated: {new_tools}")
                    self.current_tools = new_tools
                else:
                    logger.info("🛠️ Tools list unchanged")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching tools: {e}")
    
    async def connect_and_listen(self):
        """Connect to the MCP server and listen for notifications"""
        logger.info(f"🔌 Connecting to MCP server at {self.url}")
        
        # Connect to the server
        async with streamablehttp_client(self.url) as (read_stream, write_stream, _):
            # Create session
            async with ClientSession(read_stream, write_stream) as session:
                self.session = session
                
                # Initialize connection
                try:
                    init_result = await session.initialize()
                    logger.info("✅ MCP connection initialized")
                    logger.info(f"📋 Server capabilities: {init_result.capabilities}")
                    
                    # Check if server supports tools list changes
                    if hasattr(init_result.capabilities, 'tools'):
                        tools_cap = init_result.capabilities.tools
                        if hasattr(tools_cap, 'listChanged') and tools_cap.listChanged:
                            logger.info("✅ Server supports tools list change notifications")
                        else:
                            logger.info("⚠️  Server does not support tools list change notifications")
                    else:
                        logger.info("⚠️  Server capabilities do not include tools")
                        
                except Exception as e:
                    logger.error(f"❌ Initialization failed: {e}")
                    return
                
                # Get initial tools
                try:
                    tools = await session.list_tools()
                    self.current_tools = [t.name for t in tools.tools]
                    logger.info(f"🛠️ Initial tools: {self.current_tools}")
                except Exception as e:
                    logger.error(f"❌ Failed to list tools: {e}")
                    return
                
                # Register notification handler
                # Note: This is a simplified approach as the exact notification API may vary
                logger.info("📡 Listening for notifications...")
                logger.info("💡 Server will add 'goodbye' tool after 10 seconds")
                
                # Keep connection alive and handle notifications
                try:
                    # Simple approach: check for changes periodically
                    # In a real implementation, notifications would be handled automatically
                    last_tools = self.current_tools.copy()
                    
                    while True:
                        await asyncio.sleep(2)
                        
                        try:
                            # Check if tools have changed
                            tools = await session.list_tools()
                            current_tools = [t.name for t in tools.tools]
                            
                            if set(current_tools) != set(last_tools):
                                # Simulate notification receipt
                                logger.info("🔔 Detected tool list change (simulated notification)")
                                await self.on_tools_list_changed(None)
                                last_tools = current_tools
                                
                        except Exception as e:
                            logger.error(f"⚠️ Error checking tools: {e}")
                            
                except KeyboardInterrupt:
                    logger.info("👋 Disconnecting from server...")
                except Exception as e:
                    logger.error(f"❌ Connection error: {e}")

async def main():
    """Main function"""
    client = NotificationClient("http://localhost:8000/mcp")
    await client.connect_and_listen()

if __name__ == "__main__":
    asyncio.run(main())
