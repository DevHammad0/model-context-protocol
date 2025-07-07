from mcp.server.fastmcp import FastMCP
import datetime
from zoneinfo import ZoneInfo

# Initialize a stateless FastMCP server
mcp = FastMCP(
    name="my-resources-server",
    description="A simple server to demonstrate defining and accessing MCP Resources.",
    stateless_http=True
)

# --- Resource 1: A static, plain-text message ---
@mcp.resource(
    uri="app:///messages/welcome",
    name="Welcome Message",
    description="A static welcome message.",
    mime_type="text/plain"
)
async def get_welcome_message() -> str:
    """Provides a simple welcome string."""
    return "Hello and welcome to the MCP Resource Server!"

# --- Resource 2: A dynamic JSON object ---
@mcp.resource(
    uri="app:///system/time",
    name="Current Server Time",
    description="Provides the current UTC and local time of the server.",
    mime_type="application/json"
)
async def get_server_time() -> dict:
    """Provides the current server time as a JSON object."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_pakistan = now_utc.astimezone(ZoneInfo("Asia/Karachi"))
    return {
        "iso_timestamp": now_utc.isoformat(),
        "unix_epoch": now_utc.timestamp(),
        "local_time": now_pakistan.isoformat()
    }

# --- Resource 3: A resource template for dynamic user data ---
@mcp.resource(
    uri="users://{user_id}/profile",
    name="User Profile",
    description="A template for fetching a user's profile by their ID.",
    mime_type="text/plain"  # The output of our function is a plain string
)
def get_user_profile(user_id: str) -> str:
    """Returns a simple profile string for a given user ID."""
    return f"Profile for User ID: {user_id}. This is a dynamically generated resource."

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()