"""Settings for the app."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the app."""

    gunicorn_workers: int
    sqlite_db: str = "./database/database.db"
    secret_key: str
    refresh_secret_key: str
    admin_username: str
    admin_email: str
    admin_password: str

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return f"sqlite:///{self.sqlite_db}"

    class Config:
        """Config for the app."""

        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    """Get settings."""
    return Settings()
