from fastapi import Request, Depends
from agent_framework import ChatAgent

def get_agent(request: Request) -> ChatAgent:
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        raise RuntimeError("ChatAgent not bound to app.state")
    return agent
