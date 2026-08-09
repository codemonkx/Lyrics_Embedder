import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from app.models.lyric import LyricLine
from app.core.logging import logger

class TTMLParser:
    @staticmethod
    def parse_time_str(time_str: str) -> float:
        """Converts TTML timestamp string (e.g. '00:01:23.456' or '12.5s') to seconds float."""
        if not time_str:
            return 0.0
        time_str = time_str.strip()
        if time_str.endswith('s'):
            return float(time_str[:-1])
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600.0 + float(m) * 60.0 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return float(m) * 60.0 + float(s)
        try:
            return float(time_str)
        except ValueError:
            return 0.0

    @classmethod
    def parse_text(cls, xml_text: str) -> Dict[str, Any]:
        lines: List[LyricLine] = []
        metadata: Dict[str, str] = {}
        max_ts = 0.0

        try:
            root = ET.fromstring(xml_text)
            # Find all <p> elements inside <body>
            for elem in root.iter():
                if elem.tag.endswith('p'):
                    begin = elem.attrib.get('begin', '00:00.00')
                    ts = cls.parse_time_str(begin)
                    text = elem.text or "".join(elem.itertext())
                    text = text.strip()
                    if text:
                        if ts > max_ts:
                            max_ts = ts
                        mins = int(ts) // 60
                        secs = int(ts) % 60
                        msecs = int((ts - int(ts)) * 100)
                        time_tag_str = f"[{mins:02d}:{secs:02d}.{msecs:02d}]"
                        lines.append(LyricLine(timestamp=ts, text=text, time_tag=time_tag_str))
        except Exception as e:
            logger.warning(f"Error parsing TTML XML text: {e}")

        lines.sort(key=lambda l: l.timestamp)
        plain_preview = "\n".join([f"{l.time_tag} {l.text}" for l in lines[:10]])

        return {
            "lines": lines,
            "metadata": metadata,
            "last_timestamp": max_ts,
            "plain_text_preview": plain_preview
        }
