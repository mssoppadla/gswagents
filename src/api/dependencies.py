import logging
from fastapi import Request, HTTPException
from agent_framework import ChatAgent

def get_agent(request: Request) -> ChatAgent:
    project_client = getattr(request.app.state, "project_client", None)
    agent_id = getattr(request.app.state, "agent_id", None)

    if not project_client or not agent_id:
        logging.error("ChatAgent not bound to app.state")
        raise HTTPException(status_code=500, detail="ChatAgent not initialized")

    return ChatAgent(project_client=project_client, agent_id=agent_id)



# from fastapi import Request
# from agent_framework import ChatAgent
# import logging

# def get_agent(request: Request) -> ChatAgent:
#     agent = getattr(request.app.state, "agent", None)
#     if agent is None:
#         logging.info("ChatAgent not bound to app.state")
#         raise RuntimeError("ChatAgent not bound to app.state")
#     logging.info("ChatAgent bound to app.state")
#     logging.info(f"ChatAgent not bound to app.state: {agent.id}")
#     return agent




# from fastapi import Request, Depends
# from agent_framework import ChatAgent

# def get_agent(request: Request) -> ChatAgent:
#     agent = getattr(request.app.state, "agent", None)
#     if agent is None:
#         raise RuntimeError("ChatAgent not bound to app.state")
#     return agent
