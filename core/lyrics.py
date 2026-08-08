import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class LyricParser:
    LRC_METADATA_RE = re.compile(r'^\[(ti|ar|al|ln|length):(.*)\]$', re.IGNORECASE)
    LRC_TIMESTAMP_RE = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\]')

    @staticmethod
    def parse_ttml_time(time_str: str) -> float:
        """Parses a TTML timestamp string into seconds (float)."""
        time_str = time_str.strip()
        if not time_str:
            return 0.0

        # Offset formats
        if time_str.endswith('ms'):
            try:
                return float(time_str[:-2]) / 1000.0
            except ValueError:
                pass
        elif time_str.endswith('s'):
            try:
                return float(time_str[:-1])
            except ValueError:
                pass
        elif time_str.endswith('m'):
            try:
                return float(time_str[:-1]) * 60.0
            except ValueError:
                pass
        elif time_str.endswith('h'):
            try:
                return float(time_str[:-1]) * 3600.0
            except ValueError:
                pass

        # Clock formats: hh:mm:ss.frac, mm:ss.frac, ss.frac
        parts = time_str.split(':')
        try:
            if len(parts) == 3:
                h = float(parts[0])
                m = float(parts[1])
                s = float(parts[2])
                return h * 3600.0 + m * 60.0 + s
            elif len(parts) == 2:
                m = float(parts[0])
                s = float(parts[1])
                return m * 60.0 + s
            elif len(parts) == 1:
                return float(parts[0])
        except ValueError:
            pass

        return 0.0

    @staticmethod
    def parse_lrc(content: str) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Parses LRC file content into timing lines and metadata tags."""
        lines = content.splitlines()
        parsed_lines = []
        metadata = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse metadata tags
            meta_match = LyricParser.LRC_METADATA_RE.match(line)
            if meta_match:
                key = meta_match.group(1).lower()
                val = meta_match.group(2).strip()
                metadata[key] = val
                continue

            # Parse timestamp matches
            matches = list(LyricParser.LRC_TIMESTAMP_RE.finditer(line))
            if not matches:
                continue

            # Find the text after all timestamps
            last_match = matches[-1]
            text = line[last_match.end():].strip()

            for match in matches:
                min_part = int(match.group(1))
                sec_part = float(match.group(2))
                total_seconds = min_part * 60.0 + sec_part
                parsed_lines.append({
                    "time": total_seconds,
                    "text": text
                })

        parsed_lines.sort(key=lambda x: x["time"])
        return parsed_lines, metadata

    @staticmethod
    def parse_ttml(content: str) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Parses TTML XML file content into timing lines and metadata."""
        parsed_lines = []
        metadata = {}
        
        try:
            root = ET.fromstring(content)
            
            # Look for namespace
            ns = ""
            if root.tag.startswith('{'):
                ns = root.tag.split('}')[0] + '}'

            # Try to find metadata (title, etc.)
            title_node = root.find(f'.//{ns}title')
            if title_node is not None and title_node.text:
                metadata['ti'] = title_node.text.strip()
            
            # Find all <p> elements
            for p in root.iter(f'{ns}p'):
                begin = p.get('begin')
                if begin:
                    time_sec = LyricParser.parse_ttml_time(begin)
                    # Extract raw text from paragraph elements (handling child spans if any)
                    text = "".join(p.itertext()).strip()
                    parsed_lines.append({
                        "time": time_sec,
                        "text": text
                    })
        except Exception:
            pass

        parsed_lines.sort(key=lambda x: x["time"])
        return parsed_lines, metadata

    @staticmethod
    def parse_file(filepath: str) -> Dict[str, Any]:
        """Parses a lyric file (LRC or TTML) and returns normalized structure."""
        path = Path(filepath)
        ext = path.suffix.lower()

        # Read content using UTF-8 (fallback to cp1252 or other standard encodings on error)
        content = ""
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if ext == '.lrc':
            lines, metadata = LyricParser.parse_lrc(content)
        elif ext == '.ttml':
            lines, metadata = LyricParser.parse_ttml(content)
        else:
            lines, metadata = [], {}

        last_timestamp = lines[-1]["time"] if lines else 0.0

        # Create human-readable plain text preview
        plain_text_preview = ""
        for line in lines:
            minutes = int(line['time'] // 60)
            seconds = line['time'] % 60
            plain_text_preview += f"[{minutes:02d}:{seconds:05.2f}] {line['text']}\n"

        return {
            "file_path": str(path.resolve()),
            "type": ext[1:],
            "lines": lines,
            "metadata": metadata,
            "last_timestamp": last_timestamp,
            "plain_text_preview": plain_text_preview.strip()
        }
