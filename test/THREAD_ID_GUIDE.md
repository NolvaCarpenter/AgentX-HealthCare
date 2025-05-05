# Using Thread IDs with LangGraph

This document explains how to effectively use thread IDs with LangGraph in the BayMax project.

## Best Practices

When working with conversation threads in LangGraph, follow these guidelines:

### 1. Setting the Thread ID

There are three ways to set a thread ID (in order of preference):

1. **In LangGraph Configuration**:
   ```python
   config = {"configurable": {"thread_id": "your-thread-id"}}
   output = graph.invoke(state, config)
   ```

2. **In State Object**:
   ```python
   state["thread_id"] = "your-thread-id" 
   output = graph.invoke(state)
   ```

3. **In Module-Level Config**:
   ```python
   from conversation_agent import config
   config["configurable"]["thread_id"] = "your-thread-id"
   ```

For maximum reliability, use all three methods together.

### 2. Creating a New Thread

To create a new conversation thread:

```python
from conversation_thread import create_new_thread
thread_id = create_new_thread(user_id="default_user")
```

Then use this thread_id in your LangGraph configuration.

### 3. Continuing a Thread

To continue an existing thread:

```python
# Get the existing thread_id
thread_id = "existing-thread-id"

# Set up configuration
config = {"configurable": {"thread_id": thread_id}}

# Update the state with new user input
state["user_input"] = "New user message"
state["thread_id"] = thread_id

# Invoke the graph
output = graph.invoke(state, config)
```

### 4. Accessing Thread History

To access the messages in a thread:

```python
from conversation_thread import get_thread_history
messages = get_thread_history(thread_id)

# Display messages
for message in messages:
    print(f"{message['role']}: {message['content']}")
```

## Example Files

The following files demonstrate thread ID usage:

1. `langgraph_thread_direct.py` - Simple direct usage of thread_id
2. `thread_approach.py` - Comprehensive approach with best practices
3. `direct_langgraph_invoke.py` - Example with detailed logging

## Common Issues & Troubleshooting

### Thread ID Not Persisting
- Ensure you're setting the thread ID in both the state and config object
- Also update the module-level config variable (`conversation_agent.config`)
- Verify that `initialize_state` is receiving the configurable parameter

### Missing Messages
- Check if messages are being saved to the database with `save_message()`
- Verify the thread ID is valid and exists in the database
- Use `get_thread_history(thread_id)` to check what's actually stored

### Multiple Threads Created
- Always check for an existing thread before creating a new one
- Consider using a thread manager singleton to control thread creation

### State Initialization Issues
- Always use the `initialize_state()` function to create your state
- Never manually create a state dictionary with missing or None values
- If using a custom thread ID, pass it as: `initialize_state(configurable={"thread_id": your_thread_id})`

### Debugging Thread ID Issues
You can add this code to inspect thread ID at different steps:

```python
def debug_thread_id(state, config, where="unknown"):
    thread_id_state = state.get("thread_id", "NOT_FOUND")
    thread_id_config = config.get("configurable", {}).get("thread_id", "NOT_FOUND")
    print(f"[DEBUG {where}] Thread ID in state: {thread_id_state}")
    print(f"[DEBUG {where}] Thread ID in config: {thread_id_config}")
```
