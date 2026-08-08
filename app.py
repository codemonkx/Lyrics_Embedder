import os
import sys
import argparse
from pathlib import Path
from typing import List

from core.db_manager import DBManager
from core.scanner import FileScanner
from core.metadata import MetadataReader
from core.lyrics import LyricParser
from core.matcher import MatchingEngine
from core.embedder import Embedder
from core.backup import BackupManager
from core.report import ReportGenerator

def run_cli(args):
    print("=" * 60)
    print("LyricForge CLI Mode")
    print("=" * 60)

    db_path = "lyricforge.db"
    db = DBManager(db_path)
    
    music_dir = args.music_dir
    lyrics_dir = args.lyrics_dir
    threshold = args.threshold
    keep_backup = not args.no_backup
    
    if not os.path.exists(music_dir):
        print(f"[ERROR] Music folder does not exist: {music_dir}")
        sys.exit(1)
    if not os.path.exists(lyrics_dir):
        print(f"[ERROR] Lyrics folder does not exist: {lyrics_dir}")
        sys.exit(1)

    print(f"Music Folder:  {music_dir}")
    print(f"Lyrics Folder: {lyrics_dir}")
    print(f"Threshold:     {threshold}%")
    print(f"Keep Backups:  {keep_backup}")
    print("-" * 60)

    # 1. Scanning
    print("Scanning folders...")
    music_files = FileScanner.scan_music_files(music_dir)
    lyric_files = FileScanner.scan_lyric_files(lyrics_dir)
    print(f"Found {len(music_files)} music files and {len(lyric_files)} lyric files.")

    db.clear_songs()
    db.clear_lyrics()
    db.clear_matches()

    # 2. Add lyrics to DB
    print("Parsing lyrics...")
    parsed_lyrics = []
    for lyr_file in lyric_files:
        lyr_data = LyricParser.parse_file(str(lyr_file))
        lyr_id = db.add_lyric(
            lyr_data["file_path"],
            lyr_data["type"],
            lyr_data["last_timestamp"],
            lyr_data["plain_text_preview"]
        )
        lyr_data["id"] = lyr_id
        parsed_lyrics.append(lyr_data)

    # 3. Add songs to DB
    print("Reading song tags...")
    parsed_songs = []
    for song_file in music_files:
        song_data = MetadataReader.read_metadata(str(song_file))
        song_id = db.add_song(
            song_data["file_path"],
            song_data["title"],
            song_data["artist"],
            song_data["album"],
            song_data["duration"]
        )
        song_data["id"] = song_id
        parsed_songs.append(song_data)

    # Optional 3.5: Audio Verification
    if args.verify:
        print("Verifying audio legitimacy and checking spectral cutoffs...")
        from core.verifier import AudioVerifier
        for idx, song in enumerate(parsed_songs):
            print(f"  [{idx+1}/{len(parsed_songs)}] Analyzing: {Path(song['file_path']).name}")
            res = AudioVerifier.verify_file(song["file_path"])
            db.update_song_legitimacy(
                song["id"],
                res["actual_sample_rate"],
                res["spectral_cutoff"],
                res["legit"],
                res["reason"]
            )
            song["actual_sample_rate"] = res["actual_sample_rate"]
            song["spectral_cutoff"] = res["spectral_cutoff"]
            song["legit"] = res["legit"]
            song["legit_reason"] = res["reason"]

    # 4. Matching
    print("Matching songs and lyrics...")
    matches = MatchingEngine.find_matches(parsed_songs, parsed_lyrics, threshold)
    print(f"Successfully matched {len(matches)} songs.")
    
    for song_id, lyric_id, score in matches:
        db.save_match(song_id, lyric_id, score)

    # 5. Embedding (if requested)
    if args.embed:
        print("\nEmbedding lyrics...")
        backup_dir = "backups"
        backup_mgr = BackupManager(backup_dir)
        embedder = Embedder(backup_mgr)
        
        all_songs = {s["id"]: s for s in db.get_all_songs()}
        for song_id, lyric_id, score in matches:
            song = all_songs.get(song_id)
            if song:
                song_name = Path(song["file_path"]).name
                print(f"Embedding: {song_name} (Match Score: {score:.1f}%)")
                
                legit_info = None
                if args.verify:
                    legit_info = {
                        "actual_sample_rate": song.get("actual_sample_rate"),
                        "spectral_cutoff": song.get("spectral_cutoff"),
                        "legit": song.get("legit"),
                        "reason": song.get("legit_reason")
                    }
                
                success, msg = embedder.embed_lyrics(song["file_path"], song["lyrics_text"], keep_backup, legit_info)
                if success:
                    db.update_song_status(song_id, "Embedded")
                    print(f"  [SUCCESS] {msg}")
                else:
                    db.update_song_status(song_id, "Failed")
                    print(f"  [FAILED] {msg}")

    # 6. Report generation
    stats = db.get_stats()
    songs = db.get_all_songs()
    details = []
    for song in songs:
        error_msg = "Embedding tag error." if song["status"] == "Failed" else ""
        details.append({
            "file_path": song["file_path"],
            "status": song["status"],
            "title": song["title"],
            "artist": song["artist"],
            "lyric_path": song["lyric_path"],
            "error": error_msg,
            "actual_sample_rate": song.get("actual_sample_rate"),
            "spectral_cutoff": song.get("spectral_cutoff"),
            "legit": song.get("legit"),
            "legit_reason": song.get("legit_reason")
        })

    print("-" * 60)
    print("SUMMARY STATISTICS:")
    for k, v in stats.items():
        print(f"  {k.replace('_', ' ').title()}: {v}")
    print("-" * 60)

    if args.report:
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        rep_format = args.report.lower()
        filepath = os.path.join(export_dir, f"cli_report.{rep_format}")
        
        if rep_format == "html":
            ReportGenerator.generate_html_report(stats, details, filepath)
        elif rep_format == "txt":
            ReportGenerator.generate_txt_report(stats, details, filepath)
        elif rep_format == "json":
            ReportGenerator.generate_json_report(stats, details, filepath)
        
        print(f"Report exported successfully to: {filepath}")

