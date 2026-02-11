import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.dependencies import init_services, get_jira_service
from app.routers import admin, chat, jira_tickets, jira_webhooks, rag, templates

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_services(settings)
    yield
    # Shutdown
    jira = get_jira_service()
    await jira.close()


app = FastAPI(title="VOC-to-Jira Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(templates.router)
app.include_router(jira_tickets.router)
app.include_router(jira_webhooks.router)
app.include_router(rag.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
