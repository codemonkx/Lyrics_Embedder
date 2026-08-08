from core.lyrics import LyricParser

class TTMLToLRCConverter:
    @staticmethod
    def convert_content(ttml_content: str) -> str:
        """Converts TTML XML string content to standard LRC string format."""
        lines, metadata = LyricParser.parse_ttml(ttml_content)
        
        lrc_lines = []
        # Add tags if available
        if 'ti' in metadata:
            lrc_lines.append(f"[ti:{metadata['ti']}]")
        if 'ar' in metadata:
            lrc_lines.append(f"[ar:{metadata['ar']}]")
        if 'al' in metadata:
            lrc_lines.append(f"[al:{metadata['al']}]")
            
        for line in lines:
            time_sec = line['time']
            minutes = int(time_sec // 60)
            seconds = time_sec % 60
            # Format: [mm:ss.xx] (centiseconds rounded to 2 decimals)
            lrc_lines.append(f"[{minutes:02d}:{seconds:05.2f}] {line['text']}")
            
        return "\n".join(lrc_lines)

    @staticmethod
    def convert_file(ttml_path: str, lrc_path: str):
        """Converts a TTML file and writes the LRC result."""
        # Read content with fallback encodings
        content = ""
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open(ttml_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
                
        lrc_content = TTMLToLRCConverter.convert_content(content)
        
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_content)
