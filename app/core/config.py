import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from platformdirs import user_config_dir

from app.core.constants import APP_NAME, APP_ORGANIZATION, DEFAULT_MATCH_THRESHOLD, DEFAULT_WEIGHTS
from app.core.logging import logger

class AppConfigModel(BaseModel):
    music_dir: str = ""
    lyrics_dir: str = ""
    threshold: float = DEFAULT_MATCH_THRESHOLD
    keep_backup: bool = True
    verify_audio: bool = True
    monitoring_enabled: bool = False
    weights: Dict[str, float] = Field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    theme_preset: str = "NothingDark"

class ConfigManager:
    """Manages application persistent configuration using Pydantic and platformdirs."""
    
    def __init__(self):
        self.config_dir = Path(user_config_dir(APP_NAME, APP_ORGANIZATION))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self._config = self.load_config()

    def load_config(self) -> AppConfigModel:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AppConfigModel(**data)
            except Exception as e:
                logger.error(f"Failed to parse config file {self.config_file}: {e}. Resetting to defaults.")
        return AppConfigModel()

    def save_config(self) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config.model_dump(), f, indent=2)
            logger.info(f"Saved application config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to write config file {self.config_file}: {e}")

    @property
    def config(self) -> AppConfigModel:
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any) -> None:
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self.save_config()

config_manager = ConfigManager()
