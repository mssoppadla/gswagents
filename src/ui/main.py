from fastapi import FastAPI
from src.ui.routers import auth, org, sources, widget

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(org.router, prefix="/org", tags=["org"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(widget.router, prefix="/widget", tags=["widget"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