def run_gui():
    # Set AppUserModelID on Windows to show custom taskbar icon instead of Python interpreter logo
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lyricforge.embedder.desktop.v1")
        except Exception:
            pass

    # Import and run PySide6 window
    from PySide6.QtWidgets import QApplication
    from ui.main_window import LyricForgeWindow
    
    from PySide6.QtGui import QFont
    app = QApplication(sys.argv)
    
    # Set explicit font to prevent QFont pointSize <= 0 warnings
    app_font = QFont("Cantarell", 10)
    app_font.setStyleHint(QFont.SansSerif)
    app.setFont(app_font)

    window = LyricForgeWindow()
    window.show()
    sys.exit(app.exec())

def main():
    parser = argparse.ArgumentParser(description="LyricForge - Smart synchronized lyrics matching and embedding tool.")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch the GUI application (default if no library paths provided).")
    parser.add_argument("-m", "--music-dir", type=str, help="Path to local Music Library folder.")
    parser.add_argument("-l", "--lyrics-dir", type=str, help="Path to separate Lyrics folder.")
    parser.add_argument("-t", "--threshold", type=float, default=60.0, help="Minimum fuzzy matching score (0-100). Default is 60.0.")
    parser.add_argument("--embed", action="store_true", help="Automatically embed matched lyrics into songs.")
    parser.add_argument("--no-backup", action="store_true", help="Disable backups before modifying files.")
    parser.add_argument("-r", "--report", choices=["html", "txt", "json"], help="Generate report of the process in specified format.")
    parser.add_argument("--verify", action="store_true", help="Verify audio file legitimacy and check for fake upscales.")
    args = parser.parse_args()

    # Launch GUI if explicit, or if directory paths are not provided
    if args.gui or not (args.music_dir and args.lyrics_dir):
        # Check if display environment exists (GUI warning fallback for headless servers)
        if sys.platform != 'win32' and not os.environ.get('DISPLAY'):
            print("[WARNING] Headless environment detected. Launching GUI mode might fail. Use CLI parameters.")
        run_gui()
    else:
        run_cli(args)

if __name__ == "__main__":
    main()
