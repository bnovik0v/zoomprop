"""Settings for the app."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the app."""

    port: int
    gunicorn_workers: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_port: int
    db_host: str
    secret_key: str
    refresh_secret_key: str
    admin_username: str
    admin_email: str
    admin_password: str

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"

    class Config:
        """Config for the app."""

        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    """Get settings."""
    return Settings()
