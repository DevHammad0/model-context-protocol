import asyncio

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def fetch_all_tools(session: ClientSession):
    """
    Fetches all tools from the server by following the pagination cursors.
    """
    print("\n--- Fetching all tools (paginated) ---")
    all_tools = []
    next_cursor: str | None = None
    page_num = 1

    while True:
        print(f"📄 Fetching page {page_num} (cursor: {next_cursor or 'None'})...")
        response = await session.list_tools(cursor=next_cursor)

        # Format the response cleanly
        page_tools = response.tools
        all_tools.extend(page_tools)
        
        print(f"✅ Received {len(page_tools)} tools:")
        for i, tool in enumerate(page_tools, 1):
            print(f"   {i:2d}. {tool.name} - {tool.description}")
        
        print(f"📊 Total tools fetched so far: {len(all_tools)}")
        
        if response.nextCursor:
            print(f"➡️  Next cursor: {response.nextCursor}")
        else:
            print("🏁 No more pages available.")

        if not response.nextCursor:
            break

        next_cursor = response.nextCursor
        page_num += 1
        # Small delay to make the demo easier to follow
        await asyncio.sleep(0.5)
        print()  # Add spacing between pages

    print("--- All tools fetched ---")
    print(f"🎉 Total: {len(all_tools)} tools across {page_num} pages")
    return all_tools


async def main():
    """
    Main client function to demonstrate pagination.
    """
    print("🚀 Starting MCP Pagination Client Demo...")
    server_url = "http://localhost:8000/mcp/"

    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server.")
                await session.initialize()
                print("✅ Initialized session.")
                await fetch_all_tools(session)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("   Is the pagination server running?")

    print("\n🏁 Demo finished.")


if __name__ == "__main__":
    asyncio.run(main())