from functools import lru_cache
import yaml

from src.shared.utils.paths import CONFIG_DIR
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5433
    DB_NAME: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External services
    YOLO_SERVICE_URL: str = "http://localhost:8001"
    AGENT_SERVICE_URL: str = "http://localhost:8002"
    PDF_SERVICE_URL: str = "http://localhost:8003"

    # App
    SECRET_KEY: str
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()


@lru_cache(maxsize=1)
def get_yaml_config() -> dict:
    # Load config/config.yaml once and cache it
    
    config_path = CONFIG_DIR / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)