import json
import logging
from collections.abc import AsyncGenerator
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.pregel import Pregel
from baymax_team_collab.conversation_agent import create_conversation_graph
from baymax_team_collab.conversation_agent import initialize_state

from baymax_team_collab.server.settings import settings

from baymax_team_collab.server.schema import StreamInput

from baymax_team_collab.server.util import (
    convert_message_content_to_string,
    langchain_to_chat_message,
)



# Create a singleton conversation graph that will be reused across requests
CONVERSATION_GRAPH = create_conversation_graph()

def verify_bearer(
    http_auth: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(
            HTTPBearer(
                description="Please provide AUTH_SECRET api key.", auto_error=False
            )
        ),
    ],
) -> None:
    if not settings.AUTH_SECRET:
        return
    auth_secret = settings.AUTH_SECRET.get_secret_value()
    if not http_auth or http_auth.credentials != auth_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(dependencies=[Depends(verify_bearer)])


def _format_sse_message(msg_type: str, content: Any) -> str:
    """Format a message for Server-Sent Events (SSE)."""
    return f"data: {json.dumps({'type': msg_type, 'content': content})}\n\n"


async def _process_updates_event(
    event: dict, user_input: StreamInput, run_id: UUID
) -> AsyncGenerator[str, None]:
    """Process node completion events."""
    new_messages = []

    for node, updates in event.items():
        updates = updates or {}
        update_messages = updates.get("messages", [])

        new_messages.extend(update_messages)

    # Convert and yield messages
    for message in new_messages:
        try:
            chat_message = langchain_to_chat_message(message)
            chat_message.run_id = str(run_id)

         
            if (
                chat_message.type == "human"
                and chat_message.content == user_input.message
            ):
                continue

            # Log tool calls for debugging
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Tool calls: {message.tool_calls}")

            yield _format_sse_message("message", chat_message.model_dump())
        except Exception as e:
            print(f"Error parsing message: {e}")
            yield _format_sse_message("error", "Unexpected error")


async def _process_token_event(event: tuple) -> AsyncGenerator[str, None]:
    """Process token streaming events."""
    msg, metadata = event

    # Skip if tagged to skip streaming
    if "skip_stream" in metadata.get("tags", []):
        return

    # Process only AIMessageChunks (token streaming)
    if not isinstance(msg, AIMessageChunk):
        return

    # yield _format_sse_message("token", msg.content.__str__())

    if msg.content:
        yield _format_sse_message(
            "token", convert_message_content_to_string(msg.content)
        )


def get_kwargs_and_run_id(user_input: StreamInput) -> tuple[dict[str, Any], UUID]:
    run_id = uuid4()
    
    # Always have a thread_id
    thread_id = user_input.thread_id or str(uuid4())
    configurable = {"thread_id": thread_id}
    
    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )
    
    # Create input with the user message
    input_message = HumanMessage(content=user_input.message)
    
    print(f"Checking for existing state for thread: {thread_id}")
    try:
        # Try to load the last state from the checkpointer
        last_state = CONVERSATION_GRAPH.get_state({"configurable": configurable})
        
        if last_state and last_state.values:
            # Extract some info about the state to log
            num_messages = len(last_state.values.get("chat_history", [])) if "chat_history" in last_state.values else 0
            
            # State found - use it and just add the new user message
            print(f"✅ FOUND EXISTING STATE for thread {thread_id} with {num_messages} messages")

            print("-"*30)
            print("last_state.values = ",last_state.values)
            print("-" * 30)

            # Just add the new user input
            input = {
                "user_input": user_input.message,
                "chat_history": [input_message]
            }
            return {"input": input, "config": config}, run_id
        else:
            print(f"❌ NO STATE DATA found for thread {thread_id} - state object exists but is empty")
    except Exception as e:
        print(f"❌ NO EXISTING STATE found for thread {thread_id}: {str(e)}")
    
    # No existing state found - initialize new state
    print(f"🆕 Creating NEW conversation state for thread {thread_id}")
    state = initialize_state(configurable=configurable)
    state["user_input"] = user_input.message
    
    input = {
        "chat_history": [input_message],
        **state
    }
    
    return {"input": input, "config": config}, run_id


async def message_generator(user_input: StreamInput) -> AsyncGenerator[str, None]:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    agent: Pregel = CONVERSATION_GRAPH
    kwargs, run_id = get_kwargs_and_run_id(user_input)

    try:
        print(f"Starting stream with run_id: {run_id}")
        print(f"Using thread_id from client: {user_input.thread_id}")

        async for stream_event in agent.astream(
            **kwargs, stream_mode=["updates", "messages"]
        ):
            if not isinstance(stream_event, tuple):
                print(f"Unexpected stream_event type: {type(stream_event)}")
                continue

            stream_mode, event = stream_event
            

            # Process different event types
            if stream_mode == "updates":
                async for msg in _process_updates_event(event, user_input, run_id):
                    yield msg

            elif stream_mode == "messages" and user_input.stream_tokens:
                # Handle token streaming
                async for msg in _process_token_event(event):
                    yield msg

            else:
                print(f"Unhandled stream mode: {stream_mode}")

    except Exception as e:
        print(f"Error in message generator: {e}", exc_info=True)
        yield _format_sse_message("error", "Internal server error")
    finally:
        yield "data: [DONE]\n\n"


def _sse_response_example() -> dict[int | str, Any]:
    return {
        status.HTTP_200_OK: {
            "description": "Server Sent Event Response",
            "content": {
                "text/event-stream": {
                    "example": "data: {'type': 'token', 'content': 'Hello'}\n\ndata: {'type': 'token', 'content': ' World'}\n\ndata: [DONE]\n\n",
                    "schema": {"type": "string"},
                }
            },
        }
    }








@router.post(
    "/stream", response_class=StreamingResponse, responses=_sse_response_example()
)
async def stream(user_input: StreamInput) -> StreamingResponse:
    """
    Stream an agent's response to a user input, including intermediate messages and tokens.
    Use thread_id to persist and continue a multi-turn conversation.
    Set `stream_tokens=false` to return intermediate messages but not token-by-token.
    """

    print("user_input", user_input)
    return StreamingResponse(
        message_generator(user_input),
        media_type="text/event-stream",
    )


app.include_router(router)
