## Progress Notifications

When you start a long-running task, you can ask the server to send you updates on how far it’s come. Here’s how it works:

1. **Include a token**  
   In your request metadata, add a unique `progressToken` (any string).  
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "some_tool",
       "arguments": { /* your args */ },
       "_meta": {
         "progressToken": "myToken123"
       }
     }
   }
   ```

2. **Server sends updates**
   As the job runs, the server pushes notifications back to you:

   ```json
   {
     "jsonrpc": "2.0",
     "method": "notifications/progress",
     "params": {
       "progressToken": "myToken123",
       "progress": 30,
       "total": 100,
       "message": "30% done"
     }
   }
   ```

   * **progress**: how much is done so far
   * **total** (optional): full amount of work
   * **message** (optional): friendly status text

3. **Finish**

   * When `progress` reaches `total`, the server stops sending updates.
   * You’ll then receive the normal JSON-RPC response with the final result.

---

**Why use progress notifications?**

* Keeps you informed on long tasks
* Lets you show a progress bar or status messages
* Simple: just one extra field in your request and streaming notifications back on the same connection
