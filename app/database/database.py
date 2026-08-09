import os
import shutil
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.database.models import Base
from app.core.logging import logger

class DatabaseManager:
    def __init__(self, db_path: str = "lyricforge.db"):
        self.db_path = str(Path(db_path).resolve())
        self.engine = create_engine(f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.backup_and_init()

    def backup_and_init(self):
        """Creates a safety backup of existing SQLite database and migrates schema cleanly."""
        db_file = Path(self.db_path)
        if db_file.exists() and db_file.stat().st_size > 0:
            backup_dir = db_file.parent / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"lyricforge_db_backup.db"
            try:
                shutil.copy2(db_file, backup_file)
                logger.info(f"Database safety backup created at: {backup_file}")
            except Exception as e:
                logger.warning(f"Failed to create database backup: {e}")

        # Ensure all tables exist
        Base.metadata.create_all(bind=self.engine)

        # Automatic schema column migration check
        self.auto_migrate_columns()

        logger.info(f"Initialized SQLAlchemy database at {self.db_path}")

    def auto_migrate_columns(self):
        """Checks for missing columns in existing SQLite tables and adds them automatically."""
        try:
            with self.engine.connect() as conn:
                # Check lyrics table columns
                result = conn.execute(text("PRAGMA table_info(lyrics)")).fetchall()
                existing_cols = {row[1] for row in result}
                if "plain_text_preview" not in existing_cols:
                    conn.execute(text("ALTER TABLE lyrics ADD COLUMN plain_text_preview TEXT DEFAULT ''"))
                    conn.commit()
                    logger.info("Migrated schema: Added plain_text_preview column to lyrics table.")

                # Check songs table columns
                result_songs = conn.execute(text("PRAGMA table_info(songs)")).fetchall()
                song_cols = {row[1] for row in result_songs}
                if "actual_sample_rate" not in song_cols:
                    conn.execute(text("ALTER TABLE songs ADD COLUMN actual_sample_rate INTEGER"))
                if "spectral_cutoff" not in song_cols:
                    conn.execute(text("ALTER TABLE songs ADD COLUMN spectral_cutoff REAL"))
                if "legit" not in song_cols:
                    conn.execute(text("ALTER TABLE songs ADD COLUMN legit INTEGER"))
                if "legit_reason" not in song_cols:
                    conn.execute(text("ALTER TABLE songs ADD COLUMN legit_reason TEXT"))
                conn.commit()
        except Exception as e:
            logger.warning(f"Auto-migration column check warning: {e}")

    def get_session(self) -> Session:
        return self.SessionLocal()
