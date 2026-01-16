# Multi-User Web App Example

Build a multi-user web application where each user gets isolated storage and execution.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web UI (templates/)                      │
├─────────────────────────────────────────────────────────────┤
│                      FastAPI Server                         │
├─────────────────────────────────────────────────────────────┤
│                    SessionManager                           │
├───────────────┬───────────────┬───────────────┬────────────┤
│ DockerSandbox │ DockerSandbox │ DockerSandbox │    ...     │
│   (User A)    │   (User B)    │   (User C)    │            │
└───────────────┴───────────────┴───────────────┴────────────┘
```

## SessionManager

```python
from pydantic_ai_backends import SessionManager

# Create manager
manager = SessionManager(
    image="python:3.12-slim",
    workspace_root="/app/workspaces",  # Persistent storage
    auto_remove=True,
)

# Create session for user
session_id = manager.create_session(user_id="alice")

# Get sandbox for session
sandbox = manager.get_session(session_id)

# User operations are isolated
sandbox.write("/workspace/secret.txt", "Alice's private data")
sandbox.execute("python script.py")

# End session (removes container)
manager.end_session(session_id)
```

## FastAPI Server

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai_backends import SessionManager, DockerSandbox, create_console_toolset

# Session manager
session_manager: SessionManager | None = None

@asynccontextmanager
async def lifespan(app):
    global session_manager
    session_manager = SessionManager(
        image="python:3.12-slim",
        workspace_root="/tmp/workspaces",
    )
    yield
    # Cleanup on shutdown
    for sid in list(session_manager._sandboxes.keys()):
        session_manager.end_session(sid)

app = FastAPI(lifespan=lifespan)

# Agent setup
@dataclass
class UserDeps:
    backend: DockerSandbox
    user_id: str

toolset = create_console_toolset()
agent = Agent("openai:gpt-4o", deps_type=UserDeps).with_toolset(toolset)

# Request models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Endpoints
@app.post("/sessions")
async def create_session(user_id: str | None = None):
    session_id = session_manager.create_session(user_id=user_id)
    return {"session_id": session_id}

@app.post("/sessions/{session_id}/chat")
async def chat(session_id: str, request: ChatRequest):
    try:
        sandbox = session_manager.get_session(session_id)
    except ValueError:
        raise HTTPException(404, "Session not found")

    deps = UserDeps(backend=sandbox, user_id=session_id)
    result = await agent.run(request.message, deps=deps)

    return ChatResponse(response=result.output, session_id=session_id)

@app.delete("/sessions/{session_id}")
async def end_session(session_id: str):
    session_manager.end_session(session_id)
    return {"message": "Session ended"}

@app.get("/sessions/{session_id}/files")
async def list_files(session_id: str, path: str = "."):
    sandbox = session_manager.get_session(session_id)
    return {"files": sandbox.ls_info(path)}
```

## Client Usage

```python
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create session
        r = await client.post("/sessions", params={"user_id": "alice"})
        session_id = r.json()["session_id"]

        # Chat with AI
        r = await client.post(
            f"/sessions/{session_id}/chat",
            json={"message": "Create a hello world script and run it"}
        )
        print(r.json()["response"])

        # List files
        r = await client.get(f"/sessions/{session_id}/files")
        print(r.json()["files"])

        # Cleanup
        await client.delete(f"/sessions/{session_id}")
```

## Security Features

- **User Isolation**: Each user's container is separate
- **No Cross-Access**: Users cannot see other users' files
- **Persistent Storage**: Files stored on host, mounted into containers
- **Automatic Cleanup**: Containers removed when sessions end

## Full Example

See [`examples/web_production/`](https://github.com/vstorm-co/pydantic-ai-backend/tree/main/examples/web_production) for a complete implementation with:

- FastAPI server
- HTML/JS frontend
- Session management
- AI chat integration

```bash
cd examples/web_production
pip install pydantic-ai-backend[docker] fastapi uvicorn pydantic-ai jinja2
python server.py
# Open http://localhost:8000
```
