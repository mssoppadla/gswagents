# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import contextlib
import os

import fastapi
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

try:
    from azure.ai.projects.telemetry import AIProjectInstrumentor
except ImportError:
    AIProjectInstrumentor = None

from src import logging_config
from src.util import get_env_file_path
from src.api.routers import tenants, guest, chat

logger = None
enable_trace = False
env_file = None


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    agent_version_obj = None
    proj_endpoint = os.environ.get("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    agent_id = os.environ.get("AZURE_EXISTING_AGENT_ID")

    try:
        async with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=proj_endpoint, credential=credential) as project_client,
        ):
            logger.info("Created AIProjectClient")

            if enable_trace:
                try:
                    connection_string = await project_client.telemetry.get_application_insights_connection_string()
                    if connection_string:
                        from azure.monitor.opentelemetry import configure_azure_monitor
                        configure_azure_monitor(connection_string=connection_string)
                        if AIProjectInstrumentor:
                            AIProjectInstrumentor().instrument(True)
                        app.state.application_insights_connection_string = connection_string
                        logger.info("Configured Application Insights for tracing.")
                except Exception as e:
                    logger.error(f"Failed to configure tracing: {e}", exc_info=True)

            if agent_id:
                if agent_id.count(":") != 1:
                    raise RuntimeError("AZURE_EXISTING_AGENT_ID must be in format 'agent_name:agent_version'")
                agent_name, agent_version = agent_id.split(":")
                try:
                    agent_version_obj = await project_client.agents.get_version(agent_name, agent_version)
                    logger.info(f"Fetched agent, agent ID: {agent_version_obj.id}")
                except Exception as e:
                    logger.error(f"Error fetching agent: {e}", exc_info=True)

            if not agent_version_obj:
                raise RuntimeError("Failed to fetch agent. Ensure qunicorn.py created one or set AZURE_EXISTING_AGENT_ID.")

            app.state.ai_project = project_client
            app.state.agent_version_obj = agent_version_obj
            yield

    finally:
        logger.info("Closed AIProjectClient")


# Create the FastAPI app
app = fastapi.FastAPI(lifespan=lifespan)

# Configure logging and environment
logger = logging_config.configure_logging(os.getenv("APP_LOG_FILE", ""))
env_file = get_env_file_path()
load_dotenv(env_file)

# Enable CORS (fixes Swagger "Failed to fetch")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
directory = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=directory), name="static")

# Routers
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(guest.router, prefix="/guest", tags=["guest"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

# Health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
