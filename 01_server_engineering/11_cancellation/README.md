# Cancellation in Model Context Protocol (MCP)

This README provides a clear, concise guide to understanding and implementing request cancellation in MCP. It’s designed to be easy to follow even if you’re new to the protocol.

---

## Table of Contents

- [Cancellation in Model Context Protocol (MCP)](#cancellation-in-model-context-protocol-mcp)
  - [Table of Contents](#table-of-contents)
  - [What Is Cancellation?](#what-is-cancellation)
  - [Why It Matters](#why-it-matters)
  - [Cancellation Flow](#cancellation-flow)
  - [Key Protocol Rules](#key-protocol-rules)
  - [Implementing in FastMCP (Python)](#implementing-in-fastmcp-python)
  - [Best Practices](#best-practices)
  - [Common Pitfalls](#common-pitfalls)

---

## What Is Cancellation?

* **Definition:** An MCP cancellation is a one-way notification that tells the receiver to stop working on a specific in-progress request.
* **Mechanism:** Uses a JSON-RPC notification (`notifications/cancelled`) carrying the original request ID and optional reason.

---

## Why It Matters

1. **User Experience:** Lets users abort long-running tasks (e.g., big file processing) without waiting.
2. **Resource Management:** Frees up CPU, memory, and I/O tied to abandoned operations.
3. **Robustness:** Handles race conditions where cancellation arrives just after completion.

---

## Cancellation Flow

1. **Capture the Request ID:** Note the `id` before sending the request.

   ```json
   { "jsonrpc": "2.0", "id": "123", "method": "tools/call", "params": { … } }
   ```
2. **Send the Request:** Invoke your long-running operation.
3. **Send Cancellation Notification:** At any time, notify the other side:

   ```json
   {
     "jsonrpc": "2.0",
     "method": "notifications/cancelled",
     "params": {
       "requestId": "123",
       "reason": "User clicked Stop"
     }
   }
   ```
4. **Receiver Behavior:**

   * **Should** stop processing if still active.
   * **Must not** send a normal response for the cancelled `id`.
   * **May** ignore if the request is unknown or already completed.

---

## Key Protocol Rules

* **Same Direction:** Can only cancel requests you originally sent (client→server or server→client).
* **Non-cancellable `initialize`:** The initial handshake cannot be cancelled.
* **No Duplicate Responses:** Once cancelled, do not reply to the original request.
* **Graceful Ignoring:** Late or invalid cancellations are simply dropped.

---

## Implementing in FastMCP (Python)

Here’s a minimal example showing how FastMCP handles cancellation via `asyncio.CancelledError`:

```python
import asyncio
from mcp.server.fastmcp import FastMCP, Context

app = FastMCP("CancelDemo")

@app.tool()
async def long_task(ctx: Context, duration: int = 10) -> str:
    await ctx.info(f"Start processing (ID: {ctx.request_id})")
    try:
        for i in range(duration):
            # Cancellation checkpoint
            await asyncio.sleep(1)
            await ctx.debug(f"Step {i+1}/{duration}")
        return "Task completed!"
    except asyncio.CancelledError:
        await ctx.warning("Task was cancelled by client")
        # Re-raise to send a -32800 error response
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app.streamable_http_app(), host="0.0.0.0", port=8000)
```

**How It Works:**

1. FastMCP tracks each task by its request ID.
2. On `notifications/cancelled`, it injects `CancelledError` into the matching `asyncio.Task`.
3. Your `except` block handles cleanup and re-raises to signal cancellation.

---

## Best Practices

* **Log Reasons:** Surface the optional `reason` for debugging or UI messages.
* **Resource Cleanup:** Always close files, DB connections, etc., in your cancellation handler.
* **User Feedback:** Update UIs to show a “Cancelling…” state.

---

## Common Pitfalls

* **Forgetting Checkpoints:** Missing Pauses: If your code runs without any `await`, it never checks for cancellation signals.
* **Sending a Response After Cancel:** Violates protocol—don’t reply to a cancelled `id`.
* **Cancelling the Wrong Direction:** Only send a cancel notice for calls you started yourself.

---

That’s it! You now have everything you need to add robust, user-friendly cancellation to your MCP-based services.
