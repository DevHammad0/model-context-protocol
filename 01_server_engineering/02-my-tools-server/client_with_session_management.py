import httpx
import json
import asyncio


## With Session Management


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/') + '/mcp/'
        self.session_id: str | None = None
        self.request_id = 0

    def _get_next_id(self):
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    def _get_headers(self):
        """Get headers including session ID if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    async def _mcp_request(self, method: str, params: dict = {}):
        """Make an MCP request with proper session handling"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._get_next_id()
        }
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"   -> Sending {method} request...")
                response = await client.post(
                    self.base_url, 
                    json=payload, 
                    headers=self._get_headers()
                )
                
                print(f"   -> Received response with status code {response.status_code}")
                
                # Check for session ID in response headers (for initialization)
                if method == "initialize" and "mcp-session-id" in response.headers:
                    self.session_id = response.headers["mcp-session-id"]
                    print(f"   -> Captured session ID: {self.session_id}")
                
                response.raise_for_status()
                
                # Parse SSE response
                for line in response.text.strip().split('\n'):
                    if line.startswith('data: '):
                        return json.loads(line[6:])
                return {"error": "No data found in SSE response"}
                
            except Exception as e:
                print(f"   -> An error occurred: {e}")
                return {"error": str(e)}

    async def initialize(self):
        """Initialize the MCP session"""
        print("\n[Initialization: Establishing MCP session]")
        init_params = {
            "protocolVersion": "2025-03-26",
            "clientInfo": {
                "name": "python-mcp-client",
                "version": "1.0.0"
            },
            "capabilities": {}
        }
        
        response = await self._mcp_request("initialize", init_params)
        if 'error' in response:
            print(f"   -> Initialization failed: {response['error']}")
            return False
        else:
            print(f"   -> Successfully initialized with server: {response.get('result', {}).get('serverInfo', {}).get('name')}")
            
            # Send initialized notification
            await self._send_initialized_notification()
            return True

    async def _send_initialized_notification(self):
        """Send the initialized notification"""
        payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    self.base_url, 
                    json=payload, 
                    headers=self._get_headers()
                )
                print("   -> Sent initialized notification")
            except Exception as e:
                print(f"   -> Failed to send initialized notification: {e}")

    async def list_tools(self):
        """List available tools"""
        return await self._mcp_request("tools/list")

    async def call_tool(self, name: str, arguments: dict):
        """Call a specific tool"""
        params = {"name": name, "arguments": arguments}
        return await self._mcp_request("tools/call", params)

# --- Main Demonstration ---
async def main():
    """A proper MCP client demonstration with session management."""
    print("--- MCP Tool Client with Proper Session Management ---")
    
    client = MCPClient()
    
    # 1. Initialize the session
    if not await client.initialize():
        print("Failed to initialize. Exiting.")
        return
    
    # 2. List available tools
    print("\n[Step 1: Discovering Tools]")
    tools_response = await client.list_tools()
    
    if 'error' in tools_response:
        print(f"   -> Error listing tools: {tools_response['error']}")
        return
        
    tools = tools_response.get('result', {}).get('tools', [])
    print(f"   -> Success! Server has {len(tools)} tools:")
    for tool in tools:
        print(f"      - {tool.get('name')}: {tool.get('description')}")

    # 3. Call the 'add' tool
    print("\n[Step 2: Calling the 'add' tool]")
    print("Now, we'll call the 'add' tool with numbers 5 and 7.")
    add_response = await client.call_tool("add", {"a": 5, "b": 7})
    
    if 'error' in add_response:
        print(f"   -> Error calling 'add': {add_response['error']}")
    else:
        result = add_response.get('result', {}).get('content', [{}])[0].get('text')
        print(f"   -> Success! The server returned the result: '{result}'")

    # 4. Call the 'greet' tool
    print("\n[Step 3: Calling the 'greet' tool]")
    print("Finally, we'll call the 'greet' tool with the name 'Student'.")
    greet_response = await client.call_tool("greet", {"name": "Student"})
    
    if 'error' in greet_response:
        print(f"   -> Error calling 'greet': {greet_response['error']}")
    else:
        result = greet_response.get('result', {}).get('content', [{}])[0].get('text')
        print(f"   -> Success! The server returned the greeting: '{result}'")

if __name__ == "__main__":
    asyncio.run(main()) 