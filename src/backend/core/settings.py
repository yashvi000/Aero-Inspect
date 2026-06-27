from functools import lru_cache
import yaml

from src.shared.utils.paths import CONFIG_DIR


@lru_cache(maxsize=1)
def get_yaml_config() -> dict:
    # Load config/config.yaml once and cache it
    
    config_path = CONFIG_DIR / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)