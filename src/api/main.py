import os
import contextlib
import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agent_framework import ChatAgent, ChatMessage
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from src import logging_config
from src.util import get_env_file_path
from src.api.routers import tenants, guest, chat, knowledge

logger = logging_config.configure_logging(os.getenv("APP_LOG_FILE", ""))
env_file = get_env_file_path()
load_dotenv(env_file)

PROJECT_ENDPOINT = "https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent"
AGENT_NAME = "agent-template-assistant"

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    agent = project_client.agents.get(agent_name=AGENT_NAME)
    logger.info(f"Retrieved agent: {agent.name}")

    chat_client = AzureAIAgentClient(
        project_endpoint=PROJECT_ENDPOINT,
        agent_id="asst_LdDoxHftok2KTvKi29JUjd6t",
        credential=DefaultAzureCredential()
    )

    async with ChatAgent(chat_client=chat_client) as agent_instance:
        app.state.agent = agent_instance

        # Startup test call
        messages = [ChatMessage(role="user", content="Hello, what can you do?")]
        async for update in agent_instance.run_stream(messages):
            logger.info(f"Agent test response: {update.text}")

        yield


app = fastapi.FastAPI(title="Runtime Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(guest.router, prefix="/guest", tags=["guest"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])


@app.get("/healthz", tags=["ops"])
async def healthz():
    return {"status": "ok"}

@app.get("/test-agent", tags=["ops"])
async def test_agent():
    agent_instance = app.state.agent
    messages = [ChatMessage(role="user", content="Which day does next year's Christmas fall on?")]
    result = []
    async for update in agent_instance.run_stream(messages):
        result.append(update.text)
    return {"response": " ".join(result)}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# #data Plane SDK chat integration with Azure AI Projects SDK

# from azure.ai.agents import AgentsClient
# from azure.identity import DefaultAzureCredential

# agents_client = AgentsClient(
#     endpoint="https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent",
#     credential=DefaultAzureCredential()
# )

# agents = agents_client.list_agents()
# print("number of Agents in the project are :" , len(list(agents)))

# for agent in agents:
#     print(agent.id, agent.name)



 #control plane SDK:
# # working just chat integration with Azure AI Projects SDK
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient

# myEndpoint = "https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent"

# project_client = AIProjectClient(
#     endpoint=myEndpoint,
#     credential=DefaultAzureCredential(),
# )

# myAgent = "agent-template-assistant"
# # Get an existing agent
# agent = project_client.agents.get(agent_name=myAgent)
# print(f"Retrieved agent: {agent.name}")
# print(f"Retrieved id: {agent.id}")
# openai_client = project_client.get_openai_client()

# # Reference the agent to get a response
# response = openai_client.responses.create(
#     input=[{"role": "user", "content": "Tell me what you can help with."}],
#     extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
# )

# print(f"Response output: {response.output_text}")



# #Actual working copy . this is a backup of working copy
# # Copyright (c) Microsoft. All rights reserved.
# # Licensed under the MIT license.
# # src/api/main.py

# import os
# import contextlib
# import fastapi
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv

# from agent_framework import ChatAgent
# from agent_framework.azure import AzureAIAgentClient
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient

# from src import logging_config
# from src.util import get_env_file_path
# from src.api.routers import tenants, guest, chat, knowledge

# logger = logging_config.configure_logging(os.getenv("APP_LOG_FILE", ""))
# env_file = get_env_file_path()
# load_dotenv(env_file)

# PROJECT_ENDPOINT = "https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent"
# AGENT_NAME = "agent-template-assistant"

# @contextlib.asynccontextmanager
# async def lifespan(app: fastapi.FastAPI):
#     project_client = AIProjectClient(
#         endpoint=PROJECT_ENDPOINT,
#         credential=DefaultAzureCredential(),
#     )
#     agent = project_client.agents.get(agent_name=AGENT_NAME)
#     logger.info(f"Retrieved agent: {agent.name}")

#     chat_client = AzureAIAgentClient(
#         project_endpoint=PROJECT_ENDPOINT,
#         agent_id="asst_LdDoxHftok2KTvKi29JUjd6t",
#         credential=DefaultAzureCredential()
#     )

    

#     async with ChatAgent(chat_client=chat_client) as agent_instance:
#         app.state.agent = agent_instance
#         yield

# app = fastapi.FastAPI(title="Runtime Chat API", lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# static_dir = os.path.join(os.path.dirname(__file__), "static")
# if os.path.isdir(static_dir):
#     app.mount("/static", StaticFiles(directory=static_dir), name="static")

# app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
# app.include_router(guest.router, prefix="/guest", tags=["guest"])
# app.include_router(chat.router, prefix="/chat", tags=["chat"])
# app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# @app.get("/healthz", tags=["ops"])
# async def healthz():
#     return {"status": "ok"}

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error("Unhandled exception occurred", exc_info=exc)
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"})

