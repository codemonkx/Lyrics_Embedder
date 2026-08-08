import os
import sqlite3
from typing import Dict, List, Any, Optional

class DBManager:
    def __init__(self, db_path: str = "lyricforge.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                
                # Songs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS songs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        duration REAL,
                        status TEXT DEFAULT 'Unmatched',
                        lyric_id INTEGER,
                        FOREIGN KEY(lyric_id) REFERENCES lyrics(id)
                    )
                """)
                
                # Lyrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lyrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE,
                        type TEXT,
                        last_timestamp REAL,
                        lyrics_text TEXT
                    )
                """)
                
                # Matches table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS matches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        song_id INTEGER,
                        lyric_id INTEGER,
                        score REAL,
                        match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Pending',
                        FOREIGN KEY(song_id) REFERENCES songs(id),
                        FOREIGN KEY(lyric_id) REFERENCES lyrics(id)
                    )
                """)
                
                # Settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                
                # Migrations: Add new columns if missing
                for col, col_type in [
                    ("actual_sample_rate", "INTEGER"),
                    ("spectral_cutoff", "REAL"),
                    ("legit", "INTEGER"),
                    ("legit_reason", "TEXT"),
                    ("sample_rate", "INTEGER"),
                    ("bits_per_sample", "INTEGER"),
                    ("channels", "INTEGER"),
                    ("file_size", "REAL"),
                    ("bitrate", "REAL"),
                    ("replay_gain", "TEXT"),
                    ("date_modified", "TEXT")
                ]:
                    try:
                        cursor.execute(f"ALTER TABLE songs ADD COLUMN {col} {col_type}")
                    except sqlite3.OperationalError:
                        pass
                
                conn.commit()
        finally:
            conn.close()

    def add_song(self, file_path: str, title: str, artist: str, album: str, duration: float,
                 sample_rate: int = None, bits_per_sample: int = None, channels: int = None,
                 file_size: float = None, bitrate: float = None, replay_gain: str = None,
                 date_modified: str = None) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO songs (
                        file_path, title, artist, album, duration, sample_rate, bits_per_sample,
                        channels, file_size, bitrate, replay_gain, date_modified, status, lyric_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                            COALESCE((SELECT status FROM songs WHERE file_path = ?), 'Unmatched'), 
                            (SELECT lyric_id FROM songs WHERE file_path = ?))
                """, (file_path, title, artist, album, duration, sample_rate, bits_per_sample,
                      channels, file_size, bitrate, replay_gain, date_modified, file_path, file_path))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    def add_lyric(self, file_path: str, lyric_type: str, last_timestamp: float, lyrics_text: str) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO lyrics (file_path, type, last_timestamp, lyrics_text)
                    VALUES (?, ?, ?, ?)
                """, (file_path, lyric_type, last_timestamp, lyrics_text))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    def clear_songs(self):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM songs")
                conn.commit()
        finally:
            conn.close()

    def clear_lyrics(self):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM lyrics")
                conn.commit()
        finally:
            conn.close()

    def clear_matches(self):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM matches")
                conn.commit()
        finally:
            conn.close()

    def get_all_songs(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*,
                       l.file_path as lyric_path, l.lyrics_text
                FROM songs s
                LEFT JOIN lyrics l ON s.lyric_id = l.id
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_song_legitimacy(self, song_id: int, sample_rate: int, cutoff: float, legit: bool, reason: str):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE songs
                    SET actual_sample_rate = ?, spectral_cutoff = ?, legit = ?, legit_reason = ?
                    WHERE id = ?
                """, (sample_rate, cutoff, 1 if legit else 0, reason, song_id))
                conn.commit()
        finally:
            conn.close()

    def get_all_lyrics(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lyrics")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def save_match(self, song_id: int, lyric_id: int, score: float):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # Clear old matches for this song
                cursor.execute("DELETE FROM matches WHERE song_id = ?", (song_id,))
                cursor.execute("""
                    INSERT INTO matches (song_id, lyric_id, score, status)
                    VALUES (?, ?, ?, 'Pending')
                """, (song_id, lyric_id, score))
                cursor.execute("""
                    UPDATE songs
                    SET lyric_id = ?, status = 'Matched'
                    WHERE id = ?
                """, (lyric_id, song_id))
                conn.commit()
        finally:
            conn.close()

    def update_song_status(self, song_id: int, status: str, lyric_id: Optional[int] = None):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                if lyric_id is not None:
                    cursor.execute("""
                        UPDATE songs
                        SET status = ?, lyric_id = ?
                        WHERE id = ?
                    """, (status, lyric_id, song_id))
                else:
                    cursor.execute("""
                        UPDATE songs
                        SET status = ?
                        WHERE id = ?
                    """, (status, song_id))
                
                # Update matches table if it exists
                cursor.execute("""
                    UPDATE matches
                    SET status = ?
                    WHERE song_id = ? AND (lyric_id = (SELECT lyric_id FROM songs WHERE id = ?) OR lyric_id IS NULL)
                """, (status, song_id, song_id))
                conn.commit()
        finally:
            conn.close()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        finally:
            conn.close()

    def set_setting(self, key: str, value: str):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES (?, ?)
                """, (key, value))
                conn.commit()
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, int]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM songs")
            total_songs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lyrics")
            total_lyrics = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM songs WHERE status = 'Matched'")
            matched = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM songs WHERE status = 'Embedded'")
            embedded = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM songs WHERE status = 'Failed'")
            failed = cursor.fetchone()[0]
            
            return {
                "total_songs": total_songs,
                "total_lyrics": total_lyrics,
                "matched": matched,
                "embedded": embedded,
                "failed": failed,
                "unmatched": total_songs - matched - embedded - failed
            }
        finally:
            conn.close()
