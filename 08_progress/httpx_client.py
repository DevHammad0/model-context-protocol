import asyncio
import json
import httpx
from typing import Dict, Any, Optional

class SimpleMCPClient:
    """Simple MCP client using httpx"""
    
    def __init__(self, url: str):
        self.url = url
        self.session_id: Optional[str] = None
        self.headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
    
    async def initialize(self, client: httpx.AsyncClient) -> bool:
        """Initialize MCP connection"""
        print("🔌 Initializing MCP connection...")
        
        init_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "simple-mcp-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            response = await client.post(self.url, json=init_data, headers=self.headers)
            response.raise_for_status()
            
            self.session_id = response.headers.get("mcp-session-id")
            print(f"✅ Connected! Session ID: {self.session_id}")
            
            # Send initialized notification
            await self._send_initialized(client)
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def _send_initialized(self, client: httpx.AsyncClient):
        """Send initialized notification"""
        initialized_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        await client.post(self.url, json=initialized_data, headers=headers)
        print("✅ Initialized notification sent")
    
    async def call_tool(self, client: httpx.AsyncClient, tool_name: str, arguments: Dict[str, Any]):
        """Call MCP tool with progress tracking"""
        print(f"\n🛠️ Calling tool: {tool_name}")
        print("-" * 50)
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
                "_meta": {
                    "progressToken": 3
                }
            }
        }
        
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        try:
            # Use streaming to handle progress updates
            async with client.stream("POST", self.url, json=request_data, headers=headers) as response:
                if response.status_code != 200:
                    print(f"❌ Request failed: {response.status_code}")
                    return None
                
                content_type = response.headers.get("content-type", "").lower()
                
                if "text/event-stream" in content_type:
                    return await self._handle_sse_response(response)
                else:
                    # Handle regular JSON response
                    content = await response.aread()
                    data = json.loads(content)
                    return data.get("result")
                    
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return None
    
    async def _handle_sse_response(self, response):
        """Handle Server-Sent Events response"""
        print("🌊 Receiving progress updates...")
        
        final_result = None
        buffer = ""
        
        async for chunk in response.aiter_bytes():
            buffer += chunk.decode('utf-8')
            
            # Process complete lines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        
                        # Handle progress notifications
                        if data.get("method") == "notifications/progress":
                            params = data.get("params", {})
                            progress = params.get("progress", 0)
                            total = params.get("total")
                            message = params.get("message", "Working...")
                            
                            if total:
                                percentage = (progress / total) * 100
                                progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
                                print(f"📊 [{progress_bar}] {percentage:.1f}% - {message}")
                            else:
                                print(f"📊 Progress: {progress} - {message}")
                        
                        # Handle final result
                        elif "result" in data:
                            final_result = data["result"]
                            print("✅ Tool completed")
                            
                    except json.JSONDecodeError:
                        continue  # Skip malformed JSON
        
        return final_result

async def main():
    """Simple MCP client demo"""
    print("🚀 Simple MCP Client Demo")
    print("=" * 40)
    
    url = "http://localhost:8000/mcp/"
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=300.0)) as client:
        mcp_client = SimpleMCPClient(url)
        
        # Initialize connection
        if not await mcp_client.initialize(client):
            return
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(0.5)
        
        # Test scenarios
        scenarios = [
            {
                "name": "📁 File Download",
                "tool": "download_file",
                "args": {"filename": "mcp-dataset.zip", "size_mb": 5}
            },
            {
                "name": "🔄 Data Processing",
                "tool": "process_data", 
                "args": {"records": 20}
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}")
            
            result = await mcp_client.call_tool(
                client,
                scenario["tool"], 
                scenario["args"]
            )
            
            print("-" * 50)
            if result and "content" in result:
                for content in result["content"]:
                    print(f"✅ Result: {content.get('text', 'No text content')}")
            else:
                print("✅ Tool completed successfully")

if __name__ == "__main__":
    asyncio.run(main()) 