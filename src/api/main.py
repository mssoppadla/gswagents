# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
#src/api/main.py

import os
import contextlib
import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from src import logging_config
from src.util import get_env_file_path
from src.api.routers import tenants, guest, chat, knowledge
from azure.core.credentials import AzureKeyCredential
from azure.ai.agents import AgentsClient 


logger = None
env_file = None
# Logging and environment
logger = logging_config.configure_logging(os.getenv("APP_LOG_FILE", ""))
env_file = get_env_file_path()
load_dotenv(env_file)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    # Load from env
    project_endpoint = "https://xservnamechtagent.services.ai.azure.com/api/projects/xprojnamechtagent"# os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT", "").strip()
    api_key =os.environ.get("AZURE_AI_API_KEY", "").strip()  


    agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=AzureKeyCredential(api_key)
    )

    # List agents
    agents = agents_client.list_agents()
    for agent in agents:
        print(agent.id, agent.name)

    if not agents:
        raise RuntimeError("No agents found in project. Please create one in Foundry.")
    agent_id = agents[0].id  # or filter by name/instructions if needed

    # Create chat client (data plane)
    chat_client = AzureAIAgentClient(
        project_endpoint=project_endpoint,
        agent_id=agent_id,
        credential=AzureKeyCredential(api_key)
    )

    # Create ChatAgent
    async with ChatAgent(chat_client=chat_client) as agent_instance:
        app.state.agent = agent_instance
        yield

# Create FastAPI app
app = fastapi.FastAPI(title="Runtime Chat API", lifespan=lifespan)



# CORS for Swagger and frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (ensure directory exists)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routers
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(guest.router, prefix="/guest", tags=["guest"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])

# Health check
@app.get("/healthz", tags=["ops"])
async def healthz():
    return {"status": "ok"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
