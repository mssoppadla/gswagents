from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import logging 
from src.ui.routers import auth, org, sources, widget, onboarding
# Import from the new dependencies file
from src.ui.dependencies import templates 
from src.ui.dependencies import get_templates 
from fastapi.templating import Jinja2Templates 

app = FastAPI(title="Business Owner UI Service")

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

# #************ Index page working for this ************
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, HTMLResponse
# from fastapi.templating import Jinja2Templates
# import logging 
# logging.basicConfig(level=logging.INFO)
# from src.ui.routers import auth, org, sources, widget, onboarding

# app = FastAPI(title="Business Owner UI Service")

# # CORS (adjust origins for your frontend domains in production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten in prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Routers
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(org.router, prefix="/org", tags=["org"])
# app.include_router(sources.router, prefix="/sources", tags=["sources"])
# app.include_router(widget.router, prefix="/widget", tags=["widget"])
# app.include_router(onboarding.router, tags=["onboarding"])# prefix="/onboarding",

# # Templates directory (for rendering HTML pages)
# templates = Jinja2Templates(directory="templates")

# @app.get("/login", response_class=HTMLResponse, tags=["auth"])
# async def login_page(request: Request):
#     # Renders templates/login.html
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/healthz", tags=["ops"])
# async def healthz():
#     return {"status": "ok"}

# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# if __name__ == "__main__": 
#     for route in app.routes: 
#         logging.info("ROUTE: %s %s", route.path, route.methods)
        
#        # logging.info("ROUTE: %s %s", route.path, route.methods)
#        # print("ROUTE:", route.path, route.methods)