from pathlib import Path
from typing import Dict, Any
from app.lyrics.lrc import LRCParser
from app.lyrics.ttml import TTMLParser
from app.core.logging import logger

class LyricParser:
    @classmethod
    def parse_file(cls, file_path: str) -> Dict[str, Any]:
        p = Path(file_path)
        ext = p.suffix.lower()
        
        data = {
            "file_path": str(p.resolve()),
            "type": "TTML" if ext in [".ttml", ".xml"] else "LRC",
            "last_timestamp": 0.0,
            "plain_text_preview": "",
            "lines": [],
            "metadata": {}
        }

        if not p.exists():
            logger.warning(f"Lyric file not found: {file_path}")
            return data

        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if ext in [".ttml", ".xml"]:
                parsed = TTMLParser.parse_text(content)
            else:
                parsed = LRCParser.parse_text(content)

            data["lines"] = [l.model_dump() for l in parsed["lines"]]
            data["metadata"] = parsed["metadata"]
            data["last_timestamp"] = parsed["last_timestamp"]
            data["plain_text_preview"] = parsed["plain_text_preview"]

        except Exception as e:
            logger.error(f"Failed to parse lyric file {file_path}: {e}")

        return data
