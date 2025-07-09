import asyncio
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CreateMessageRequestParams, CreateMessageResult, ErrorData, TextContent
from mcp.shared.context import RequestContext


async def mock_sampler(context: RequestContext["ClientSession", Any], params: CreateMessageRequestParams) -> CreateMessageResult | ErrorData:
    """A mock LLM handler that gets called by the ClientSession when the server sends a 'sampling/create' request."""

    print("<- Client: Received 'sampling/create' request from server.")

    print(f"<- Client Parameters '{params}'.")
    print(f"<- Client Context '{context}'.")

    # Extract the message content to determine the type of request
    if params.messages and len(params.messages) > 0:
        message_content = params.messages[0].content.text if hasattr(params.messages[0].content, 'text') else str(params.messages[0].content)
        
        print(f"-> Server Parameters Message Content Recieved: '{message_content}'.")
        
        # Check if this is a summarization request
        if "Summarize this document" in message_content:
            mock_llm_response = (
                "• The document discusses key concepts and implementation strategies for software development\n"
                "• It covers best practices for code organization, testing, and deployment workflows\n"
                "• The content emphasizes the importance of documentation and maintainable architecture"
            )
            print("-> Client: Sending mock summary back to the server.")
        else:
            # Default to story generation
            mock_llm_response = (
                f"In a world of shimmering code, a brave little function set out to find the legendary Golden Bug. "
                f"It traversed treacherous loops and navigated complex conditionals. "
                f"Finally, it found not a bug, but a feature, more valuable than any treasure."
            )
            print("-> Client: Sending mock story back to the server.")
    else:
        # Fallback response
        mock_llm_response = "Unable to process the request due to missing message content."
        print("-> Client: Sending fallback response to the server.")

    # Respond with a dictionary that matches the expected structure
    return CreateMessageResult(
        role="assistant",
        content=TextContent(text=mock_llm_response, type="text"),
        model="openai/gpt-4o-mini",
    )

async def main():
    """A simple client to demonstrate receiving MCP logging notifications."""
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, get_session_id):
            async with ClientSession(read_stream, write_stream, sampling_callback=mock_sampler) as session:
                print("✅ Connected. Initializing session...")
                await session.initialize()
                print("🛠️ Session initialized.")

                # Call the create_story tool
                story_topic = "a function's adventure"
                print(f"-> Client: Calling 'create_story' tool with topic: '{story_topic}'")

                story_result = await session.call_tool("create_story", {"topic": story_topic})

                print("-" * 50)
                print(f"🎉 Final Story Received from Server:")
                if story_result:
                    print(f"'{story_result.content[0].text}'")
                else:
                    print("No content received from server.")

                print("\n" + "=" * 50)
                
                # Call the summarize_document tool
                sample_document = """
                The Model Context Protocol (MCP) is a groundbreaking framework that enables seamless integration between AI applications and external data sources. It provides a standardized way for language models to access real-time information, execute tools, and maintain context across different systems.

                Key features include bidirectional communication, secure data access, and extensible architecture. MCP supports various transport mechanisms and allows for both local and remote server connections. The protocol emphasizes security through controlled access patterns and user approval workflows.

                Implementation involves setting up servers that expose capabilities like tools, resources, and sampling, while clients manage the connection and facilitate communication with language models. This architecture enables powerful AI assistants that can interact with live data and perform complex tasks across multiple systems.
                """
                
                print(f"-> Client: Calling 'summarize_document' tool with sample document...")

                summary_result = await session.call_tool("summarize_document", {"text": sample_document})

                print("-" * 50)
                print(f"🎉 Final Summary Received from Server:")
                if summary_result:
                    print(f"'{summary_result.content[0].text}'")
                else:
                    print("No content received from server.")

                print("\n✅ Demo complete!")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Make sure the server is running.")

    print("\n🎉 Demo finished.")

if __name__ == "__main__":
    asyncio.run(main())