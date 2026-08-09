import sys
import os
from pathlib import Path
from platformdirs import user_data_dir

from app.core.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from app.core.logging import logger

def get_user_data_path() -> Path:
    """Returns the persistent user data directory path using platformdirs."""
    data_dir = Path(user_data_dir(APP_NAME, APP_ORGANIZATION))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_database_path() -> str:
    """Returns the path to the primary SQLite database, prioritizing local workspace DB if present."""
    local_db = Path("lyricforge.db")
    if local_db.exists():
        return str(local_db.resolve())
    return str((get_user_data_path() / "lyricforge.db").resolve())

def setup_platform_integration():
    """Configures Win32 taskbar integration and process flags."""
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f"lyricforge.pro.desktop.v{APP_VERSION.split()[0]}"
            )
            logger.info("Configured Win32 AppUserModelID.")
        except Exception as e:
            logger.warning(f"Could not set Win32 AppUserModelID: {e}")
