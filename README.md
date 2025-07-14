# Model Context Protocol (MCP) - Comprehensive Implementation Repository

A complete implementation collection of the Model Context Protocol (MCP) featuring servers, clients, utilities, and real-world applications. This repository demonstrates every aspect of MCP from basic "Hello World" examples to advanced features like progress tracking, cancellation and resumability.

## 🏗️ Repository Structure

```
Model_Context_Protocol_(MCP)/
├── 01_server_features/          # Server-side MCP implementations
├── 02_client_features/          # Client-side MCP implementations  
├── 03_base_protocol/           # Core protocol features & utilities
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- UV package manager (recommended)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Model_Context_Protocol_(MCP)

# Install any example (using UV)
cd 01_server_features/01-hello-mcp
uv sync
```

### Running Your First MCP Server
```bash
# Start a basic MCP server
cd 01_server_features/01-hello-mcp
uv run python server.py

# Test with included Postman collection or HTTP client
```

## 📋 Table of Contents

- [Server Features](#-server-features)
- [Client Features](#-client-features)
- [Base Protocol](#-base-protocol)
- [Development Utilities](#-development-utilities)

## 🔧 Server Features

### Core Server Implementations

#### 1. Hello MCP (`01_server_features/01-hello-mcp/`)
**Basic weather forecast server demonstrating fundamental MCP concepts**
- Simple tool implementation (`get_forecast`)
- FastMCP server setup
- HTTP transport via uvicorn
- Postman collection included

```python
@mcp.tool()
async def get_forecast(city: str) -> str:
    return f"The weather in {city} will be warm and sunny"
```

#### 2. Tools (`01_server_features/02_tools/`)
**Advanced tool management and notifications**

**Simple Tools Server** (`02_simple_tools_server_&_client/`)
- Calculator tool (`add` function)
- Greeting tool with personalization
- Client examples included
- Session management demonstrations

**Tool Update Notifications** (`07_tool_update_notification/`)
- Dynamic tool registration
- Real-time tool list updates
- Background tool management
- Streamable HTTP notifications

#### 3. Resources (`01_server_features/03_resources/`)
**Static and dynamic resource serving**
- Static welcome messages
- Dynamic server time resources
- URI templating with variables
- Multiple content types (text/plain, JSON)

```python
@mcp.resource(uri="app:///messages/welcome")
async def get_welcome_message() -> str:
    return "Hello and welcome to the MCP Resource Server!"
```

#### 4. Prompts (`01_server_features/04_prompts/`)
**LLM prompt template management**
- Simple text prompts
- Complex prompt messages with roles
- Prompt argument handling
- Multiple prompt formats

### Server Utilities

#### Completion (`01_server_features/utilities/01_completion/`)
**Auto-completion for tool arguments**
- Language completions (Python, JavaScript, TypeScript)
- Framework suggestions
- GitHub repository completions
- Context-aware suggestions

#### Logging (`01_server_features/utilities/02_logging/`)
**Comprehensive logging with MCP Context**
- Info, debug, warning levels
- Task-specific logging
- Real-time log streaming
- Structured log messages

#### Pagination (`01_server_features/utilities/03_pagination/`)
**Cursor-based pagination for large datasets**
- MCP 2025-06-18 compliant implementation
- Opaque cursor tokens
- Server-determined page sizes
- Resource list pagination

## 👥 Client Features

### 1. Roots (`02_client_features/01_roots/`)
**Directory permission and project boundary management**
- File system root definitions
- Security boundary enforcement
- Project context awareness
- Root capability negotiation

**Key Features:**
- Automatic project detection
- Safe file access patterns
- Multi-root project support
- Dynamic root updates

### 2. Sampling (`02_client_features/02_sampling/`)
**LLM sampling and generation control**
- Temperature and top-p controls
- Custom sampling strategies
- Response format specifications
- Generation parameter management

### 3. Elicitation (`02_client_features/03_elicitation/`)
**User interaction and preference gathering**
- Interactive prompt flows
- User preference collection
- Context-aware questioning
- Response validation

## 🔄 Base Protocol

### Core Lifecycle (`03_base_protocol/01_hello_mcp_lifecycle/`)
**Complete MCP connection lifecycle management**
- Initialization handshake
- Capability negotiation
- Session management
- Graceful shutdown

**Demonstrates:**
- Protocol version handling
- Client-server communication
- Persistent HTTP connections
- Error handling patterns

### Resumability (`03_base_protocol/02_resumability_and_redelivery/`)
**Connection resilience and message recovery**
- Automatic reconnection
- Message deduplication
- Event store integration
- Resumption token handling

**Features:**
- In-memory event storage
- Last-Event-ID headers
- Client timeout handling
- Seamless operation recovery

### Protocol Utilities

#### Cancellation (`03_base_protocol/utilities/01_cancellation/`)
**Request cancellation and resource cleanup**
- Graceful task interruption
- Resource cleanup
- Cancellation notifications
- AsyncIO integration

```python
@mcp_server.tool()
async def process_large_file(ctx: Context, filename: str, processing_time: int = 10) -> str:
    try:
        for i in range(processing_time):
            await asyncio.sleep(1)  # Cancellation checkpoint
            await ctx.debug(f"Processed chunk {i + 1}/{processing_time}")
        return f"Successfully processed {filename}"
    except asyncio.CancelledError:
        await ctx.warning(f"Processing of {filename} was cancelled")
        raise
```

#### Ping (`03_base_protocol/utilities/02_ping/`)
**Connection health monitoring**
- Automatic ping/pong handling
- Connection validation
- Network latency measurement
- Keep-alive mechanisms

#### Progress (`03_base_protocol/utilities/03_progress/`)
**Real-time operation progress tracking**
- Progress notifications
- Percentage completion
- Status messages
- Streaming updates

```python
await ctx.report_progress(
    progress=chunk,
    total=total_chunks,
    message=f"Downloading {filename}... {percentage:.1f}%"
)
```


## 🛠️ Development Utilities

### Testing Tools
- **Postman Collections**: Pre-configured API tests for all servers
- **Client Examples**: Reference implementations for each feature
- **HTTP Clients**: Direct HTTP testing utilities

### Code Organization
- **Consistent Structure**: All examples follow the same pattern
- **UV Integration**: Modern Python package management
- **Type Safety**: Full Pydantic integration
- **Async/Await**: Modern Python concurrency patterns


## 🔧 Common Patterns

### Server Setup
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="my-server",
    description="Server description",
    stateless_http=True  # For HTTP transport
)
```

### Tool Definition
```python
@mcp.tool()
async def my_tool(param: str, ctx: Context) -> str:
    await ctx.info(f"Processing {param}")
    return f"Result for {param}"
```

### Resource Definition
```python
@mcp.resource(uri="app:///my-resource")
async def my_resource() -> str:
    return "Resource content"
```

### Client Connection
```python
async with streamablehttp_client("http://localhost:8000/mcp/") as (read, write, _):
    async with ClientSession(read, write) as session:
        result = await session.call_tool("my_tool", {"param": "value"})
```

### Development Setup
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to any example
cd 01_server_features/01-hello-mcp

# Install dependencies
uv sync

# Run the example
uv run python server.py
```

## 📖 Additional Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/mcp-python)
- [OpenAI Agents SDK](https://github.com/openai/agents-python)

**Built with 💙 for the MCP community**

This repository serves as a comprehensive learning resource for understanding and implementing the Model Context Protocol across various use cases and transport mechanisms.
