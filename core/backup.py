import os
import shutil
import time
from pathlib import Path
from typing import Optional

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, filepath: str) -> Optional[str]:
        """
        Creates a backup copy of the file.
        Returns the absolute path to the backup file if successful, otherwise None.
        """
        try:
            orig_path = Path(filepath)
            if not orig_path.exists():
                return None
            
            # Generate unique backup filename using timestamp
            timestamp = int(time.time() * 1000)
            backup_filename = f"{timestamp}_{orig_path.name}"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(orig_path, backup_path)
            return str(backup_path.resolve())
        except Exception:
            return None

    def restore_backup(self, original_filepath: str, backup_filepath: str) -> bool:
        """
        Restores a backup file to its original location, overwriting any current changes.
        Returns True if successful, otherwise False.
        """
        try:
            orig_path = Path(original_filepath)
            back_path = Path(backup_filepath)
            
            if not back_path.exists():
                return False
                
            # Copy backup back to original location
            shutil.copy2(back_path, orig_path)
            return True
        except Exception:
            return False

    def remove_backup(self, backup_filepath: str) -> bool:
        """
        Deletes the backup file from disk.
        Returns True if successful, otherwise False.
        """
        try:
            back_path = Path(backup_filepath)
            if back_path.exists():
                back_path.unlink()
                return True
            return False
        except Exception:
            return False
