import os
import unittest
import struct
import tempfile
import shutil
from pathlib import Path

# Adjust path to import core modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.db_manager import DBManager
from core.scanner import FileScanner
from core.metadata import MetadataReader
from core.lyrics import LyricParser
from core.converter import TTMLToLRCConverter
from core.matcher import MatchingEngine
from core.backup import BackupManager
from core.embedder import Embedder
from core.report import ReportGenerator

class TestLyricForgeCore(unittest.TestCase):
    def setUp(self):
        # Create temp folder for test files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_lyricforge.db")
        self.db = DBManager(self.db_path)
        self.backup_dir = os.path.join(self.test_dir, "backups")
        self.backup_mgr = BackupManager(self.backup_dir)
        self.embedder = Embedder(self.backup_mgr)

    def tearDown(self):
        # Remove temp folder
        shutil.rmtree(self.test_dir)

    def make_tiny_wav(self, name: str, duration_sec: int = 2) -> str:
        """Helper to create a tiny valid WAV file."""
        filepath = os.path.join(self.test_dir, name)
        sample_rate = 8000
        num_samples = int(sample_rate * duration_sec)
        byte_rate = sample_rate * 2
        block_align = 2
        data_size = num_samples * 2
        file_size = 36 + data_size
        
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF', file_size, b'WAVE',
            b'fmt ', 16, 1, 1, sample_rate, byte_rate, block_align, 16,
            b'data', data_size
        )
        data = b'\x00' * data_size
        with open(filepath, 'wb') as f:
            f.write(header + data)
        return filepath

    def test_database_manager(self):
        # Test inserting and fetching song
        song_id = self.db.add_song("song1.mp3", "Title 1", "Artist 1", "Album 1", 180.0)
        self.assertIsNotNone(song_id)
        
        # Test inserting and fetching lyric
        lyric_id = self.db.add_lyric("lyric1.lrc", "lrc", 175.0, "[00:10.00] Test")
        self.assertIsNotNone(lyric_id)
        
        # Save match
        self.db.save_match(song_id, lyric_id, 95.5)
        
        # Fetch status
        songs = self.db.get_all_songs()
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0]["status"], "Matched")
        self.assertEqual(songs[0]["lyric_id"], lyric_id)
        
        # Check stats
        stats = self.db.get_stats()
        self.assertEqual(stats["total_songs"], 1)
        self.assertEqual(stats["matched"], 1)

    def test_file_scanner(self):
        # Create dummy music and lyric files
        m1 = self.make_tiny_wav("song1.wav")
        m2 = self.make_tiny_wav("song2.flac") # Note: FLAC signature is wrong, but scanner only checks suffix
        l1 = os.path.join(self.test_dir, "lyrics1.lrc")
        l2 = os.path.join(self.test_dir, "lyrics2.ttml")
        
        with open(l1, 'w') as f: f.write("")
        with open(l2, 'w') as f: f.write("")
        
        music_files = FileScanner.scan_music_files(self.test_dir)
        lyric_files = FileScanner.scan_lyric_files(self.test_dir)
        
        # Filter matching absolute paths
        music_names = [f.name for f in music_files]
        lyric_names = [f.name for f in lyric_files]
        
        self.assertIn("song1.wav", music_names)
        self.assertIn("song2.flac", music_names)
        self.assertIn("lyrics1.lrc", lyric_names)
        self.assertIn("lyrics2.ttml", lyric_names)

    def test_metadata_reader(self):
        # Create tiny WAV file
        wav_path = self.make_tiny_wav("test.wav", duration_sec=3)
        meta = MetadataReader.read_metadata(wav_path)
        
        self.assertEqual(meta["title"], "test") # Default parsed from filename
        self.assertAlmostEqual(meta["duration"], 3.0, delta=0.5)

    def test_lyric_parser_lrc(self):
        lrc_content = """[ti:LRC Title]
[ar:LRC Artist]
[al:LRC Album]
[00:10.00]Line One
[00:20.50]Line Two
"""
        parsed, metadata = LyricParser.parse_lrc(lrc_content)
        self.assertEqual(metadata["ti"], "LRC Title")
        self.assertEqual(metadata["ar"], "LRC Artist")
        self.assertEqual(metadata["al"], "LRC Album")
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["time"], 10.0)
        self.assertEqual(parsed[0]["text"], "Line One")
        self.assertEqual(parsed[1]["time"], 20.5)
        self.assertEqual(parsed[1]["text"], "Line Two")

    def test_lyric_parser_ttml(self):
        ttml_content = """<tt xmlns="http://www.w3.org/ns/ttml">
            <head><title>TTML Title</title></head>
            <body>
                <div>
                    <p begin="00:00:12.500" end="00:00:15.000">TTML Line One</p>
                    <p begin="45.2s" end="50s">TTML Line Two</p>
                </div>
            </body>
        </tt>"""
        parsed, metadata = LyricParser.parse_ttml(ttml_content)
        self.assertEqual(metadata.get("ti"), "TTML Title")
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["time"], 12.5)
        self.assertEqual(parsed[0]["text"], "TTML Line One")
        self.assertEqual(parsed[1]["time"], 45.2)
        self.assertEqual(parsed[1]["text"], "TTML Line Two")

    def test_ttml_to_lrc_converter(self):
        ttml_content = """<tt xmlns="http://www.w3.org/ns/ttml">
            <head><title>Test Converter</title></head>
            <body>
                <div>
                    <p begin="00:01:05.400" end="00:01:08.000">Converted Line</p>
                </div>
            </body>
        </tt>"""
        lrc = TTMLToLRCConverter.convert_content(ttml_content)
        self.assertIn("[ti:Test Converter]", lrc)
        self.assertIn("[01:05.40] Converted Line", lrc)

    def test_matching_engine(self):
        song = {"title": "Shape of You", "artist": "Ed Sheeran", "album": "Divide", "duration": 233.0, "file_path": "song.mp3"}
        lyric = {"metadata": {"ti": "Shape of You", "ar": "Ed Sheeran", "al": "Divide"}, "last_timestamp": 230.0, "file_path": "shape_of_you.lrc"}
        
        score = MatchingEngine.calculate_match_score(song, lyric)
        self.assertGreater(score, 90.0)

    def test_backup_and_embedder_flow(self):
        # Create a WAV file to write metadata to
        wav_path = self.make_tiny_wav("song_to_embed.wav", duration_sec=5)
        lyrics_to_write = "[00:01.00] Line one\n[00:03.00] Line two"
        
        # Test backup creation
        back_path = self.backup_mgr.create_backup(wav_path)
        self.assertIsNotNone(back_path)
        self.assertTrue(os.path.exists(back_path))
        
        # Test embedding (must write, verify, and clean up/keep backup)
        success, msg = self.embedder.embed_lyrics(wav_path, lyrics_to_write, keep_backup=True)
        self.assertTrue(success, msg)
        
        # Verify readback matches
        read_back = self.embedder.read_embedded_lyrics(wav_path)
        self.assertEqual(read_back.strip(), lyrics_to_write.strip())

    def test_report_generation(self):
        stats = {"total_songs": 10, "total_lyrics": 8, "embedded": 5, "matched": 2, "failed": 1, "unmatched": 2}
        details = [
            {"file_path": "song1.wav", "status": "Embedded", "lyric_path": "lyric1.lrc"},
            {"file_path": "song2.wav", "status": "Failed", "error": "Disk full"},
            {"file_path": "song3.wav", "status": "Unmatched", "artist": "Artist X", "title": "Song Y"}
        ]
        
        txt_report = os.path.join(self.test_dir, "report.txt")
        html_report = os.path.join(self.test_dir, "report.html")
        json_report = os.path.join(self.test_dir, "report.json")
        
        ReportGenerator.generate_txt_report(stats, details, txt_report)
        ReportGenerator.generate_html_report(stats, details, html_report)
        ReportGenerator.generate_json_report(stats, details, json_report)
        
        self.assertTrue(os.path.exists(txt_report))
        self.assertTrue(os.path.exists(html_report))
        self.assertTrue(os.path.exists(json_report))

    def test_audio_verifier(self):
        from core.verifier import AudioVerifier
        # Create a tiny WAV file (8000Hz, 2 sec)
        wav_path = self.make_tiny_wav("audio_to_verify.wav", duration_sec=2)
        
        # Test verification pipeline execution
        result = AudioVerifier.verify_file(wav_path)
        self.assertIsNotNone(result)
        self.assertEqual(result["actual_sample_rate"], 8000)
        self.assertTrue(result["legit"])  # 8000Hz doesn't trigger upscale checks
        
        # Test tag writing pipeline execution
        success, msg = AudioVerifier.write_legitimacy_tags(wav_path, result)
        self.assertTrue(success, msg)

    def test_audio_verifier_transcode_detection(self):
        import numpy as np
        import scipy.io.wavfile as wavfile
        from core.verifier import AudioVerifier
        
        # 1. Create a simulated transcode file at 44.1kHz with 16kHz brickwall cutoff
        path_16k = os.path.join(self.test_dir, "transcode_16k.wav")
        sample_rate = 44100
        duration = 5
        n_samples = sample_rate * duration
        data = np.random.normal(0, 0.1, n_samples)
        fft_data = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(n_samples, 1.0/sample_rate)
        # brickwall filter at 16kHz
        fft_data[freqs >= 16000] *= 1e-4  # Apply -80dB noise floor
        filtered = np.fft.irfft(fft_data, n_samples)
        int_data = (np.clip(filtered, -1.0, 1.0) * 32767).astype(np.int16)
        wavfile.write(path_16k, sample_rate, int_data)
        
        res = AudioVerifier.verify_file(path_16k)
        self.assertFalse(res["legit"])
        self.assertIn("Lossy Transcode", res["reason"])
        self.assertIn("16.0 kHz", res["reason"])
        
        # 2. Create a simulated transcode file at 44.1kHz with 20kHz brickwall cutoff (320kbps MP3 transcode)
        path_20k = os.path.join(self.test_dir, "transcode_20k.wav")
        fft_data_20 = np.fft.rfft(data)
        fft_data_20[freqs >= 20000] *= 1e-4
        filtered_20 = np.fft.irfft(fft_data_20, n_samples)
        int_data_20 = (np.clip(filtered_20, -1.0, 1.0) * 32767).astype(np.int16)
        wavfile.write(path_20k, sample_rate, int_data_20)
        
        res_20 = AudioVerifier.verify_file(path_20k)
        self.assertFalse(res_20["legit"])
        self.assertIn("Lossy Transcode", res_20["reason"])
        self.assertIn("20.0 kHz", res_20["reason"])

    def test_audio_verifier_silence_handling(self):
        import numpy as np
        import scipy.io.wavfile as wavfile
        from core.verifier import AudioVerifier
        
        # Create a near-silent file at 44.1kHz
        path_silent = os.path.join(self.test_dir, "silent.wav")
        sample_rate = 44100
        duration = 5
        n_samples = sample_rate * duration
        data = np.random.normal(0, 1e-7, n_samples)  # quiet noise
        int_data = (data * 32767).astype(np.int16)
        wavfile.write(path_silent, sample_rate, int_data)
        
        res = AudioVerifier.verify_file(path_silent)
        # Should be classified as legit (fallback to the absolute cutoff check since all slices were silent)
        self.assertTrue(res["legit"])
        self.assertEqual(res["actual_sample_rate"], 44100)

if __name__ == "__main__":
    unittest.main()
