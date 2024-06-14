"""Main module for the application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .init import init_admin_user
from .database import Base, SessionLocal, engine
from .routers import (
    users,
)
from .settings import get_settings


# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_admin_user(db)
    finally:
        db.close()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="ZoomProp Test",
    description="zoomprop test",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check."""
    logger.info("Health check")
    return {"status": "healthy"}


app.include_router(users.router)
