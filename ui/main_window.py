import os
import sys
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QPropertyAnimation, QRectF, QRect, QPoint, QEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QTextEdit, QProgressBar,
    QMessageBox, QCheckBox, QSlider, QGridLayout, QFrame, QStackedWidget,
    QButtonGroup, QLineEdit, QScrollArea, QMenu, QComboBox, QSizeGrip
)
from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QPainter, QPixmap

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

from core.db_manager import DBManager
from core.scanner import FileScanner
from core.metadata import MetadataReader
from core.lyrics import LyricParser
from core.matcher import MatchingEngine
from core.embedder import Embedder
from core.backup import BackupManager
from core.report import ReportGenerator
from core.verifier import AudioVerifier

from ui.theme import (
    NOTHING_OS_QSS, BG_BASE, BG_SURFACE, BG_CARD, BORDER_SUBTLE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_RED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
)
from ui.widgets.header_bar import GNOMEHeaderBar
from ui.widgets.sidebar import GNOMESidebar
from ui.widgets.settings_row import GNOMESettingsRow
from ui.widgets.empty_state import GNOMEEmptyState
from ui.widgets.toast import GNOMEToast
from ui.widgets.about_dialog import GNOMEAboutDialog


class DragDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and os.path.isdir(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and os.path.isdir(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_path = url.toLocalFile()
                if os.path.isdir(local_path):
                    self.setText(local_path)
                    event.acceptProposedAction()
                    return


class ScanWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(dict)

    def __init__(self, db: DBManager, music_dir: str, lyrics_dir: str, threshold: float, verify_audio: bool, custom_weights: Optional[Dict[str, float]] = None):
        super().__init__()
        self.db = db
        self.music_dir = music_dir
        self.lyrics_dir = lyrics_dir
        self.threshold = threshold
        self.verify_audio = verify_audio
        self.custom_weights = custom_weights

    def run(self):
        try:
            self.progress.emit(5, "Clearing old records...")
            self.db.clear_songs()
            self.db.clear_lyrics()
            self.db.clear_matches()

            self.progress.emit(10, "Scanning music files...")
            music_files = FileScanner.scan_music_files(self.music_dir)
            
            self.progress.emit(20, "Scanning lyrics files...")
            lyric_files = FileScanner.scan_lyric_files(self.lyrics_dir)

            total_music = len(music_files)
            total_lyrics = len(lyric_files)
            
            # Step 1: Read lyrics files
            self.progress.emit(30, f"Parsing {total_lyrics} lyrics files...")
            parsed_lyrics = []
            for idx, lyr_file in enumerate(lyric_files):
                lyr_data = LyricParser.parse_file(str(lyr_file))
                lyr_id = self.db.add_lyric(
                    lyr_data["file_path"],
                    lyr_data["type"],
                    lyr_data["last_timestamp"],
                    lyr_data["plain_text_preview"]
                )
                lyr_data["id"] = lyr_id
                parsed_lyrics.append(lyr_data)
                
                val = 30 + int((idx / max(1, total_lyrics)) * 15)
                self.progress.emit(val, f"Parsing lyrics: {idx+1}/{total_lyrics}")

            # Step 2: Read audio metadata
            self.progress.emit(45, f"Extracting metadata from {total_music} songs...")
            parsed_songs = []
            for idx, song_file in enumerate(music_files):
                song_data = MetadataReader.read_metadata(str(song_file))
                song_id = self.db.add_song(
                    song_data["file_path"],
                    song_data["title"],
                    song_data["artist"],
                    song_data["album"],
                    song_data["duration"],
                    song_data["sample_rate"],
                    song_data["bits_per_sample"],
                    song_data["channels"],
                    song_data["file_size"],
                    song_data["bitrate"],
                    song_data["replay_gain"],
                    song_data["date_modified"]
                )
                song_data["id"] = song_id
                parsed_songs.append(song_data)
                
                val = 45 + int((idx / max(1, total_music)) * 15)
                self.progress.emit(val, f"Reading metadata: {idx+1}/{total_music}")

            # Optional Step 2.5: Verify audio files legitimacy
            if self.verify_audio and total_music > 0:
                self.progress.emit(60, "Verifying audio legitimacy & checking spectral cutoffs...")
                for idx, song in enumerate(parsed_songs):
                    self.progress.emit(60 + int((idx / total_music) * 15), f"Analyzing audio spectral data: {idx+1}/{total_music}")
                    res = AudioVerifier.verify_file(song["file_path"])
                    self.db.update_song_legitimacy(
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

            # Step 3: Match songs to lyrics
            self.progress.emit(75, "Running matching engine...")
            matches = MatchingEngine.find_matches(parsed_songs, parsed_lyrics, self.threshold, self.custom_weights)
            
            self.progress.emit(90, "Caching matches in database...")
            for song_id, lyric_id, score in matches:
                self.db.save_match(song_id, lyric_id, score)

            self.progress.emit(100, "Scanning complete.")
            self.finished.emit(self.db.get_stats())

        except Exception as e:
            self.progress.emit(100, f"Error: {e}")
            self.finished.emit({"error": str(e)})


class EmbedWorker(QThread):
    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self, db: DBManager, song_ids: List[int], keep_backup: bool, backup_dir: str, only_write_integrity: bool = False):
        super().__init__()
        self.db = db
        self.song_ids = song_ids
        self.keep_backup = keep_backup
        self.only_write_integrity = only_write_integrity
        
        backup_mgr = BackupManager(backup_dir)
        self.embedder = Embedder(backup_mgr)

    def run(self):
        try:
            total = len(self.song_ids)
            embedded_count = 0
            failed_count = 0
            
            all_songs = {s["id"]: s for s in self.db.get_all_songs()}

            for idx, song_id in enumerate(self.song_ids):
                song = all_songs.get(song_id)
                if not song:
                    continue
                if not self.only_write_integrity and not song.get("lyric_id"):
                    continue

                song_name = Path(song["file_path"]).name
                self.log.emit(f"Processing: {song_name}")
                self.progress.emit(int((idx / total) * 100), f"Writing tags: {idx+1}/{total}")

                legit_info = {
                    "actual_sample_rate": song.get("actual_sample_rate"),
                    "spectral_cutoff": song.get("spectral_cutoff"),
                    "legit": song.get("legit"),
                    "reason": song.get("legit_reason")
                }

                if self.only_write_integrity:
                    backup_path = self.embedder.backup_manager.create_backup(song["file_path"])
                    if not backup_path:
                        self.db.update_song_status(song_id, "Failed")
                        failed_count += 1
                        self.log.emit(f"  [FAILED] Failed to create safety backup.")
                        continue
                        
                    success, msg = AudioVerifier.write_legitimacy_tags(song["file_path"], legit_info)
                    if success:
                        self.db.update_song_status(song_id, "Embedded")
                        embedded_count += 1
                        self.log.emit(f"  [SUCCESS] {msg}")
                        if not self.keep_backup:
                            self.embedder.backup_manager.remove_backup(backup_path)
                    else:
                        self.db.update_song_status(song_id, "Failed")
                        failed_count += 1
                        self.log.emit(f"  [FAILED] {msg}")
                        self.embedder.backup_manager.restore_backup(song["file_path"], backup_path)
                        if not self.keep_backup:
                            self.embedder.backup_manager.remove_backup(backup_path)
                else:
                    lyrics_text = song.get("lyrics_text", "")
                    success, msg = self.embedder.embed_lyrics(song["file_path"], lyrics_text, self.keep_backup, legit_info)
                    if success:
                        self.db.update_song_status(song_id, "Embedded")
                        embedded_count += 1
                        self.log.emit(f"  [SUCCESS] {msg}")
                    else:
                        self.db.update_song_status(song_id, "Failed")
                        failed_count += 1
                        self.log.emit(f"  [FAILED] {msg}")

            self.progress.emit(100, "Embedding processes complete.")
            self.finished.emit({"embedded": embedded_count, "failed": failed_count})
        except Exception as e:
            self.log.emit(f"Embed Exception: {e}")
            self.finished.emit({"error": str(e)})


class LyricForgeWindow(QMainWindow):
    """
    Main LyricForge Resizable Desktop Application Window.
    """
    BORDER_MARGIN = 10

    def __init__(self, db_path: str = "lyricforge.db"):
        super().__init__()
        self.db = DBManager(db_path)
        self.mode = "lyrics"
        self.setWindowTitle("LyricForge Pro")
        self.setMinimumSize(960, 600)
        
        # Frameless window configuration
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Window Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.resize(1260, 800)
        self.setStyleSheet(NOTHING_OS_QSS)

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        central.setObjectName("central")
        central.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Nothing OS HeaderBar
        self.header_bar = GNOMEHeaderBar(self)
        self.header_bar.search_changed.connect(self.on_search_filter_changed)
        self.header_bar.page_changed.connect(self.on_page_changed)
        main_layout.addWidget(self.header_bar)

        # 2. Main Body Container (Sidebar + Stacked Content Workspaces)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar Navigation
        self.sidebar = GNOMESidebar(self)
        self.sidebar.page_changed.connect(self.on_page_changed)
        body_layout.addWidget(self.sidebar)

        # Content Workspaces Stack
        self.stack = QStackedWidget()
        
        self.page_library = self.create_library_page()
        self.page_audio = self.create_audio_page()
        self.page_reports = self.create_reports_page()
        self.page_settings = self.create_settings_page()

        self.stack.addWidget(self.page_library)
        self.stack.addWidget(self.page_audio)
        self.stack.addWidget(self.page_reports)
        self.stack.addWidget(self.page_settings)

        body_layout.addWidget(self.stack, 1)
        main_layout.addWidget(body_widget, 1)

        # Bottom Right QSizeGrip for Resize Dragging
        sizegrip = QSizeGrip(self)
        sizegrip.setStyleSheet("width: 16px; height: 16px; background: transparent;")
        main_layout.addWidget(sizegrip, 0, Qt.AlignBottom | Qt.AlignRight)

        # Toast notification overlay
        self.toast = GNOMEToast(self)

        self.load_table_data()

    # =========================================================================
    # NATIVE WINDOW RESIZING & MAXIMIZE LOGIC
    # =========================================================================

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.header_bar.update_max_button_icon(False)
        else:
            self.showMaximized()
            self.header_bar.update_max_button_icon(True)

    def nativeEvent(self, eventType, message):
        if sys.platform == "win32":
            try:
                if eventType in (b"windows_generic_MSG", "windows_generic_MSG"):
                    msg = ctypes.wintypes.MSG.from_address(int(message))
                    WM_NCHITTEST = 0x0084
                    if msg.message == WM_NCHITTEST and not self.isMaximized():
                        x = ctypes.c_short(msg.lParam & 0xFFFF).value
                        y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
                        
                        local_pos = self.mapFromGlobal(QPoint(x, y))
                        lx = local_pos.x()
                        ly = local_pos.y()
                        w = self.width()
                        h = self.height()
                        m = self.BORDER_MARGIN
                        
                        if lx < m and ly < m:
                            return True, 13  # HTTOPLEFT
                        elif lx > w - m and ly < m:
                            return True, 14  # HTTOPRIGHT
                        elif lx < m and ly > h - m:
                            return True, 16  # HTBOTTOMLEFT
                        elif lx > w - m and ly > h - m:
                            return True, 17  # HTBOTTOMRIGHT
                        elif lx < m:
                            return True, 10  # HTLEFT
                        elif lx > w - m:
                            return True, 11  # HTRIGHT
                        elif ly < m:
                            return True, 12  # HTTOP
                        elif ly > h - m:
                            return True, 15  # HTBOTTOM
            except Exception:
                pass

        return super().nativeEvent(eventType, message)

    # =========================================================================
    # WORKSPACE PAGES BUILDERS
    # =========================================================================

    def create_library_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(14)

        # 1. Active Folders Banner Card
        self.folders_banner = QFrame()
        self.folders_banner.setObjectName("cardFrame")
        self.folders_banner.setAttribute(Qt.WA_StyledBackground, True)
        fb_lay = QHBoxLayout(self.folders_banner)
        fb_lay.setContentsMargins(16, 12, 16, 12)
        fb_lay.setSpacing(16)

        self.lbl_paths_info = QLabel("No music or lyrics folders configured.")
        self.lbl_paths_info.setStyleSheet(f"font-size: 9.5pt; color: {TEXT_SECONDARY};")
        fb_lay.addWidget(self.lbl_paths_info, 1)

        btn_change_paths = QPushButton("⚙️ CHANGE FOLDERS")
        btn_change_paths.setStyleSheet("padding: 5px 12px; font-size: 8.5pt; font-weight: 800; letter-spacing: 0.5px;")
        btn_change_paths.clicked.connect(self.show_settings_popup)
        fb_lay.addWidget(btn_change_paths)

        layout.addWidget(self.folders_banner)

        # 2. Header Toolbar Area
        header_lay = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_title = QLabel(":: LIBRARY ::")
        lbl_title.setProperty("class", "pageTitle")
        lbl_sub = QLabel("Match lyrics and embed synchronized metadata into your audio library.")
        lbl_sub.setProperty("class", "pageSubtitle")

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_sub)
        header_lay.addLayout(header_text)
        header_lay.addStretch()

        self.btn_choose_folder = QPushButton("📁 CHOOSE MUSIC FOLDER")
        self.btn_choose_folder.clicked.connect(lambda: self.browse_folder("music"))
        
        self.scan_btn = QPushButton("🔴 SCAN LIBRARY")
        self.scan_btn.setObjectName("primaryButton")
        self.scan_btn.clicked.connect(self.start_scan)

        header_lay.addWidget(self.btn_choose_folder)
        header_lay.addWidget(self.scan_btn)
        layout.addLayout(header_lay)

        # 3. Nothing OS Metric Capsules Area
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(14)

        def make_stat_card(num_code: str, label_text: str, color_hex: str):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setAttribute(Qt.WA_StyledBackground, True)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(16, 12, 16, 12)
            c_lay.setSpacing(2)

            top_lay = QHBoxLayout()
            lbl_num = QLabel(num_code)
            lbl_num.setStyleSheet(f"font-size: 8.5pt; font-weight: 900; color: {ACCENT_RED}; letter-spacing: 1px; border: none; background: transparent;")
            lbl_tit = QLabel(label_text)
            lbl_tit.setStyleSheet(f"font-size: 8pt; font-weight: 800; color: {TEXT_SECONDARY}; text-transform: uppercase; letter-spacing: 1px; border: none; background: transparent;")
            top_lay.addWidget(lbl_num)
            top_lay.addWidget(lbl_tit, 1)
            c_lay.addLayout(top_lay)

            val_lbl = QLabel("0")
            val_lbl.setStyleSheet(f"font-size: 20pt; font-weight: 900; color: {color_hex}; border: none; background: transparent;")
            c_lay.addWidget(val_lbl)
            return val_lbl, card

        self.lbl_stat_total, card1 = make_stat_card("01 //", "TOTAL TRACKS", TEXT_PRIMARY)
        self.lbl_stat_matched, card2 = make_stat_card("02 //", "MATCHED LYRICS", COLOR_SUCCESS)
        self.lbl_stat_unmatched, card3 = make_stat_card("03 //", "UNMATCHED", TEXT_MUTED)
        self.lbl_stat_suspicious, card4 = make_stat_card("04 //", "NEEDS REVIEW", COLOR_WARNING)

        stats_lay.addWidget(card1)
        stats_lay.addWidget(card2)
        stats_lay.addWidget(card3)
        stats_lay.addWidget(card4)

        layout.addLayout(stats_lay)

        # 4. Main Workspace Splitter (Track List & Responsive Detail Pane)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(12)
        self.splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Left Container: Track List + Empty State Overlay
        left_container = QWidget()
        left_lay = QVBoxLayout(left_container)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.horizontalHeader().setMinimumHeight(36)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.itemClicked.connect(self.table_row_clicked)
        self.table.itemChanged.connect(self.on_table_item_changed)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)

        left_lay.addWidget(self.table)

        self.empty_state = GNOMEEmptyState(
            "🔴",
            "NO MUSIC LIBRARY SCANNED",
            "Select your music library folder to begin matching lyrics and verifying audio files.",
            "CHOOSE MUSIC FOLDER"
        )
        self.empty_state.action_clicked.connect(lambda: self.browse_folder("music"))
        left_lay.addWidget(self.empty_state)

        self.splitter.addWidget(left_container)

        # Right Container: Track Details & Lyrics Preview Drawer
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(340)

        right_card = QFrame()
        right_card.setObjectName("cardFrame")
        right_card.setAttribute(Qt.WA_StyledBackground, True)
        right_lay = QVBoxLayout(right_card)
        right_lay.setContentsMargins(18, 18, 18, 18)
        right_lay.setSpacing(16)

        # Track Hero Card Header (Nothing OS Glyph Style)
        hero_box = QFrame()
        hero_box.setStyleSheet("background-color: #0e1014; border: 1px solid #292d38; border-radius: 8px; padding: 12px;")
        hero_lay = QHBoxLayout(hero_box)
        hero_lay.setContentsMargins(8, 8, 8, 8)
        hero_lay.setSpacing(12)

        lbl_hero_art = QLabel("🔴")
        lbl_hero_art.setStyleSheet(f"font-size: 24pt; color: {ACCENT_RED}; background: transparent; border: none;")
        hero_lay.addWidget(lbl_hero_art)

        self.meta_info_lbl = QLabel("Select a track from the list to view details.")
        self.meta_info_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 9.5pt; line-height: 18px; background: transparent; border: none;")
        self.meta_info_lbl.setWordWrap(True)
        hero_lay.addWidget(self.meta_info_lbl, 1)

        right_lay.addWidget(hero_box)

        # Lyrics Editor Preview
        lyrics_hdr = QLabel(":: LYRICS PREVIEW ::")
        lyrics_hdr.setProperty("class", "sectionTitle")
        right_lay.addWidget(lyrics_hdr)

        self.lyric_preview = QTextEdit()
        self.lyric_preview.setPlaceholderText("Select a track with matched lyrics...")
        self.lyric_preview.setFixedHeight(180)
        self.lyric_preview.textChanged.connect(self.on_lyrics_text_edited)
        right_lay.addWidget(self.lyric_preview)

        # Audio Analysis
        audio_hdr = QLabel(":: SPECTRAL VERIFICATION ::")
        audio_hdr.setProperty("class", "sectionTitle")
        right_lay.addWidget(audio_hdr)

        self.spec_verdict_lbl = QLabel("Select a track to verify cutoff frequencies.")
        self.spec_verdict_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 9.5pt;")
        self.spec_verdict_lbl.setWordWrap(True)
        right_lay.addWidget(self.spec_verdict_lbl)

        self.plot_btn = QPushButton("📈 PLOT SPECTRUM GRAPH")
        self.plot_btn.clicked.connect(self.plot_selected_spectrum)
        self.plot_btn.setEnabled(False)
        right_lay.addWidget(self.plot_btn)

        self.plot_img_lbl = QLabel()
        self.plot_img_lbl.setAlignment(Qt.AlignCenter)
        self.plot_img_lbl.setVisible(False)
        right_lay.addWidget(self.plot_img_lbl)

        # Quick Actions
        actions_hdr = QLabel(":: ACTIONS ::")
        actions_hdr.setProperty("class", "sectionTitle")
        right_lay.addWidget(actions_hdr)

        act_lay = QVBoxLayout()
        act_lay.setSpacing(8)

        self.check_tags_btn = QPushButton("🔍 VERIFY FILE TAGS")
        self.check_tags_btn.setEnabled(False)
        self.check_tags_btn.clicked.connect(self.check_file_tags)

        self.manual_match_btn = QPushButton("🔗 SELECT LYRIC FILE...")
        self.manual_match_btn.setEnabled(False)
        self.manual_match_btn.clicked.connect(self.manual_match_lyric)

        act_lay.addWidget(self.check_tags_btn)
        act_lay.addWidget(self.manual_match_btn)
        right_lay.addLayout(act_lay)

        right_lay.addStretch()
        right_scroll.setWidget(right_card)

        self.splitter.addWidget(right_scroll)
        self.splitter.setSizes([680, 360])

        layout.addWidget(self.splitter, 1)

        # 5. Sticky Bottom Action Bar
        bottom_bar = QFrame()
        bottom_bar.setObjectName("cardFrame")
        bottom_bar.setAttribute(Qt.WA_StyledBackground, True)
        bottom_lay = QHBoxLayout(bottom_bar)
        bottom_lay.setContentsMargins(16, 10, 16, 10)
        bottom_lay.setSpacing(16)

        self.center_status_lbl = QLabel("READY")
        self.center_status_lbl.setStyleSheet(f"font-size: 9.5pt; font-weight: 700; color: {TEXT_SECONDARY}; letter-spacing: 1px;")
        bottom_lay.addWidget(self.center_status_lbl, 1)

        self.center_progress = QProgressBar()
        self.center_progress.setFixedWidth(160)
        bottom_lay.addWidget(self.center_progress)

        self.embed_selected_btn = QPushButton("🔴 EMBED SELECTED LYRICS")
        self.embed_selected_btn.setObjectName("primaryButton")
        self.embed_selected_btn.setEnabled(False)
        self.embed_selected_btn.clicked.connect(self.embed_selected)
        bottom_lay.addWidget(self.embed_selected_btn)

        layout.addWidget(bottom_bar)
        self.update_folders_banner()
        return page

    def create_audio_page(self) -> QWidget:
        """
        Full-featured Audio Inspector Workspace.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(14)

        # Header
        header_lay = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_title = QLabel(":: AUDIO INSPECTOR ::")
        lbl_title.setProperty("class", "pageTitle")
        lbl_sub = QLabel("Analyze sample rates, bit depths, bitrates, and spectral cutoff frequencies.")
        lbl_sub.setProperty("class", "pageSubtitle")

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_sub)
        header_lay.addLayout(header_text)
        header_lay.addStretch()

        btn_inspect = QPushButton("🔴 INSPECT AUDIO INTEGRITY")
        btn_inspect.setObjectName("primaryButton")
        btn_inspect.clicked.connect(self.start_scan)
        header_lay.addWidget(btn_inspect)

        layout.addLayout(header_lay)

        # Filter Toolbar
        filter_bar = QFrame()
        filter_bar.setObjectName("cardFrame")
        fb_lay = QHBoxLayout(filter_bar)
        fb_lay.setContentsMargins(16, 10, 16, 10)
        fb_lay.setSpacing(12)

        lbl_filter = QLabel("FILTER STATUS:")
        lbl_filter.setStyleSheet(f"font-size: 9pt; font-weight: 800; color: {TEXT_SECONDARY}; letter-spacing: 1px;")
        fb_lay.addWidget(lbl_filter)

        self.audio_filter_combo = QComboBox()
        self.audio_filter_combo.addItems(["All Tracks", "Genuine Hi-Res", "Possible Upscales", "Fake Lossless"])
        self.audio_filter_combo.currentTextChanged.connect(self.filter_audio_table)
        fb_lay.addWidget(self.audio_filter_combo)

        fb_lay.addStretch()
        layout.addWidget(filter_bar)

        # Audio Files Table
        self.audio_table = QTableWidget()
        self.audio_table.setAlternatingRowColors(True)
        self.audio_table.setShowGrid(False)
        self.audio_table.verticalHeader().setVisible(False)
        self.audio_table.verticalHeader().setDefaultSectionSize(42)
        self.audio_table.horizontalHeader().setMinimumHeight(36)
        self.audio_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.audio_table.setColumnCount(10)
        self.audio_table.setHorizontalHeaderLabels([
            "FILE NAME", "SAMPLE RATE", "BITS", "CH", "DURATION", 
            "SIZE", "BITRATE", "FORMAT", "MAX FREQ", "STATUS"
        ])
        self.audio_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.audio_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.audio_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)

        layout.addWidget(self.audio_table, 1)
        return page

    def create_reports_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(16)

        # Header
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_title = QLabel(":: REPORTS & LOGS ::")
        lbl_title.setProperty("class", "pageTitle")
        lbl_sub = QLabel("Export detailed matching summary reports or filter real-time process logs.")
        lbl_sub.setProperty("class", "pageSubtitle")

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_sub)
        layout.addLayout(header_text)

        # Report Export Card
        export_card = QFrame()
        export_card.setObjectName("cardFrame")
        export_lay = QVBoxLayout(export_card)
        export_lay.setContentsMargins(18, 18, 18, 18)
        export_lay.setSpacing(12)

        lbl_exp_title = QLabel(":: EXPORT REPORT ::")
        lbl_exp_title.setProperty("class", "sectionTitle")
        export_lay.addWidget(lbl_exp_title)

        exp_btns_lay = QHBoxLayout()
        btn_exp_html = QPushButton("📄 HTML REPORT")
        btn_exp_html.clicked.connect(lambda: self.export_report("html"))

        btn_exp_txt = QPushButton("📝 TEXT SUMMARY")
        btn_exp_txt.clicked.connect(lambda: self.export_report("txt"))

        btn_exp_json = QPushButton("⚙️ JSON RAW DATA")
        btn_exp_json.clicked.connect(lambda: self.export_report("json"))

        exp_btns_lay.addWidget(btn_exp_html)
        exp_btns_lay.addWidget(btn_exp_txt)
        exp_btns_lay.addWidget(btn_exp_json)
        export_lay.addLayout(exp_btns_lay)

        layout.addWidget(export_card)

        # Process Logs Card
        logs_card = QFrame()
        logs_card.setObjectName("cardFrame")
        logs_lay = QVBoxLayout(logs_card)
        logs_lay.setContentsMargins(18, 18, 18, 18)
        logs_lay.setSpacing(10)

        logs_hdr = QHBoxLayout()
        lbl_logs_title = QLabel(":: PROCESS LOGS ::")
        lbl_logs_title.setProperty("class", "sectionTitle")

        self.logs_search = QLineEdit()
        self.logs_search.setPlaceholderText("Filter logs...")
        self.logs_search.setFixedWidth(200)
        self.logs_search.setClearButtonEnabled(True)
        self.logs_search.textChanged.connect(self.filter_logs)

        logs_hdr.addWidget(lbl_logs_title)
        logs_hdr.addStretch()
        logs_hdr.addWidget(self.logs_search)
        logs_lay.addLayout(logs_hdr)

        self.logs_txt = QTextEdit()
        self.logs_txt.setReadOnly(True)
        self.logs_txt.setFont(QFont("Courier New", 9))
        logs_lay.addWidget(self.logs_txt, 1)

        layout.addWidget(logs_card, 1)
        return page

    def create_settings_page(self) -> QWidget:
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(20)

        # Header
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_title = QLabel(":: PREFERENCES ::")
        lbl_title.setProperty("class", "pageTitle")
        lbl_sub = QLabel("Configure library folders, matching presets, threshold, and backup preferences.")
        lbl_sub.setProperty("class", "pageSubtitle")

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_sub)
        layout.addLayout(header_text)

        # 1. MUSIC LIBRARY FOLDERS GROUP
        grp1_lbl = QLabel(":: MUSIC LIBRARY FOLDERS ::")
        grp1_lbl.setProperty("class", "sectionTitle")
        layout.addWidget(grp1_lbl)

        self.music_dir_txt = DragDropLineEdit()
        self.music_dir_txt.setText(self.db.get_setting("music_dir", ""))
        self.music_dir_txt.setPlaceholderText("Music folder path...")
        btn_b1 = QPushButton("Browse...")
        btn_b1.clicked.connect(lambda: self.browse_folder("music"))
        lay_music = QHBoxLayout()
        lay_music.addWidget(self.music_dir_txt, 1)
        lay_music.addWidget(btn_b1)
        w_music = QWidget()
        w_music.setLayout(lay_music)

        row_music = GNOMESettingsRow("Music Folder", "Primary directory containing your audio files.", w_music)
        layout.addWidget(row_music)

        self.lyrics_dir_txt = DragDropLineEdit()
        self.lyrics_dir_txt.setText(self.db.get_setting("lyrics_dir", ""))
        self.lyrics_dir_txt.setPlaceholderText("Lyrics folder path...")
        btn_b2 = QPushButton("Browse...")
        btn_b2.clicked.connect(lambda: self.browse_folder("lyrics"))
        lay_lyrics = QHBoxLayout()
        lay_lyrics.addWidget(self.lyrics_dir_txt, 1)
        lay_lyrics.addWidget(btn_b2)
        w_lyrics = QWidget()
        w_lyrics.setLayout(lay_lyrics)

        row_lyrics = GNOMESettingsRow("Lyrics Folder", "Directory containing .lrc or .ttml synced lyric files.", w_lyrics)
        layout.addWidget(row_lyrics)

        # 2. MATCHING ENGINE GROUP
        grp2_lbl = QLabel(":: MATCHING ALGORITHM ::")
        grp2_lbl.setProperty("class", "sectionTitle")
        layout.addWidget(grp2_lbl)

        # Preset Combo
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Fast", "Balanced", "Strict"])
        self.preset_combo.setCurrentText("Balanced")
        self.preset_combo.currentTextChanged.connect(lambda txt: self.set_preset(txt.lower()))

        row_preset = GNOMESettingsRow("Preset Profile", "Adjust matching confidence strictness.", self.preset_combo)
        layout.addWidget(row_preset)

        # Threshold Slider
        saved_threshold = float(self.db.get_setting("threshold", "60.0"))
        thresh_container = QWidget()
        thresh_lay = QHBoxLayout(thresh_container)
        thresh_lay.setContentsMargins(0, 0, 0, 0)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(30, 100)
        self.threshold_slider.setValue(int(saved_threshold))
        self.threshold_slider.setFixedWidth(160)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)

        self.threshold_lbl = QLabel(f"{int(saved_threshold)}%")
        self.threshold_lbl.setStyleSheet(f"color: {ACCENT_RED}; font-weight: bold;")

        thresh_lay.addWidget(self.threshold_slider)
        thresh_lay.addWidget(self.threshold_lbl)

        row_thresh = GNOMESettingsRow("Match Threshold", "Minimum confidence score required for a lyric match.", thresh_container)
        layout.addWidget(row_thresh)

        # Weights Sliders
        weights_container = QWidget()
        w_lay = QVBoxLayout(weights_container)
        w_lay.setContentsMargins(0, 0, 0, 0)
        w_lay.setSpacing(6)

        def make_weight_slider(name: str, default_val: int):
            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 100)
            sl.setValue(default_val)
            sl.setFixedWidth(120)
            lb = QLabel(f"{default_val}%")
            sl.valueChanged.connect(lambda v: lb.setText(f"{v}%"))
            r_lay = QHBoxLayout()
            r_lay.addWidget(QLabel(f"{name}:"))
            r_lay.addWidget(sl)
            r_lay.addWidget(lb)
            return sl, r_lay

        self.w_title_slider, r1 = make_weight_slider("Title", 40)
        self.w_artist_slider, r2 = make_weight_slider("Artist", 30)
        self.w_album_slider, r3 = make_weight_slider("Album", 15)
        self.w_filename_slider, r4 = make_weight_slider("File", 10)

        w_lay.addLayout(r1)
        w_lay.addLayout(r2)
        w_lay.addLayout(r3)
        w_lay.addLayout(r4)

        row_weights = GNOMESettingsRow("Weight Matrix", "Fuzzy matching relevance weights.", weights_container)
        layout.addWidget(row_weights)

        # 3. BACKUP & VERIFICATION GROUP
        grp3_lbl = QLabel(":: SAFETY & VERIFICATION ::")
        grp3_lbl.setProperty("class", "sectionTitle")
        layout.addWidget(grp3_lbl)

        self.backup_chk = QCheckBox()
        self.backup_chk.setChecked(self.db.get_setting("keep_backup", "True") == "True")
        row_backup = GNOMESettingsRow("Backup Audio Files", "Create backup copies before modifying audio tags.", self.backup_chk)
        layout.addWidget(row_backup)

        self.verify_chk = QCheckBox()
        self.verify_chk.setChecked(self.db.get_setting("verify_audio", "True") == "True")
        row_verify = GNOMESettingsRow("Inspect Audio Integrity", "Check spectral cutoff frequencies for fake upscales.", self.verify_chk)
        layout.addWidget(row_verify)

        # Reset Library Button
        btn_reset_lib = QPushButton("⚠️ RESET LIBRARY DATA")
        btn_reset_lib.setObjectName("destructiveButton")
        btn_reset_lib.clicked.connect(self.reset_library)
        row_reset = GNOMESettingsRow("Clear Database", "Delete all cached library records, tracks, and matches.", btn_reset_lib)
        layout.addWidget(row_reset)

        layout.addStretch()
        scroll.setWidget(content)

        page_lay = QVBoxLayout(page)
        page_lay.setContentsMargins(0, 0, 0, 0)
        page_lay.addWidget(scroll)
        return page

    # =========================================================================
    # EVENT HANDLERS & NAVIGATION
    # =========================================================================

    def update_folders_banner(self):
        m_path = self.db.get_setting("music_dir", "")
        l_path = self.db.get_setting("lyrics_dir", "")

        if m_path or l_path:
            m_name = Path(m_path).name if m_path else "Not set"
            l_name = Path(l_path).name if l_path else "Not set"
            self.lbl_paths_info.setText(f"📁 <b>Music Folder:</b> {m_name} &nbsp;&nbsp;|&nbsp;&nbsp; 📝 <b>Lyrics Folder:</b> {l_name}")
            self.folders_banner.setVisible(True)
        else:
            self.lbl_paths_info.setText("No music or lyrics folders configured.")

    def on_page_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        self.sidebar.set_active_page(index)
        self.header_bar.set_active_segment(index)
        if index == 1:
            self.load_audio_inspector_table()

    def browse_folder(self, folder_type: str):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec():
            selected = dialog.selectedFiles()[0]
            if folder_type == "music":
                self.music_dir_txt.setText(selected)
                self.db.set_setting("music_dir", selected)
            else:
                self.lyrics_dir_txt.setText(selected)
                self.db.set_setting("lyrics_dir", selected)
            self.update_folders_banner()

    def on_search_filter_changed(self, text: str):
        text = text.lower().strip()
        for row in range(self.table.rowCount()):
            match_found = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match_found = True
                    break
            self.table.setRowHidden(row, not match_found)

    def show_reports_popup(self):
        self.on_page_changed(2)

    def show_settings_popup(self):
        self.on_page_changed(3)

    def reset_library(self):
        reply = QMessageBox.question(
            self, "Reset Library",
            "Are you sure you want to clear all tracks, lyrics, and matched database data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.clear_songs()
            self.db.clear_lyrics()
            self.db.clear_matches()
            self.load_table_data()
            self.lbl_stat_total.setText("0")
            self.lbl_stat_matched.setText("0")
            self.lbl_stat_unmatched.setText("0")
            self.lbl_stat_suspicious.setText("0")
            self.toast.show_message("Library database cleared.", "🗑")

    def export_library_reports(self):
        self.export_report("html")

    def on_suspicious_stat_changed(self, value: str):
        self.lbl_stat_suspicious.setText(value)

    def render_lyrics_html(self, text: str) -> str:
        if not text:
            return "<span style='color:#707070;'>No lyrics loaded.</span>"
        import re
        lines = []
        for line in text.splitlines():
            match = re.match(r'^(\[[0-9:.]+\])(.*)', line)
            if match:
                time_tag = match.group(1)
                content = match.group(2)
                lines.append(f"<span style='color:{ACCENT_RED}; font-family:Courier New; font-weight:bold;'>{time_tag}</span> <span style='color:#ffffff;'>{content}</span>")
            else:
                lines.append(f"<span style='color:#ffffff;'>{line}</span>")
        return "<br>".join(lines)

    def set_progress_smooth(self, bar, value):
        self.anim = QPropertyAnimation(bar, b"value", self)
        self.anim.setDuration(180)
        self.anim.setStartValue(bar.value())
        self.anim.setEndValue(value)
        self.anim.start()

    def show_table_context_menu(self, position):
        menu = QMenu(self)
        act_tag = menu.addAction("🔍 Verify File Tag")
        act_tag.setEnabled(hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_match = menu.addAction("🔗 Manual Lyric Match...")
        act_match.setEnabled(hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_plot = menu.addAction("📈 Plot Spectrum Graph")
        act_plot.setEnabled(hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_export = menu.addAction("📊 Export Library Report")
        
        action = menu.exec(self.table.mapToGlobal(position))
        if action == act_tag:
            self.check_file_tags()
        elif action == act_match:
            self.manual_match_lyric()
        elif action == act_plot:
            self.plot_selected_spectrum()
        elif action == act_export:
            self.export_report("html")

    def switch_to_lyrics_mode(self):
        self.mode = "lyrics"
        self.load_table_data()

    def switch_to_audio_mode(self):
        self.mode = "audio"
        self.load_table_data()

    def on_threshold_changed(self, val: int):
        self.threshold_lbl.setText(f"{val}%")

    def set_preset(self, preset_name: str):
        if preset_name == "fast":
            self.threshold_slider.setValue(40)
            self.threshold_lbl.setText("40%")
        elif preset_name == "balanced":
            self.threshold_slider.setValue(60)
            self.threshold_lbl.setText("60%")
        elif preset_name == "strict":
            self.threshold_slider.setValue(85)
            self.threshold_lbl.setText("85%")

    def toggle_advanced_panel(self):
        self.show_settings_popup()

    def on_lyrics_text_edited(self):
        if hasattr(self, 'selected_song') and self.selected_song:
            self.selected_song["lyrics_text"] = self.lyric_preview.toPlainText()

    def filter_logs(self, text: str):
        if not hasattr(self, 'full_log_lines'):
            return
        filtered = [line for line in self.full_log_lines if text.lower() in line.lower()]
        self.logs_txt.setPlainText("\n".join(filtered))
        self.logs_txt.moveCursor(self.logs_txt.textCursor().End)

    def start_scan(self):
        music_path = self.music_dir_txt.text().strip()
        if not music_path or not os.path.exists(music_path):
            QMessageBox.warning(self, "Invalid Path", "Please select a valid Music library folder.")
            return

        self.db.set_setting("music_dir", music_path)
        self.center_progress.setValue(0)
        if hasattr(self, 'logs_txt'):
            self.logs_txt.clear()
        self.full_log_lines = []

        if self.mode == "audio":
            self.db.set_setting("keep_backup", "True" if self.backup_chk.isChecked() else "False")
            self.center_status_lbl.setText("INSPECTING AUDIO INTEGRITY...")
            self.scan_worker = ScanWorker(self.db, music_path, "", 0.0, True, None)
        else:
            lyrics_path = self.lyrics_dir_txt.text().strip()
            threshold = float(self.threshold_slider.value())

            if not lyrics_path or not os.path.exists(lyrics_path):
                QMessageBox.warning(self, "Invalid Path", "Please select a valid Lyrics folder.")
                return

            self.db.set_setting("lyrics_dir", lyrics_path)
            self.db.set_setting("threshold", str(threshold))
            self.db.set_setting("keep_backup", "True" if self.backup_chk.isChecked() else "False")
            self.db.set_setting("verify_audio", "True" if self.verify_chk.isChecked() else "False")

            self.center_status_lbl.setText("SCANNING LIBRARY...")
            
            verify_audio = self.verify_chk.isChecked()
            custom_weights = {
                "title": self.w_title_slider.value() / 100.0,
                "artist": self.w_artist_slider.value() / 100.0,
                "album": self.w_album_slider.value() / 100.0,
                "filename": self.w_filename_slider.value() / 100.0,
                "duration": 0.05
            }
            self.scan_worker = ScanWorker(self.db, music_path, lyrics_path, threshold, verify_audio, custom_weights)

        self.scan_worker.progress.connect(self.on_scan_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()

    @Slot(int, str)
    def on_scan_progress(self, val: int, status_text: str):
        self.set_progress_smooth(self.center_progress, val)
        self.center_status_lbl.setText(status_text.upper())

    @Slot(dict)
    def on_scan_finished(self, stats: dict):
        if "error" in stats:
            QMessageBox.critical(self, "Scan Error", f"Scan failed: {stats['error']}")
            return

        self.load_table_data()
        
        songs = self.db.get_all_songs()
        total = len(songs)
        matched = sum(1 for s in songs if s.get("lyric_id"))
        unmatched = total - matched
        suspicious = sum(1 for s in songs if s.get("legit") == 0 and s.get("spectral_cutoff"))
        
        self.lbl_stat_total.setText(str(total))
        self.lbl_stat_matched.setText(str(matched))
        self.lbl_stat_unmatched.setText(str(unmatched))
        self.lbl_stat_suspicious.setText(str(suspicious))

        self.toast.show_message(f"Library scanned: {total} tracks found ({matched} matched).", "🔴")

    def load_table_data(self):
        self.selected_song = None
        self.check_tags_btn.setEnabled(False)
        self.manual_match_btn.setEnabled(False)
        self.plot_btn.setEnabled(False)
        self.plot_img_lbl.setVisible(False)
        
        self.meta_info_lbl.setText("Select a track from the list to view details.")
        self.spec_verdict_lbl.setText("Select a song to review audio integrity verification.")
        self.lyric_preview.setPlainText("Select a song with matched lyrics to preview/edit.")

        self.table.blockSignals(True)
        
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["", "SONG TITLE", "ARTIST", "ALBUM", "TIME", "SCORE", "STATUS"])
        self.table.setColumnWidth(0, 32)
        self.table.setColumnWidth(4, 75)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        songs = self.db.get_all_songs()
        self.table_songs = songs
        
        has_songs = len(songs) > 0
        self.empty_state.setVisible(not has_songs)
        self.table.setVisible(has_songs)
        
        self.table.setRowCount(len(songs))

        for row, song in enumerate(songs):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if song["status"] in ["Matched", "Embedded"]:
                chk_item.setCheckState(Qt.Checked)
            else:
                chk_item.setCheckState(Qt.Unchecked)
            self.table.setItem(row, 0, chk_item)

            title_text = song["title"] or Path(song["file_path"]).name
            title_item = QTableWidgetItem(title_text)
            if song.get("legit") == 0 and song.get("spectral_cutoff"):
                title_item.setForeground(QBrush(QColor(COLOR_WARNING)))
                title_item.setToolTip(song.get("legit_reason", "Fake upscale or transcode detected"))
            self.table.setItem(row, 1, title_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(song["artist"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(song["album"] or ""))
            
            dur = song.get("duration", 0.0)
            if dur > 0:
                minutes = int(dur) // 60
                seconds = int(dur) % 60
                dur_txt = f"{minutes}:{seconds:02d}"
            else:
                dur_txt = "-"
            self.table.setItem(row, 4, QTableWidgetItem(dur_txt))

            score_val = 0.0
            score_txt = "-"
            if song["lyric_id"]:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT score FROM matches WHERE song_id = ? AND lyric_id = ?", (song["id"], song["lyric_id"]))
                    row_match = cursor.fetchone()
                    if row_match:
                        score_val = float(row_match['score'])
                        score_txt = f"{score_val:.1f}%"
            score_item = QTableWidgetItem(score_txt)
            score_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, score_item)

            thresh = float(self.threshold_slider.value())
            if song["status"] in ["Embedded", "Matched"]:
                if score_val >= 99.9:
                    status_str = "MATCHED"
                    status_color = COLOR_SUCCESS
                elif score_val >= thresh:
                    status_str = "PARTIAL"
                    status_color = COLOR_WARNING
                else:
                    status_str = "UNMATCHED"
                    status_color = COLOR_ERROR
            else:
                status_str = "UNMATCHED"
                status_color = COLOR_ERROR

            status_item = QTableWidgetItem(status_str)
            status_item.setForeground(QBrush(QColor(status_color)))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, status_item)

        self.table.blockSignals(False)
        self.update_embed_btn_label()

    def load_audio_inspector_table(self):
        songs = self.db.get_all_songs()
        self.audio_table.setRowCount(len(songs))
        
        for row, song in enumerate(songs):
            filename = Path(song["file_path"]).name
            self.audio_table.setItem(row, 0, QTableWidgetItem(filename))
            
            sr_val = song.get("sample_rate")
            sr_txt = f"{sr_val:,} Hz" if sr_val else "-"
            self.audio_table.setItem(row, 1, QTableWidgetItem(sr_txt))
            
            bits_val = song.get("bits_per_sample")
            bits_txt = str(bits_val) if bits_val else "-"
            self.audio_table.setItem(row, 2, QTableWidgetItem(bits_txt))
            
            ch_val = song.get("channels")
            ch_txt = "Mono" if ch_val == 1 else "Stereo" if ch_val == 2 else f"{ch_val} Ch" if ch_val else "-"
            self.audio_table.setItem(row, 3, QTableWidgetItem(ch_txt))
            
            dur = song.get("duration", 0.0)
            if dur > 0:
                minutes = int(dur) // 60
                seconds = int(dur) % 60
                dur_txt = f"{minutes}:{seconds:02d}"
            else:
                dur_txt = "-"
            self.audio_table.setItem(row, 4, QTableWidgetItem(dur_txt))
            
            size_val = song.get("file_size")
            size_txt = f"{size_val / (1024 * 1024):.1f} MB" if size_val else "-"
            self.audio_table.setItem(row, 5, QTableWidgetItem(size_txt))
            
            br_val = song.get("bitrate")
            br_txt = f"{int(br_val)} kbps" if br_val else "-"
            self.audio_table.setItem(row, 6, QTableWidgetItem(br_txt))
            
            self.audio_table.setItem(row, 7, QTableWidgetItem(Path(song["file_path"]).suffix.upper().replace(".", "")))
            
            cutoff_val = song.get("spectral_cutoff")
            cutoff_txt = f"{int(cutoff_val):,} Hz" if cutoff_val else "-"
            self.audio_table.setItem(row, 8, QTableWidgetItem(cutoff_txt))
            
            legit_val = song.get("legit")
            if song.get("spectral_cutoff"):
                reason_str = song.get("legit_reason", "")
                if legit_val == 1:
                    status_item = QTableWidgetItem("Genuine Lossless")
                    status_item.setForeground(QBrush(QColor(COLOR_SUCCESS)))
                elif "upscale" in reason_str.lower() or "upscaled" in reason_str.lower():
                    status_item = QTableWidgetItem("Possible Upscale")
                    status_item.setForeground(QBrush(QColor(COLOR_WARNING)))
                else:
                    status_item = QTableWidgetItem("Fake Lossless")
                    status_item.setForeground(QBrush(QColor(COLOR_ERROR)))
            else:
                status_item = QTableWidgetItem("Unverified")
                status_item.setForeground(QBrush(QColor(TEXT_MUTED)))
            self.audio_table.setItem(row, 9, status_item)

    def filter_audio_table(self, filter_text: str):
        filter_text = filter_text.lower()
        for row in range(self.audio_table.rowCount()):
            status_item = self.audio_table.item(row, 9)
            if not status_item:
                continue
            if filter_text == "all tracks":
                self.audio_table.setRowHidden(row, False)
            elif filter_text in status_item.text().lower():
                self.audio_table.setRowHidden(row, False)
            else:
                self.audio_table.setRowHidden(row, True)

    def on_table_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            self.update_embed_btn_label()

    def update_embed_btn_label(self):
        count = 0
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                song = self.table_songs[row]
                if song["lyric_id"]:
                    count += 1
                        
        if count > 0:
            self.embed_selected_btn.setText(f"🔴 EMBED {count} TRACKS")
            self.embed_selected_btn.setEnabled(True)
        else:
            self.embed_selected_btn.setText("🔴 EMBED SELECTED LYRICS")
            self.embed_selected_btn.setEnabled(False)

    def table_row_clicked(self, item: QTableWidgetItem):
        row = item.row()
        if row >= len(self.table_songs):
            return
        
        song = self.table_songs[row]
        self.selected_song = song
        self.check_tags_btn.setEnabled(True)
        self.manual_match_btn.setEnabled(True)
        self.plot_btn.setEnabled(True)
        self.plot_img_lbl.setVisible(False)
        self.plot_btn.setText("📈 PLOT SPECTRUM GRAPH")
        
        ext = Path(song["file_path"]).suffix.upper().replace(".", "")
        sr_val = song.get("sample_rate")
        sr_txt = f"{sr_val:,} Hz" if sr_val else "Unknown"
        bits_val = song.get("bits_per_sample")
        bits_txt = f"{bits_val}-bit" if bits_val else "Unknown"
        ch_val = song.get("channels")
        ch_txt = "Mono" if ch_val == 1 else "Stereo" if ch_val == 2 else f"{ch_val} Channels" if ch_val else "Unknown"
        br_val = song.get("bitrate")
        br_txt = f"{int(br_val)} kbps" if br_val else "Unknown"
        size_mb = (song.get("file_size") or 0) / (1024 * 1024)
        
        meta_txt = (
            f"<b style='font-size: 11pt;'>{song['title'] or Path(song['file_path']).name}</b><br>"
            f"<span style='color: {TEXT_SECONDARY};'>{song['artist'] or 'Unknown Artist'} — {song['album'] or 'Unknown Album'}</span><br><br>"
            f"<span style='background: #1c1f28; color: {ACCENT_RED}; border: 1px solid #3d141b; border-radius: 4px; padding: 2px 6px; font-weight: bold;'>{ext}</span> "
            f"<span style='background: #1c1f28; color: #ffffff; border-radius: 4px; padding: 2px 6px;'>{bits_txt} / {sr_txt}</span> "
            f"<span style='background: #1c1f28; color: #ffffff; border-radius: 4px; padding: 2px 6px;'>{size_mb:.1f} MB</span>"
        )
        self.meta_info_lbl.setText(meta_txt)
        
        cutoff_hz = song.get("spectral_cutoff")
        legit_val = song.get("legit")
        if cutoff_hz:
            reason_str = song.get("legit_reason", "")
            if legit_val == 1:
                verdict = "Genuine Lossless"
                verdict_color = COLOR_SUCCESS
            elif "upscale" in reason_str.lower() or "upscaled" in reason_str.lower():
                verdict = "Possible Upscale"
                verdict_color = COLOR_WARNING
            else:
                verdict = "Fake Lossless"
                verdict_color = COLOR_ERROR
            spec_txt = (
                f"<b>Verdict:</b> <span style='color:{verdict_color}; font-weight: bold;'>{verdict}</span><br>"
                f"<b>Spectral Cutoff:</b> {cutoff_hz:.1f} Hz<br>"
                f"<b>Details:</b> {song.get('legit_reason', 'No additional details.')}"
            )
        else:
            spec_txt = "Enable verification to analyze track cutoff frequencies."
        self.spec_verdict_lbl.setText(spec_txt)

        lyrics = song.get("lyrics_text", "")
        if lyrics:
            self.lyric_preview.setHtml(self.render_lyrics_html(lyrics))
        else:
            self.lyric_preview.setPlainText("[No lyrics matched for this song.]")
        self.lyric_preview.setEnabled(True)

    def check_file_tags(self):
        if not hasattr(self, 'selected_song') or not self.selected_song:
            return

        filepath = self.selected_song["file_path"]
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "File Not Found", f"The audio file could not be found at:\n{filepath}")
            return

        embedder = Embedder()
        embedded_text = embedder.read_embedded_lyrics(filepath)

        if embedded_text.strip():
            num_lines = len(embedded_text.splitlines())
            QMessageBox.information(
                self, "Tags Verified",
                f"Embedded lyrics successfully verified inside file!\n\n"
                f"File: {Path(filepath).name}\n"
                f"Format: {Path(filepath).suffix.upper()}\n"
                f"Length: {len(embedded_text)} characters ({num_lines} timing lines)."
            )
        else:
            QMessageBox.information(
                self, "No Tags Detected",
                f"No embedded lyrics were detected inside this file.\n\n"
                f"File: {Path(filepath).name}"
            )

    def manual_match_lyric(self):
        if not hasattr(self, 'selected_song') or not self.selected_song:
            return

        song_id = self.selected_song["id"]
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Lyric Files (*.lrc *.ttml)")
        dialog.setWindowTitle("Choose Lyric File Manually")
        
        if dialog.exec():
            selected_file = dialog.selectedFiles()[0]
            try:
                lyr_data = LyricParser.parse_file(selected_file)
                lyric_id = self.db.add_lyric(
                    lyr_data["file_path"],
                    lyr_data["type"],
                    lyr_data["last_timestamp"],
                    lyr_data["plain_text_preview"]
                )
                self.db.save_match(song_id, lyric_id, 100.0)
                self.load_table_data()
                
                for row in range(self.table.rowCount()):
                    if self.table_songs[row]["id"] == song_id:
                        self.table.setCurrentCell(row, 1)
                        self.table_row_clicked(self.table.item(row, 1))
                        break
                        
                self.toast.show_message("Lyric file matched manually.", "🔴")
            except Exception as e:
                QMessageBox.critical(self, "Match Error", f"Failed to match lyric file: {e}")

    def plot_selected_spectrum(self):
        if not hasattr(self, 'selected_song') or not self.selected_song:
            return
        
        filepath = self.selected_song["file_path"]
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "File Not Found", f"The audio file could not be found at:\n{filepath}")
            return
            
        self.plot_btn.setText("Generating Spectrum...")
        self.plot_btn.setEnabled(False)
        QApplication.processEvents()
        
        import matplotlib.pyplot as plt
        import scipy.io.wavfile as wavfile
        import subprocess
        import numpy as np
        
        temp_wav = tempfile.mktemp(suffix=".wav")
        temp_img = os.path.join(tempfile.gettempdir(), f"spectrum_{int(QThread.currentThreadId())}.png")
        
        try:
            cmd = [
                'ffmpeg', '-y',
                '-ss', '30',
                '-t', '10',
                '-i', filepath,
                '-ac', '1',
                temp_wav
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            sample_rate, data = wavfile.read(temp_wav)
            n = len(data)
            
            if n == 0:
                cmd[3] = '0'
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                sample_rate, data = wavfile.read(temp_wav)
                n = len(data)
                
            if n > 0:
                fft_result = np.fft.rfft(data)
                frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
                magnitudes = np.abs(fft_result)
                magnitudes = np.clip(magnitudes, 1e-10, None)
                magnitudes_db = 20 * np.log10(magnitudes)
                magnitudes_db -= np.max(magnitudes_db)
                
                band_size = 250
                max_freq = sample_rate / 2.0
                bands = np.arange(1000, max_freq, band_size)
                
                band_means = []
                for b in bands:
                    mask = (frequencies >= b) & (frequencies < b + band_size)
                    if np.any(mask):
                        band_means.append(np.mean(magnitudes_db[mask]))
                    else:
                        band_means.append(-100.0)
                band_means = np.array(band_means)
                
                diffs = band_means[1:] - band_means[:-1]
                
                brickwall_idx = -1
                max_drop = 0.0
                for i in range(len(diffs)):
                    freq = bands[i]
                    if freq >= 10000:
                        if diffs[i] < -12.0:
                            if abs(diffs[i]) > max_drop:
                                max_drop = abs(diffs[i])
                                brickwall_idx = i
                
                threshold_db = -55.0
                if brickwall_idx != -1:
                    cutoff = float(bands[brickwall_idx] + band_size)
                    method_title = f"Brickwall Drop: {cutoff/1000:.1f} kHz (-{max_drop:.1f}dB)"
                else:
                    active_freqs = frequencies[magnitudes_db > threshold_db]
                    cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
                    method_title = f"Threshold Limit: {cutoff/1000:.1f} kHz"
                
                plt.figure(figsize=(5.5, 2.8))
                plt.plot(frequencies / 1000.0, magnitudes_db, color='#ff002b', alpha=0.85)
                plt.axhline(y=threshold_db, color='#8a8d9b', linestyle='--', alpha=0.7)
                plt.axvline(x=cutoff / 1000.0, color='#34d399', linestyle='-.', linewidth=1.5)
                
                plt.title(method_title, fontsize=9, color='white', fontweight='bold')
                plt.xlabel("Frequency (kHz)", fontsize=8, color='white')
                plt.ylabel("Magnitude (dB)", fontsize=8, color='white')
                plt.xlim(0, sample_rate / 2000.0)
                plt.ylim(-100, 5)
                
                fig = plt.gcf()
                fig.patch.set_facecolor('#0b0c0e')
                ax = plt.gca()
                ax.set_facecolor('#16181d')
                ax.spines['bottom'].set_color('#292d38')
                ax.spines['top'].set_color('#292d38')
                ax.spines['left'].set_color('#292d38')
                ax.spines['right'].set_color('#292d38')
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(True, color='#222630', linestyle=':', alpha=0.6)
                
                plt.tight_layout()
                plt.savefig(temp_img, facecolor='#0b0c0e', dpi=100)
                plt.close()
                
                pixmap = QPixmap(temp_img)
                self.plot_img_lbl.setPixmap(pixmap)
                self.plot_img_lbl.setVisible(True)
                
                try:
                    os.unlink(temp_img)
                except Exception:
                    pass
            else:
                QMessageBox.warning(self, "Analysis Failed", "Could not extract valid audio samples for spectrum plotting.")
                
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", f"Failed to generate spectrum plot: {e}")
        finally:
            if os.path.exists(temp_wav):
                try:
                    os.unlink(temp_wav)
                except Exception:
                    pass
            self.plot_btn.setText("📈 PLOT SPECTRUM GRAPH")
            self.plot_btn.setEnabled(True)

    def embed_selected(self):
        selected_ids = []
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                song = self.table_songs[row]
                if self.mode == "audio" or song["lyric_id"]:
                    selected_ids.append(song["id"])

        if not selected_ids:
            QMessageBox.information(self, "No Selection", "Please check at least one song with matched lyrics.")
            return

        if hasattr(self, 'logs_txt'):
            self.logs_txt.clear()
        self.full_log_lines = []
        if hasattr(self, 'logs_search'):
            self.logs_search.clear()
            
        initial_msg = f"Ready. Initializing embedding process...\n"
        if hasattr(self, 'logs_txt'):
            self.logs_txt.append(initial_msg)
        self.full_log_lines.append(initial_msg.strip())
        
        self.center_progress.setValue(0)
        self.center_status_lbl.setText("EMBEDDING LYRICS...")

        keep_backup = self.backup_chk.isChecked()
        backup_dir = os.path.join(os.path.dirname(self.db.db_path), "backups")

        only_write_integrity = (self.mode == "audio")
        self.embed_worker = EmbedWorker(self.db, selected_ids, keep_backup, backup_dir, only_write_integrity)
        self.embed_worker.progress.connect(self.on_embed_progress)
        self.embed_worker.log.connect(self.on_embed_log)
        self.embed_worker.finished.connect(self.on_embed_finished)
        self.embed_worker.start()

    @Slot(int, str)
    def on_embed_progress(self, val: int, text: str):
        self.set_progress_smooth(self.center_progress, val)
        self.center_status_lbl.setText(f"PROCESSING: {text.upper()}")

    @Slot(str)
    def on_embed_log(self, log_msg: str):
        self.full_log_lines.append(log_msg)
        filter_text = ""
        if hasattr(self, 'logs_search'):
            filter_text = self.logs_search.text().strip()
        if filter_text:
            self.filter_logs(filter_text)
        elif hasattr(self, 'logs_txt'):
            self.logs_txt.append(log_msg)

    @Slot(dict)
    def on_embed_finished(self, results: dict):
        if "error" in results:
            QMessageBox.critical(self, "Embedding Error", f"Embedding failed: {results['error']}")
            return

        embedded = results.get("embedded", 0)
        failed = results.get("failed", 0)
        
        all_songs = self.db.get_all_songs()
        fake_count = sum(1 for s in all_songs if s.get("legit") == 0 and s.get("spectral_cutoff"))
        
        self.center_progress.setValue(100)
        self.center_status_lbl.setText("PROCESSING COMPLETE.")
        
        self.toast.show_message(f"Embedding finished! {embedded} embedded, {failed} failed.", "🔴", 4000)
        self.load_table_data()
        
        self.lbl_stat_total.setText(str(len(all_songs)))
        self.lbl_stat_matched.setText(str(sum(1 for s in all_songs if s.get("lyric_id"))))
        self.lbl_stat_unmatched.setText(str(len(all_songs) - sum(1 for s in all_songs if s.get("lyric_id"))))
        self.lbl_stat_suspicious.setText(str(fake_count))

    def export_report(self, report_format: str):
        stats = self.db.get_stats()
        songs = self.db.get_all_songs()
        
        export_dir = os.path.join(os.path.dirname(self.db.db_path), "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f"report_{int(QThread.currentThreadId())}"
        filepath = os.path.join(export_dir, f"{filename}.{report_format}")

        details = []
        for song in songs:
            error_msg = ""
            if song["status"] == "Failed":
                error_msg = "Embedding tag error (mismatch or corrupt format)."
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

        if report_format == "html":
            ReportGenerator.generate_html_report(stats, details, filepath)
        elif report_format == "txt":
            ReportGenerator.generate_txt_report(stats, details, filepath)
        elif report_format == "json":
            ReportGenerator.generate_json_report(stats, details, filepath)

        self.toast.show_message(f"Report exported to {os.path.basename(filepath)}", "📊")
        
        try:
            os.startfile(os.path.dirname(filepath))
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    
    app_font = QFont("Inter", 10)
    app_font.setStyleHint(QFont.SansSerif)
    app.setFont(app_font)

    window = LyricForgeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
