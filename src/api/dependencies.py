from fastapi import Request
from agent_framework import ChatAgent

def get_agent(request: Request) -> ChatAgent:
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        logging.info("ChatAgent not bound to app.state")
        raise RuntimeError("ChatAgent not bound to app.state")
    logging.info("ChatAgent bound to app.state")
    logging.info(f"ChatAgent not bound to app.state: {agent.id}")
    return agent




# from fastapi import Request, Depends
# from agent_framework import ChatAgent

# def get_agent(request: Request) -> ChatAgent:
#     agent = getattr(request.app.state, "agent", None)
#     if agent is None:
#         raise RuntimeError("ChatAgent not bound to app.state")
#     return agent
