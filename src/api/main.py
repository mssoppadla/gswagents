# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
# src/api/main.py

import os
import contextlib
import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agent_framework import ChatAgent
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
        agent_id=agent.id,
        credential=DefaultAzureCredential()
    )

    async with ChatAgent(chat_client=chat_client) as agent_instance:
        app.state.agent = agent_instance
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})






## working just chat integration with Azure AI Projects SDK
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

# openai_client = project_client.get_openai_client()

# # Reference the agent to get a response
# response = openai_client.responses.create(
#     input=[{"role": "user", "content": "Tell me what you can help with."}],
#     extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
# )

# print(f"Response output: {response.output_text}")




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

# # Logging and environment
# logger = logging_config.configure_logging(os.getenv("APP_LOG_FILE", ""))
# env_file = get_env_file_path()
# load_dotenv(env_file)

# # Project endpoint
# PROJECT_ENDPOINT = "https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent"
# #AGENT_NAME = "agent-template-assistant"


# @contextlib.asynccontextmanager
# async def lifespan(app: fastapi.FastAPI):
#     """
#     Application lifespan: initialize Azure AI Project client and ChatAgent.
#     """
#     # Initialize AIProjectClient with MSI/DefaultAzureCredential
#     project_client = AIProjectClient(
#         endpoint=PROJECT_ENDPOINT,
#         credential=DefaultAzureCredential(),
#     )

#     # Retrieve agent by name
#     agent = project_client.agents.get(agent_name=AGENT_NAME)
#     logger.info(f"Retrieved agent: {agent.name}")

#     # Create OpenAI client bound to project
#     openai_client = project_client.get_openai_client()

#     # Quick test call (optional, can remove in prod)
#     response = openai_client.responses.create(
#         input=[{"role": "user", "content": "Tell me what you can help with."}],
#         extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
#     )
#     logger.info(f"Agent response: {response.output_text}")

#     # Create ChatAgent (data plane client)
#     chat_client = AzureAIAgentClient(
#         project_endpoint=PROJECT_ENDPOINT,
#         agent_id=agent.id,
#         credential=DefaultAzureCredential()
#     )

#     async with ChatAgent(chat_client=chat_client) as agent_instance:
#         app.state.agent = agent_instance
#         yield


# # Create FastAPI app
# app = fastapi.FastAPI(title="Runtime Chat API", lifespan=lifespan)

# # CORS for Swagger and frontends
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten to your frontend domains in prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Static files (ensure directory exists)
# static_dir = os.path.join(os.path.dirname(__file__), "static")
# if os.path.isdir(static_dir):
#     app.mount("/static", StaticFiles(directory=static_dir), name="static")

# # Routers
# app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
# app.include_router(guest.router, prefix="/guest", tags=["guest"])
# app.include_router(chat.router, prefix="/chat", tags=["chat"])
# app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# # Health check
# @app.get("/healthz", tags=["ops"])
# async def healthz():
#     return {"status": "ok"}

# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error("Unhandled exception occurred", exc_info=exc)
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"})
