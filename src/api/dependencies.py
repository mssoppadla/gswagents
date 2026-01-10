import logging
from fastapi import Request, HTTPException
from src.api.core.foundryagent import run_agent_task
import json

class FoundryChatAgent:
    """
    Wrapper so endpoints can call .run() or .run_stream()
    """
    def __init__(self, project_client, agent_id):
        self.project_client = project_client
        self.agent_id = agent_id

    async def run(self, message: str, org_id: str, thread_id: str = None):
        result = await run_agent_task(
            business_tenant_id=org_id,
            org_id=org_id,
            domain="chat",
            instructions="Respond conversationally.",
            description="General assistant",
            task=message,
            thread_id=thread_id
        )
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        return result

    async def run_stream(self, message: str, org_id: str, thread_id: str = None):
        result = await self.run(message, org_id, thread_id=thread_id)
        # yield the whole dict so frontend can JSON.parse it
        yield json.dumps(result)

    # working memoryless agent.
    # async def run_stream(self, message: str, org_id: str, thread_id: str = None):
    #     result = await self.run(message, org_id, thread_id=thread_id)
    #     yield result.get("response", "")

def get_agent(request: Request) -> FoundryChatAgent:
    project_client = getattr(request.app.state, "project_client", None)
    agent_id = getattr(request.app.state, "agent_id", None)

    if not project_client or not agent_id:
        logging.error("Agent not bound to app.state")
        raise HTTPException(status_code=500, detail="Agent not initialized")
    logging.error(f"Agent is bound to app.state : {agent_id}")
    return FoundryChatAgent(project_client=project_client, agent_id=agent_id)

#Working memoryless agent.
# #src/api/dependencies.py
# import logging
# from fastapi import Request, HTTPException
# from src.api.core.foundryagent import run_agent_task

# class FoundryChatAgent:
#     """
#     Lightweight wrapper so endpoints can call .run() or .run_stream()
#     but internally it delegates to run_agent_task.
#     """
#     def __init__(self, project_client, agent_id):
#         self.project_client = project_client
#         self.agent_id = agent_id

#     async def run(self, message: str, org_id: str):
#         result = await run_agent_task(
#             business_tenant_id=org_id,
#             org_id=org_id,
#             domain="chat",
#             instructions="Respond conversationally.",
#             description="General assistant",
#             task=message,
#             thread_id=None
#         )
#         if result.get("status") == "error":
#             raise HTTPException(status_code=500, detail=result.get("error"))
#         return result

#     async def run_stream(self, message: str, org_id: str):
#         # For now just yield the final response once
#         result = await self.run(message, org_id)
#         yield result.get("response", "")


# def get_agent(request: Request) -> FoundryChatAgent:
#     project_client = getattr(request.app.state, "project_client", None)
#     agent_id = getattr(request.app.state, "agent_id", None)

#     if not project_client or not agent_id:
#         logging.error("Agent not bound to app.state")
#         raise HTTPException(status_code=500, detail="Agent not initialized")
#     logging.error(f"Agent is bound to app.state : {agent_id}")
#     return FoundryChatAgent(project_client=project_client, agent_id=agent_id)
