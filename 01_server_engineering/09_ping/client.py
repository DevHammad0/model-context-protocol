import asyncio
import time
import httpx
import json

async def ping_server():
    """Simple MCP ping client"""
    url = "http://localhost:8000/mcp/"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-06-18"
    }
    
    async with httpx.AsyncClient() as client:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "clientInfo": {"name": "ping-client", "version": "1.0.0"},
                "capabilities": {}
            },
            "id": 1
        }
        
        response = await client.post(url, json=init_request, headers=headers)
        
        response.raise_for_status()
        
        print("✅ Initialization successful")
        print(f"Session ID: {response.headers.get('mcp-session-id')}")
        
        # Get session ID and add to headers
        session_id = response.headers.get("mcp-session-id")
        if session_id:
            headers["mcp-session-id"] = session_id
        
        # Send initialized notification
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        response = await client.post(url, json=initialized_request, headers=headers)
        response.raise_for_status()
        print("✅ Initialized notification sent")
        
        # Send ping
        ping_request = {
            "jsonrpc": "2.0",
            "id": "ping_test",
            "method": "ping"
        }
        
        start_time = time.time()
        try:
            # Add timeout as per specification
            response = await client.post(url, json=ping_request, headers=headers, timeout=5.0)
            
            end_time = time.time()
            rtt_ms = (end_time - start_time) * 1000
            
            response.raise_for_status()
            
            # The ping response can also be an SSE stream or plain JSON
            pong_data_text = response.text
            if "data: " in pong_data_text:
                data_line = pong_data_text.split("data: ")[1]
                pong_result = json.loads(data_line)
            else:
                pong_result = response.json()

            # Validate response format as per specification
            if (pong_result.get("jsonrpc") == "2.0" and 
                pong_result.get("id") == "ping_test" and 
                "result" in pong_result):
                print(f"✅ Pong received in {rtt_ms:.2f} ms")
                print(f"   Response: {json.dumps(pong_result)}")
            else:
                print(f"❌ Invalid ping response format: {json.dumps(pong_result)}")
                
        except Exception as e:
            # Handle timeouts and connection failures as per specification
            end_time = time.time()
            rtt_ms = (end_time - start_time) * 1000
            
            if "timeout" in str(e).lower():
                print(f"❌ Ping timeout after {rtt_ms:.2f} ms - connection may be stale")
                print("   Consider terminating connection or reconnecting")
            else:
                print(f"❌ Ping failed: {e}")
                print("   Connection failure detected")

if __name__ == "__main__":
    asyncio.run(ping_server()) 