# src/api/main.py
import os
import sys
import contextlib
import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import AzureAppConfigurationKeyVaultOptions
from azure.ai.agents.models import ListSortOrder

from src.util import get_env_file_path
from src.api.routers import tenants, guest, chat, knowledge
from src.api.core import config as config_router

import logging



# --- Logging setup aligned with Uvicorn ---
logger = logging.getLogger("uvicorn.error")   # or "uvicorn.access"
logger.setLevel(logging.INFO)
logger.propagate = True


# --- Environment setup ---
env_file = get_env_file_path()
load_dotenv(env_file)

APP_CONFIG_ENDPOINT = "https://xappconfig.azconfig.io"
logger.info(f"App config endpoint is gent ID: {APP_CONFIG_ENDPOINT}")

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    async with DefaultAzureCredential() as credential:
        kv_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
        config = await load(
            endpoint=APP_CONFIG_ENDPOINT,
            credential=credential,
            key_vault_options=kv_options,
        )

        project_endpoint = config.get("azure-existing-aiproject-endpoint")
        agent_id = config.get("azure-existing-agent-id")

        logger.info(f"[API startup] Project endpoint: {project_endpoint}")
        logger.info(f"[API startup] Agent ID: {agent_id}")

        async with AIProjectClient(credential=credential, endpoint=project_endpoint) as project:
            app.state.project_client = project
            app.state.agent_id = agent_id

            # Startup test aligned with foundryagent.py
            try:
                thread = await project.agents.threads.create(metadata={"startup": "true"})
                await project.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content="Hello, what can you do?"
                )
                run = await project.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent_id
                )
                logger.info(f"Startup run status: {run.status}")
                if run.last_error:
                    logger.error(f"Startup run error: {run.last_error}")
            except Exception as e:
                logger.error("Agent test run failed during startup", exc_info=True)

            yield

# --- FastAPI app setup ---
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

# Routers
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(guest.router, prefix="/guest", tags=["guest"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
# after other routers 
app.include_router(config_router.router, tags=["config"])
# --- Health and test endpoints ---
@app.get("/healthz", tags=["ops"])
async def healthz():
    return {"status": "ok"}

@app.get("/test-agent", tags=["ops"])
async def test_agent():
    project = app.state.project_client
    agent_id = app.state.agent_id

    thread = await project.agents.threads.create(metadata={"test": "true"})
    await project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Which day does next year's Christmas fall on?"
    )
    run = await project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent_id
    )

    response_text = ""
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    async for message in messages:
        if message.role == "assistant" and message.text_messages:
            response_text = message.text_messages[-1].text.value

    return {"response": response_text}

@app.get("/")
async def root():
    return {"message": "Runtime Chat API is running"}
