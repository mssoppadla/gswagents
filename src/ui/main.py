#src/ui/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import logging 
from src.ui.routers import auth, org, sources, widget, onboarding
# Import from the new dependencies file
from src.ui.dependencies import templates 
from src.ui.dependencies import get_templates 
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
import os
import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse

import logging

logging.basicConfig(
    level=logging.INFO,  # ensure INFO messages are shown
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("ui")

# then use logger instead of logging
logger.info("[UI proxy] logging in UI: ...")


app = FastAPI(title="Business Owner UI Service")

templates_dir = os.path.join(os.path.dirname(__file__), "templates") 
templates = Jinja2Templates(directory=templates_dir)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(org.router, prefix="/org", tags=["org"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(widget.router, prefix="/widget", tags=["widget"])
app.include_router(onboarding.router) # Prefix handled in router file

@app.get("/", response_class=HTMLResponse, tags=["auth"])
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["auth"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/healthz", tags=["ops"])
async def healthz():
    return {"status": "ok"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    tenant_id: int, 
    templates: Jinja2Templates = Depends(get_templates)
):
    # You might want to fetch tenant details here to display on the dashboard
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "tenant_id": tenant_id
    })

# Serve widget.html
@app.get("/widget", response_class=HTMLResponse)
async def serve_widget(request: Request):
    return templates.TemplateResponse("widget.html", {"request": request})
# Serve widget.js
app.mount("/static", StaticFiles(directory=templates_dir), name="static")
######################################

# ✅ Proxy endpoint: UI forwards /chat/query to API on port 8000
@app.post("/chat/query")
async def proxy_query(request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://chat.zenai.co.in/chat/query",
            content=await request.body(),
            headers=request.headers
        )
        return resp.json()

@app.post("/chat/query/stream")
async def proxy_query_stream(request: Request):
    # Log incoming request
    body = await request.body()
    logger.info(f"[UI proxy] Received stream request body: ... ")
    #logging.info(f"[UI proxy] Received stream request body: {body.decode('utf-8', errors='ignore')}")
    #logging.info(f"[UI proxy] Headers: {dict(request.headers)}")

    async def event_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            logger.info("[UI proxy] Opening stream to backend /chat/query/stream")
            #logging.info("[UI proxy] Opening stream to backend /chat/query/stream")
            
            async with client.stream(
                "POST",
                "https://chat.zenai.co.in/chat/query/stream", # "http://127.0.0.1:8000/chat/query/stream",
                data=body,   # ✅ use data instead of content
                headers=request.headers,
            ) as upstream:
                logger.info("[UI proxy] upstream statusL ")
             #   logging.info(f"[UI proxy] Upstream status: {upstream.status_code}")
                
                
                async for chunk in upstream.aiter_bytes():
                    logger.info("[UI proxy] forwarding chunks")
                    logging.info(f"[UI proxy] Forwarding chunk: {chunk[:100]!r}")  # log first 100 bytes
                    
                    yield chunk
            logger.info("[UI proxy] upstream stream closed")
            logging.info("[UI proxy] Upstream stream closed")

    return StreamingResponse(event_generator(), media_type="text/event-stream")