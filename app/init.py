"""Initialization functions."""

import logging
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.settings import get_settings
from app import crud, models
from app.database import engine, Base

logger = logging.getLogger(__name__)

settings = get_settings()

def init_admin_user(db: Session) -> models.User:
    """Initialize admin user."""
    admin_user = crud.get_user(db, username=settings.admin_username)
    if not admin_user:
        try:
            admin_user = crud.create_user(
                db,
                {
                    "username": settings.admin_username,
                    "email": settings.admin_email,
                    "password": settings.admin_password,
                    "is_admin": True,
                },
            )
            logger.info("Admin user %s created.", admin_user.username)
        except IntegrityError:
            db.rollback()
            admin_user = crud.get_user(db, username=settings.admin_username)
            logger.info("Admin user %s already exists.", admin_user.username)
    else:
        logger.info("Admin user %s already exists.", admin_user.username)
    return admin_user

def database_exists(engine) -> bool:
    """Check if the database exists by inspecting for tables."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return bool(tables)

def init_db():
    """Initialize the database."""
    if not database_exists(engine):
        logger.info("Initializing the database.")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Database already exists. Skipping initialization.")