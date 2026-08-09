import re
from typing import Dict, Any, List
from app.models.lyric import LyricLine

class LRCParser:
    TIME_TAG_REGEX = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\]')
    META_TAG_REGEX = re.compile(r'\[([a-zA-Z]+):(.*?)\]')

    @classmethod
    def parse_text(cls, text: str) -> Dict[str, Any]:
        lines: List[LyricLine] = []
        metadata: Dict[str, str] = {}
        max_ts = 0.0

        for line_raw in text.splitlines():
            line_str = line_raw.strip()
            if not line_str:
                continue

            time_tags = cls.TIME_TAG_REGEX.findall(line_str)
            if time_tags:
                clean_text = cls.TIME_TAG_REGEX.sub('', line_str).strip()
                for mm, ss, ms in time_tags:
                    mins = int(mm)
                    secs = int(ss)
                    msecs = int(ms) if len(ms) == 3 else int(ms) * 10
                    ts = mins * 60.0 + secs + (msecs / 1000.0)
                    if ts > max_ts:
                        max_ts = ts
                    time_tag_str = f"[{mm}:{ss}.{ms}]"
                    lines.append(LyricLine(timestamp=ts, text=clean_text, time_tag=time_tag_str))
            else:
                meta_match = cls.META_TAG_REGEX.match(line_str)
                if meta_match:
                    k, v = meta_match.groups()
                    metadata[k.lower()] = v.strip()

        lines.sort(key=lambda l: l.timestamp)
        plain_preview = "\n".join([f"{l.time_tag} {l.text}" for l in lines[:10]])

        return {
            "lines": lines,
            "metadata": metadata,
            "last_timestamp": max_ts,
            "plain_text_preview": plain_preview
        }
