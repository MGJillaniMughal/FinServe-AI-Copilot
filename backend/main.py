"""FinServe AI Copilot - FastAPI application entry point.

Enterprise Financial Risk Intelligence, Compliance Automation and Document
Intelligence platform. Developed by Jillani SofTech (Muhammad Ghulam Jillani).
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.config import settings
from backend.utils.logger import get_logger
from backend.routers import (auth, health, documents, rag, risk, compliance, analysis, dashboard)
from backend.seed import seed

logger = get_logger("main")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=("Enterprise Financial Risk Intelligence, Compliance Automation and Document "
                 "Intelligence platform. Developed by Jillani SofTech (Muhammad Ghulam Jillani)."),
    contact={"name": settings.VENDOR, "url": "https://www.jillanisoftech.com/",
             "email": "m.g.jillani@jillanisoftech.com"},
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for r in (auth, health, documents, rag, risk, compliance, analysis, dashboard):
    app.include_router(r.router)


@app.on_event("startup")
def _startup():
    seed()
    logger.info("%s v%s by %s is ready", settings.APP_NAME, settings.VERSION, settings.VENDOR)


_assets = os.path.join(FRONTEND_DIR, "assets")
if os.path.isdir(_assets):
    app.mount("/assets", StaticFiles(directory=_assets), name="assets")


def _page(name: str):
    path = os.path.join(FRONTEND_DIR, name)
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"message": f"{name} not found. See /docs for the API."})


@app.get("/", include_in_schema=False)
def landing():
    return _page("index.html")


@app.get("/login", include_in_schema=False)
def login_page():
    return _page("login.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return _page("dashboard.html")
