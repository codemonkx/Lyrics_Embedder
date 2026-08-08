import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QPropertyAnimation, QRectF
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QTextEdit, QProgressBar,
    QMessageBox, QCheckBox, QSlider, QGridLayout, QFrame, QStackedWidget,
    QButtonGroup, QLineEdit, QScrollArea, QMenu
)
from PySide6.QtGui import QFont, QColor, QBrush, QIcon, QPainter

from core.db_manager import DBManager
from core.scanner import FileScanner
from core.metadata import MetadataReader
from core.lyrics import LyricParser
from core.matcher import MatchingEngine
from core.embedder import Embedder
from core.backup import BackupManager
from core.report import ReportGenerator
from core.verifier import AudioVerifier

# Define clean macOS dark styling sheet (QSS)
DARK_STYLE = """
QWidget#central {
    background-color: #1E1F22;
    border: 1px solid #393B40;
    border-radius: 8px;
}
QFrame#leftSidebar, QScrollArea#rightSidebarScroll {
    background-color: #2B2D30;
    border: 1px solid #393B40;
    border-radius: 3px;
}
QScrollArea#rightSidebarScroll > QWidget {
    background-color: transparent;
}
QFrame#progressFrame, QFrame#tableFrame, QWidget#emptyStateOverlay {
    background-color: #2B2D30;
    border: 1px solid #393B40;
    border-radius: 3px;
}
QWidget {
    color: #DFE1E5;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}
QLabel {
    color: #DFE1E5;
}
QLabel#subtleLabel {
    color: #868A91;
    font-size: 12px;
}
QLabel.sectionLabel {
    color: #868A91;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QLineEdit {
    background-color: #1E1F22;
    border: 1px solid #393B40;
    border-radius: 3px;
    padding: 5px 8px;
    color: #DFE1E5;
}
QLineEdit:focus {
    border: 1px solid #3574F0;
}
QPushButton {
    background-color: #2B2D30;
    border: 1px solid #393B40;
    border-radius: 3px;
    padding: 5px 12px;
    color: #DFE1E5;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #35383F;
}
QPushButton:pressed {
    background-color: #1E1F22;
}
QPushButton#primaryButton {
    background-color: #3574F0;
    border: 1px solid #2B58B0;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background-color: #4A85F2;
}
QPushButton#primaryButton:pressed {
    background-color: #1E4FB0;
}
QPushButton#primaryButton:disabled {
    background-color: #2B2D30;
    border-color: #393B40;
    color: #868A91;
}
QPushButton#tabButtonActive {
    background-color: #3574F0;
    border: 1px solid #2B58B0;
    border-radius: 3px;
    padding: 5px 16px;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#tabButtonInactive {
    background-color: #2B2D30;
    border: 1px solid #393B40;
    border-radius: 3px;
    padding: 5px 16px;
    color: #868A91;
    font-weight: 500;
}
QPushButton#tabButtonInactive:hover {
    color: #DFE1E5;
    background-color: #35383F;
}
QTableWidget {
    background-color: transparent;
    alternate-background-color: #2B2D30;
    gridline-color: transparent;
    border: none;
}
QTableWidget::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #393B40;
    border-radius: 2px;
    background-color: #1E1F22;
}
QTableWidget::indicator:checked {
    background-color: #3574F0;
    border-color: #3574F0;
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}
QTableWidget::item {
    border-bottom: 1px solid #393B40;
    padding: 6px 8px;
    color: #DFE1E5;
}
QTableWidget::item:selected {
    background-color: #2E436E;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #2B2D30;
    color: #868A91;
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid #393B40;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}
QProgressBar {
    border: none;
    border-radius: 2px;
    background-color: #1E1F22;
    text-align: center;
    color: transparent;
    height: 4px;
}
QProgressBar::chunk {
    background-color: #3574F0;
    border-radius: 2px;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #393B40;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #4E5157;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 6px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #393B40;
    min-width: 20px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #4E5157;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}
QSplitter::handle {
    background-color: #393B40;
}
QTextEdit {
    background-color: #1E1F22;
    border: 1px solid #393B40;
    border-radius: 4px;
    color: #DFE1E5;
    padding: 8px;
}
QCheckBox {
    spacing: 8px;
    color: #DFE1E5;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #393B40;
    border-radius: 2px;
    background-color: #1E1F22;
}
QCheckBox::indicator:checked {
    background-color: #3574F0;
    border-color: #3574F0;
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #1E1F22;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #DFE1E5;
    border: 1px solid #393B40;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::handle:horizontal:hover {
    background: #ffffff;
}
"""

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

class DashboardRow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            DashboardRow {
                background-color: #2B2D30;
                border: 1px solid #393B40;
                border-radius: 3px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        self.setFixedHeight(64)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(24)
        
        # Metric 1: Total Tracks (Blue)
        self.lbl_total_val = QLabel("0")
        self.lbl_total_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #3574F0;")
        lbl_total_tit = QLabel("Total Tracks")
        lbl_total_tit.setStyleSheet("font-size: 11px; color: #868A91; text-transform: uppercase; font-weight: 500;")
        
        total_lay = QVBoxLayout()
        total_lay.setSpacing(2)
        total_lay.addWidget(self.lbl_total_val)
        total_lay.addWidget(lbl_total_tit)
        
        # Metric 2: Matched (Green)
        self.lbl_matched_val = QLabel("0")
        self.lbl_matched_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #4F8557;")
        lbl_matched_tit = QLabel("Matched")
        lbl_matched_tit.setStyleSheet("font-size: 11px; color: #868A91; text-transform: uppercase; font-weight: 500;")
        
        matched_lay = QVBoxLayout()
        matched_lay.setSpacing(2)
        matched_lay.addWidget(self.lbl_matched_val)
        matched_lay.addWidget(lbl_matched_tit)
        
        # Metric 3: Unmatched (Muted/Grey)
        self.lbl_unmatched_val = QLabel("0")
        self.lbl_unmatched_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #868A91;")
        lbl_unmatched_tit = QLabel("Unmatched")
        lbl_unmatched_tit.setStyleSheet("font-size: 11px; color: #868A91; text-transform: uppercase; font-weight: 500;")
        
        unmatched_lay = QVBoxLayout()
        unmatched_lay.setSpacing(2)
        unmatched_lay.addWidget(self.lbl_unmatched_val)
        unmatched_lay.addWidget(lbl_unmatched_tit)
        
        # Metric 4: Suspicious (Warning Orange/Red depending on count)
        self.lbl_suspicious_val = QLabel("0")
        self.lbl_suspicious_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #A67C3B;")
        lbl_suspicious_tit = QLabel("Suspicious Audio")
        lbl_suspicious_tit.setStyleSheet("font-size: 11px; color: #868A91; text-transform: uppercase; font-weight: 500;")
        
        suspicious_lay = QVBoxLayout()
        suspicious_lay.setSpacing(2)
        suspicious_lay.addWidget(self.lbl_suspicious_val)
        suspicious_lay.addWidget(lbl_suspicious_tit)
        
        layout.addLayout(total_lay)
        layout.addLayout(matched_lay)
        layout.addLayout(unmatched_lay)
        layout.addLayout(suspicious_lay)
        layout.addStretch()
        
    def update_stats(self, total: int, matched: int, unmatched: int, suspicious: int):
        self.lbl_total_val.setText(str(total))
        self.lbl_matched_val.setText(str(matched))
        self.lbl_unmatched_val.setText(str(unmatched))
        self.lbl_suspicious_val.setText(str(suspicious))
        
        if suspicious > 10:
            self.lbl_suspicious_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #B85C5C;")
        elif suspicious > 0:
            self.lbl_suspicious_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #A67C3B;")
        else:
            self.lbl_suspicious_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #868A91;")

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_win = parent
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #1E1F22;
                border-bottom: 1px solid #393B40;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        self.setFixedHeight(52)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # Logo & App Name
        logo_lbl = QLabel("LyricForge")
        logo_lbl.setStyleSheet("font-weight: 700; font-size: 16px; color: #3B82F6; background: transparent; border: none;")
        layout.addWidget(logo_lbl)
        
        ver_lbl = QLabel("v1.2.0")
        ver_lbl.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent; border: none; font-weight: 500;")
        layout.addWidget(ver_lbl)
        
        layout.addStretch()
        
        # Mode Switcher buttons in toolbar center
        self.btn_tab_lyrics = QPushButton("Embed Lyrics")
        self.btn_tab_lyrics.setCheckable(True)
        self.btn_tab_lyrics.setChecked(True)
        self.btn_tab_lyrics.setObjectName("tabButtonActive")
        
        self.btn_tab_audio = QPushButton("Audio Inspector")
        self.btn_tab_audio.setCheckable(True)
        self.btn_tab_audio.setObjectName("tabButtonInactive")
        
        self.btn_tab_lyrics.clicked.connect(self.parent_win.switch_to_lyrics_mode)
        self.btn_tab_audio.clicked.connect(self.parent_win.switch_to_audio_mode)
        
        # Exclusivity group
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.btn_tab_lyrics)
        self.mode_group.addButton(self.btn_tab_audio)
        self.mode_group.setExclusive(True)
        
        layout.addWidget(self.btn_tab_lyrics)
        layout.addWidget(self.btn_tab_audio)
        
        layout.addStretch()
        
        # Integrated Search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter tracks...")
        self.search_bar.setFixedWidth(160)
        self.search_bar.textChanged.connect(self.parent_win.on_search_filter_changed)
        layout.addWidget(self.search_bar)
        
        # Reports & Settings triggers
        self.btn_reports = QPushButton("Reports")
        self.btn_reports.setObjectName("secondaryButton")
        self.btn_reports.setStyleSheet("padding: 4px 10px; font-size: 12px;")
        self.btn_reports.clicked.connect(self.parent_win.show_reports_popup)
        layout.addWidget(self.btn_reports)
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setObjectName("secondaryButton")
        self.btn_settings.setStyleSheet("padding: 4px 10px; font-size: 12px;")
        self.btn_settings.clicked.connect(self.parent_win.show_settings_popup)
        layout.addWidget(self.btn_settings)
        
        # Control Buttons
        btn_min = QPushButton("—")
        btn_min.setFixedSize(28, 20)
        btn_min.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #94A3B8; font-size: 12px; font-weight: bold; padding: 0px; }
            QPushButton:hover { color: #F3F4F6; background-color: #1A2030; border-radius: 3px; }
        """)
        btn_min.clicked.connect(self.parent_win.showMinimized)
        layout.addWidget(btn_min)
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 20)
        btn_close.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #94A3B8; font-size: 11px; font-weight: bold; padding: 0px; }
            QPushButton:hover { color: #ffffff; background-color: #EF4444; border-radius: 3px; }
        """)
        btn_close.clicked.connect(self.parent_win.close)
        layout.addWidget(btn_close)
        
        self.drag_position = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_win.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent_win.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

class DonutChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = {"success": 0, "failed": 0, "unmatched": 0}
        self.setMinimumSize(140, 140)
        self.setMaximumSize(140, 140)

    def set_stats(self, success: int, failed: int, unmatched: int):
        self.stats = {"success": success, "failed": failed, "unmatched": unmatched}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = sum(self.stats.values())
        rect = QRectF(8, 8, self.width() - 16, self.height() - 16)
        
        if total == 0:
            painter.setBrush(QColor("#3a3a3c"))
            painter.setPen(Qt.NoPen)
            painter.drawPie(rect, 0, 360 * 16)
            
            inner_rect = QRectF(32, 32, self.width() - 64, self.height() - 64)
            painter.setBrush(QColor("#1e1e1e"))
            painter.drawEllipse(inner_rect)
            return
            
        success_deg = (self.stats["success"] / total) * 360.0
        failed_deg = (self.stats["failed"] / total) * 360.0
        unmatched_deg = (self.stats["unmatched"] / total) * 360.0
        
        start_angle = 90.0
        
        painter.setPen(Qt.NoPen)
        
        if success_deg > 0:
            painter.setBrush(QColor("#34c759"))
            painter.drawPie(rect, int(start_angle * 16), int(-success_deg * 16))
            start_angle -= success_deg
            
        if failed_deg > 0:
            painter.setBrush(QColor("#ff3b30"))
            painter.drawPie(rect, int(start_angle * 16), int(-failed_deg * 16))
            start_angle -= failed_deg
            
        if unmatched_deg > 0:
            painter.setBrush(QColor("#8e8e93"))
            painter.drawPie(rect, int(start_angle * 16), int(-unmatched_deg * 16))
            
        inner_rect = QRectF(32, 32, self.width() - 64, self.height() - 64)
        painter.setBrush(QColor("#1e1e1e"))
        painter.drawEllipse(inner_rect)
        
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("sans-serif", 9, QFont.Bold))
        painter.drawText(inner_rect, Qt.AlignCenter, f"{total}\nFiles")



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
                    # Update local properties for matches query fallback
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
                    # Write only the legitimacy/integrity tags
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
                    # Standard embedding (lyrics + integrity)
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
    def __init__(self, db_path: str = "lyricforge.db"):
        super().__init__()
        self.db = DBManager(db_path)
        self.mode = "lyrics"
        self.setWindowTitle("LyricForge")
        
        # Set frameless window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Set app icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.resize(1250, 750)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        central.setObjectName("central")
        central.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Custom Title Bar (Mode Switcher is embedded in the center)
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # 2. Main Dashboard Layout (3-Column Layout: Left, Center, Right)
        self.dashboard = QSplitter(Qt.Horizontal)
        self.dashboard.setHandleWidth(16)
        self.dashboard.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
        """)

        # =========================================================================
        # --- LEFT PANEL (Configuration & Inputs) ---
        # =========================================================================
        left_widget = QFrame()
        left_widget.setObjectName("leftSidebar")
        left_widget.setFrameShape(QFrame.StyledPanel)
        left_widget.setFrameShadow(QFrame.Plain)
        left_widget.setAttribute(Qt.WA_StyledBackground, True)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(24) # Section spacing: 24px
        
        # 1. LIBRARY SECTION
        lib_lbl = QLabel("LIBRARY")
        lib_lbl.setProperty("class", "sectionLabel")
        lib_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        music_lbl = QLabel("Music Folder:")
        music_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        self.music_dir_txt = DragDropLineEdit()
        self.music_dir_txt.setText(self.db.get_setting("music_dir", ""))
        self.music_dir_txt.setPlaceholderText("Drag & drop music folder or browse...")
        self.music_dir_btn = QPushButton("Browse...")
        self.music_dir_btn.clicked.connect(lambda: self.browse_folder("music"))
        
        music_lay = QHBoxLayout()
        music_lay.setSpacing(8)
        music_lay.addWidget(self.music_dir_txt, 1)
        music_lay.addWidget(self.music_dir_btn)
        
        self.lyrics_dir_lbl = QLabel("Lyrics Folder:")
        self.lyrics_dir_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        self.lyrics_dir_txt = DragDropLineEdit()
        self.lyrics_dir_txt.setText(self.db.get_setting("lyrics_dir", ""))
        self.lyrics_dir_txt.setPlaceholderText("Drag & drop lyrics folder or browse...")
        self.lyrics_dir_btn = QPushButton("Browse...")
        self.lyrics_dir_btn.clicked.connect(lambda: self.browse_folder("lyrics"))
        
        lyrics_lay = QHBoxLayout()
        lyrics_lay.setSpacing(8)
        lyrics_lay.addWidget(self.lyrics_dir_txt, 1)
        lyrics_lay.addWidget(self.lyrics_dir_btn)
        
        lib_layout = QVBoxLayout()
        lib_layout.setSpacing(8)
        lib_layout.addWidget(lib_lbl)
        lib_layout.addWidget(music_lbl)
        lib_layout.addLayout(music_lay)
        lib_layout.addWidget(self.lyrics_dir_lbl)
        lib_layout.addLayout(lyrics_lay)
        left_layout.addLayout(lib_layout)
        
        # 2. MATCHING SECTION
        self.preset_widget = QWidget()
        self.preset_widget.setStyleSheet("background: transparent; border: none;")
        preset_lay = QVBoxLayout(self.preset_widget)
        preset_lay.setContentsMargins(0, 0, 0, 0)
        preset_lay.setSpacing(8)
        
        matching_lbl = QLabel("MATCHING")
        matching_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        preset_title_lbl = QLabel("Preset Profile:")
        preset_title_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        
        preset_btn_lay = QHBoxLayout()
        preset_btn_lay.setSpacing(4)
        self.btn_preset_fast = QPushButton("Fast")
        self.btn_preset_fast.setCheckable(True)
        self.btn_preset_balanced = QPushButton("Balanced")
        self.btn_preset_balanced.setCheckable(True)
        self.btn_preset_balanced.setChecked(True)
        self.btn_preset_strict = QPushButton("Strict")
        self.btn_preset_strict.setCheckable(True)
        
        self.preset_group = QButtonGroup(self)
        self.preset_group.addButton(self.btn_preset_fast)
        self.preset_group.addButton(self.btn_preset_balanced)
        self.preset_group.addButton(self.btn_preset_strict)
        self.preset_group.setExclusive(True)
        
        self.btn_preset_fast.clicked.connect(lambda: self.set_preset("fast"))
        self.btn_preset_balanced.clicked.connect(lambda: self.set_preset("balanced"))
        self.btn_preset_strict.clicked.connect(lambda: self.set_preset("strict"))
        
        preset_btn_lay.addWidget(self.btn_preset_fast)
        preset_btn_lay.addWidget(self.btn_preset_balanced)
        preset_btn_lay.addWidget(self.btn_preset_strict)
        
        # Threshold slider
        self.threshold_widget = QWidget()
        self.threshold_widget.setStyleSheet("background: transparent; border: none;")
        thresh_lay = QVBoxLayout(self.threshold_widget)
        thresh_lay.setContentsMargins(0, 0, 0, 0)
        thresh_lay.setSpacing(6)
        
        thresh_lbl_lay = QHBoxLayout()
        thresh_lbl_title = QLabel("Match Threshold:")
        thresh_lbl_title.setStyleSheet("font-size: 12px; color: #94A3B8;")
        saved_threshold = float(self.db.get_setting("threshold", "60.0"))
        self.threshold_lbl = QLabel(f"{int(saved_threshold)}%")
        self.threshold_lbl.setStyleSheet("color: #3B82F6; font-weight: bold;")
        thresh_lbl_lay.addWidget(thresh_lbl_title)
        thresh_lbl_lay.addStretch()
        thresh_lbl_lay.addWidget(self.threshold_lbl)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(30, 100)
        self.threshold_slider.setValue(int(saved_threshold))
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        
        thresh_lay.addLayout(thresh_lbl_lay)
        thresh_lay.addWidget(self.threshold_slider)
        
        preset_lay.addWidget(matching_lbl)
        preset_lay.addWidget(preset_title_lbl)
        preset_lay.addLayout(preset_btn_lay)
        preset_lay.addWidget(self.threshold_widget)
        left_layout.addWidget(self.preset_widget)
        
        # 3. ADVANCED SECTION (Collapsible)
        advanced_lbl_container = QWidget()
        advanced_lbl_container.setStyleSheet("background: transparent; border: none;")
        adv_lbl_lay = QHBoxLayout(advanced_lbl_container)
        adv_lbl_lay.setContentsMargins(0, 0, 0, 0)
        
        self.btn_toggle_advanced = QPushButton("ADVANCED ▼")
        self.btn_toggle_advanced.setStyleSheet("""
            QPushButton {
                font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;
                border: none; background: transparent; text-align: left; padding: 0px;
            }
            QPushButton:hover { color: #3B82F6; }
        """)
        self.btn_toggle_advanced.clicked.connect(self.toggle_advanced_panel)
        adv_lbl_lay.addWidget(self.btn_toggle_advanced)
        left_layout.addWidget(advanced_lbl_container)
        
        # Expandable widget
        self.advanced_widget = QWidget()
        self.advanced_widget.setStyleSheet("background: transparent; border: none;")
        advanced_lay = QVBoxLayout(self.advanced_widget)
        advanced_lay.setContentsMargins(0, 0, 0, 0)
        advanced_lay.setSpacing(10)
        
        self.backup_chk = QCheckBox("Backup original audio files")
        self.backup_chk.setChecked(self.db.get_setting("keep_backup", "True") == "True")
        advanced_lay.addWidget(self.backup_chk)
        
        self.verify_chk = QCheckBox("Inspect spectral verifier cutoff")
        self.verify_chk.setChecked(self.db.get_setting("verify_audio", "True") == "True")
        advanced_lay.addWidget(self.verify_chk)
        
        # Sliders for matching weights
        w_lbl = QLabel("Weight Distribution Matrix:")
        w_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #94A3B8;")
        advanced_lay.addWidget(w_lbl)
        
        self.w_title_slider = QSlider(Qt.Horizontal)
        self.w_title_slider.setRange(0, 100)
        self.w_title_slider.setValue(40)
        self.w_title_lbl = QLabel("40%")
        self.w_title_slider.valueChanged.connect(lambda v: self.w_title_lbl.setText(f"{v}%"))
        title_w_lay = QHBoxLayout()
        title_w_lay.addWidget(QLabel("Title:"))
        title_w_lay.addWidget(self.w_title_slider, 1)
        title_w_lay.addWidget(self.w_title_lbl)
        advanced_lay.addLayout(title_w_lay)
        
        self.w_artist_slider = QSlider(Qt.Horizontal)
        self.w_artist_slider.setRange(0, 100)
        self.w_artist_slider.setValue(30)
        self.w_artist_lbl = QLabel("30%")
        self.w_artist_slider.valueChanged.connect(lambda v: self.w_artist_lbl.setText(f"{v}%"))
        artist_w_lay = QHBoxLayout()
        artist_w_lay.addWidget(QLabel("Artist:"))
        artist_w_lay.addWidget(self.w_artist_slider, 1)
        artist_w_lay.addWidget(self.w_artist_lbl)
        advanced_lay.addLayout(artist_w_lay)
        
        self.w_album_slider = QSlider(Qt.Horizontal)
        self.w_album_slider.setRange(0, 100)
        self.w_album_slider.setValue(15)
        self.w_album_lbl = QLabel("15%")
        self.w_album_slider.valueChanged.connect(lambda v: self.w_album_lbl.setText(f"{v}%"))
        album_w_lay = QHBoxLayout()
        album_w_lay.addWidget(QLabel("Album:"))
        album_w_lay.addWidget(self.w_album_slider, 1)
        album_w_lay.addWidget(self.w_album_lbl)
        advanced_lay.addLayout(album_w_lay)
        
        self.w_filename_slider = QSlider(Qt.Horizontal)
        self.w_filename_slider.setRange(0, 100)
        self.w_filename_slider.setValue(10)
        self.w_filename_lbl = QLabel("10%")
        self.w_filename_slider.valueChanged.connect(lambda v: self.w_filename_lbl.setText(f"{v}%"))
        filename_w_lay = QHBoxLayout()
        filename_w_lay.addWidget(QLabel("File:"))
        filename_w_lay.addWidget(self.w_filename_slider, 1)
        filename_w_lay.addWidget(self.w_filename_lbl)
        advanced_lay.addLayout(filename_w_lay)
        
        left_layout.addWidget(self.advanced_widget)
        left_layout.addStretch()
        
        # 4. ACTIONS SECTION
        actions_lbl = QLabel("ACTIONS")
        actions_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.scan_btn = QPushButton("Scan Library")
        self.scan_btn.setObjectName("primaryButton")
        self.scan_btn.setMinimumHeight(32)
        self.scan_btn.clicked.connect(self.start_scan)
        
        actions_sub_lay = QHBoxLayout()
        actions_sub_lay.setSpacing(8)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("secondaryButton")
        self.btn_reset.clicked.connect(self.reset_library)
        self.btn_export = QPushButton("Export")
        self.btn_export.setObjectName("secondaryButton")
        self.btn_export.clicked.connect(self.export_library_reports)
        
        actions_sub_lay.addWidget(self.btn_reset, 1)
        actions_sub_lay.addWidget(self.btn_export, 1)
        
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        actions_layout.addWidget(actions_lbl)
        actions_layout.addWidget(self.scan_btn)
        actions_layout.addLayout(actions_sub_lay)
        
        left_layout.addLayout(actions_layout)
        self.dashboard.addWidget(left_widget)

        # =========================================================================
        # --- CENTER PANEL (Progress, Stats Dashboard, Data Table, and Logs) ---
        # =========================================================================
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        
        # 1. Progress section (current operation, percentage, remaining time)
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progressFrame")
        self.progress_frame.setFrameShape(QFrame.StyledPanel)
        self.progress_frame.setFrameShadow(QFrame.Plain)
        self.progress_frame.setAttribute(Qt.WA_StyledBackground, True)
        prog_lay = QGridLayout(self.progress_frame)
        prog_lay.setContentsMargins(16, 12, 16, 12)
        prog_lay.setSpacing(8)
        
        self.center_status_lbl = QLabel("Standby. Configure folders and click scan to begin library matching.")
        self.center_status_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #868A91; border: none; background: transparent;")
        
        self.center_progress = QProgressBar()
        self.center_progress.setRange(0, 100)
        self.center_progress.setValue(0)
        
        self.lbl_progress_percent = QLabel("0%")
        self.lbl_progress_percent.setStyleSheet("font-size: 13px; font-weight: bold; color: #3574F0; border: none; background: transparent;")
        
        self.lbl_remaining_time = QLabel("Remaining: --")
        self.lbl_remaining_time.setStyleSheet("font-size: 12px; color: #868A91; border: none; background: transparent;")
        
        prog_lay.addWidget(self.center_status_lbl, 0, 0)
        prog_lay.addWidget(self.lbl_remaining_time, 0, 1, Qt.AlignRight)
        prog_lay.addWidget(self.center_progress, 1, 0)
        prog_lay.addWidget(self.lbl_progress_percent, 1, 1, Qt.AlignRight)
        
        center_layout.addWidget(self.progress_frame)
        
        # 2. Statistics row
        self.stats_row = DashboardRow()
        center_layout.addWidget(self.stats_row)
        
        # StatCardProxy setup
        class StatCardProxy:
            def __init__(self, callback):
                self.callback = callback
            def set_value(self, value):
                self.callback(value)
            def setVisible(self, visible):
                pass
                
        self.card_total = StatCardProxy(lambda v: self.stats_row.lbl_total_val.setText(v))
        self.card_matched = StatCardProxy(lambda v: self.stats_row.lbl_matched_val.setText(v))
        self.card_unmatched = StatCardProxy(lambda v: self.stats_row.lbl_unmatched_val.setText(v))
        self.card_suspicious = StatCardProxy(self.on_suspicious_stat_changed)
        
        # 3. Table area frame
        self.table_frame = QFrame()
        self.table_frame.setObjectName("tableFrame")
        self.table_frame.setFrameShape(QFrame.StyledPanel)
        self.table_frame.setFrameShadow(QFrame.Plain)
        self.table_frame.setAttribute(Qt.WA_StyledBackground, True)
        table_frame_lay = QVBoxLayout(self.table_frame)
        table_frame_lay.setContentsMargins(8, 8, 8, 8)
        table_frame_lay.setSpacing(0)
        
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setMinimumHeight(28)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection) # Enable multi-select!
        self.table.setSortingEnabled(True) # Sortable!
        self.table.itemClicked.connect(self.table_row_clicked)
        self.table.itemChanged.connect(self.on_table_item_changed)
        
        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        table_frame_lay.addWidget(self.table)
        center_layout.addWidget(self.table_frame, 1) # table stretches to fill central space
        
        # 4. Empty State Placeholder Overlay
        self.empty_state_overlay = QFrame()
        self.empty_state_overlay.setObjectName("emptyStateOverlay")
        self.empty_state_overlay.setFrameShape(QFrame.StyledPanel)
        self.empty_state_overlay.setFrameShadow(QFrame.Plain)
        self.empty_state_overlay.setAttribute(Qt.WA_StyledBackground, True)
        empty_lay = QVBoxLayout(self.empty_state_overlay)
        empty_lay.setContentsMargins(24, 24, 24, 24)
        empty_lay.setAlignment(Qt.AlignCenter)
        
        self.empty_msg_lbl = QLabel("No library loaded. Select a music folder to begin matching track lyrics and inspecting audio integrity.")
        self.empty_msg_lbl.setStyleSheet("font-size: 13px; color: #868A91; font-weight: 500; background: transparent; border: none;")
        self.empty_msg_lbl.setAlignment(Qt.AlignCenter)
        self.empty_msg_lbl.setWordWrap(True)
        
        empty_lay.addWidget(self.empty_msg_lbl)
        center_layout.addWidget(self.empty_state_overlay, 1)
        
        # 5. Collapsible filterable logs drawer
        self.logs_container = QWidget()
        logs_lay = QVBoxLayout(self.logs_container)
        logs_lay.setContentsMargins(0, 0, 0, 0)
        logs_lay.setSpacing(6)
        
        log_header = QHBoxLayout()
        log_title_lbl = QLabel("PROCESS LOGS")
        log_title_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.logs_search = QLineEdit()
        self.logs_search.setPlaceholderText("Filter logs...")
        self.logs_search.setFixedWidth(200)
        self.logs_search.textChanged.connect(self.filter_logs)
        
        log_header.addWidget(log_title_lbl)
        log_header.addStretch()
        log_header.addWidget(self.logs_search)
        logs_lay.addLayout(log_header)
        
        self.logs_txt = QTextEdit()
        self.logs_txt.setReadOnly(True)
        self.logs_txt.setFont(QFont("Courier New", 9))
        self.logs_txt.setFixedHeight(95)
        
        logs_lay.addWidget(self.logs_txt)
        center_layout.addWidget(self.logs_container)
        
        # 6. Primary Action Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        self.embed_selected_btn = QPushButton("Embed Selected Lyrics")
        self.embed_selected_btn.setObjectName("primaryButton")
        self.embed_selected_btn.setMinimumHeight(32)
        self.embed_selected_btn.setEnabled(False)
        self.embed_selected_btn.clicked.connect(self.embed_selected)
        footer_layout.addWidget(self.embed_selected_btn)
        
        center_layout.addLayout(footer_layout)
        self.dashboard.addWidget(center_widget)

        # =========================================================================
        # --- RIGHT PANEL (Metadata details, Audio Analysis, Lyrics Edit) ---
        # =========================================================================
        right_scroll = QScrollArea()
        right_scroll.setObjectName("rightSidebarScroll")
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.StyledPanel)
        right_scroll.setFrameShadow(QFrame.Plain)
        right_scroll.setAttribute(Qt.WA_StyledBackground, True)
        
        right_widget = QFrame()
        right_widget.setObjectName("rightWidget")
        right_widget.setStyleSheet("background-color: transparent; border: none;")
        right_widget.setMinimumWidth(320)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(24) # Section spacing: 24px
        
        # 1. TRACK DETAILS Section
        details_lbl = QLabel("TRACK DETAILS")
        details_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.meta_info_lbl = QLabel("No track selected.")
        self.meta_info_lbl.setStyleSheet("color: #F3F4F6; line-height: 18px; font-size: 13px;")
        self.meta_info_lbl.setWordWrap(True)
        
        details_lay = QVBoxLayout()
        details_lay.setSpacing(8)
        details_lay.addWidget(details_lbl)
        details_lay.addWidget(self.meta_info_lbl)
        
        div1 = QFrame()
        div1.setFrameShape(QFrame.HLine)
        div1.setFrameShadow(QFrame.Plain)
        div1.setStyleSheet("color: #1f232d; max-height: 1px;")
        
        right_layout.addLayout(details_lay)
        right_layout.addWidget(div1)
        
        # 2. AUDIO ANALYSIS Section
        spec_lbl = QLabel("AUDIO ANALYSIS")
        spec_lbl.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.spec_verdict_lbl = QLabel("Select a track to verify cutoff frequencies.")
        self.spec_verdict_lbl.setStyleSheet("color: #F3F4F6; line-height: 18px; font-size: 13px;")
        self.spec_verdict_lbl.setWordWrap(True)
        
        self.plot_btn = QPushButton("Plot Spectrum Graph")
        self.plot_btn.setObjectName("secondaryButton")
        self.plot_btn.clicked.connect(self.plot_selected_spectrum)
        self.plot_btn.setEnabled(False)
        
        self.plot_img_lbl = QLabel()
        self.plot_img_lbl.setAlignment(Qt.AlignCenter)
        self.plot_img_lbl.setVisible(False)
        
        analysis_lay = QVBoxLayout()
        analysis_lay.setSpacing(8)
        analysis_lay.addWidget(spec_lbl)
        analysis_lay.addWidget(self.spec_verdict_lbl)
        analysis_lay.addWidget(self.plot_btn)
        analysis_lay.addWidget(self.plot_img_lbl)
        
        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setFrameShadow(QFrame.Plain)
        div2.setStyleSheet("color: #1f232d; max-height: 1px;")
        
        right_layout.addLayout(analysis_lay)
        right_layout.addWidget(div2)
        
        # 3. LYRICS PREVIEW Section
        self.right_lyrics_frame = QWidget()
        self.right_lyrics_frame.setStyleSheet("background: transparent; border: none;")
        lyrics_preview_lay = QVBoxLayout(self.right_lyrics_frame)
        lyrics_preview_lay.setContentsMargins(0, 0, 0, 0)
        lyrics_preview_lay.setSpacing(8)
        
        lyrics_lbl_title = QLabel("LYRICS PREVIEW")
        lyrics_lbl_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.lyric_preview = QTextEdit()
        self.lyric_preview.setPlaceholderText("Select a song with matched lyrics to preview/edit...")
        self.lyric_preview.setFixedHeight(180)
        self.lyric_preview.textChanged.connect(self.on_lyrics_text_edited)
        
        lyrics_preview_lay.addWidget(lyrics_lbl_title)
        lyrics_preview_lay.addWidget(self.lyric_preview)
        
        div3 = QFrame()
        div3.setFrameShape(QFrame.HLine)
        div3.setFrameShadow(QFrame.Plain)
        div3.setStyleSheet("color: #1f232d; max-height: 1px;")
        
        right_layout.addWidget(self.right_lyrics_frame)
        right_layout.addWidget(div3)
        
        # 4. ACTIONS Section
        actions_title = QLabel("ACTIONS")
        actions_title.setStyleSheet("font-weight: 600; font-size: 11px; color: #94A3B8; letter-spacing: 0.8px;")
        
        self.check_tags_btn = QPushButton("Verify Tags")
        self.check_tags_btn.setObjectName("secondaryButton")
        self.check_tags_btn.setEnabled(False)
        self.check_tags_btn.clicked.connect(self.check_file_tags)
        
        self.manual_match_btn = QPushButton("Select Lyrics File")
        self.manual_match_btn.setObjectName("secondaryButton")
        self.manual_match_btn.setEnabled(False)
        self.manual_match_btn.clicked.connect(self.manual_match_lyric)
        
        self.btn_inspect_export_rep = QPushButton("Export Report")
        self.btn_inspect_export_rep.setObjectName("secondaryButton")
        self.btn_inspect_export_rep.clicked.connect(lambda: self.export_report("html"))
        
        actions_panel_lay = QVBoxLayout()
        actions_panel_lay.setSpacing(8)
        actions_panel_lay.addWidget(actions_title)
        actions_panel_lay.addWidget(self.check_tags_btn)
        actions_panel_lay.addWidget(self.manual_match_btn)
        actions_panel_lay.addWidget(self.btn_inspect_export_rep)
        
        right_layout.addLayout(actions_panel_lay)
        right_layout.addStretch()
        
        right_scroll.setWidget(right_widget)
        self.dashboard.addWidget(right_scroll)
        
        # Add outer padded layout wrapper for QSplitter dashboard
        body_widget = QWidget()
        body_widget.setStyleSheet("background-color: transparent; border: none;")
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.addWidget(self.dashboard)
        
        main_layout.addWidget(body_widget, 1)
        
        # Enforce exact splitter widths initially
        self.dashboard.setSizes([250, 687, 313])
        self.setStyleSheet(DARK_STYLE)
        self.load_table_data()

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
        self.export_report("html")
        
    def show_settings_popup(self):
        self.toggle_advanced_panel()

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
            self.card_total.set_value("0")
            self.card_matched.set_value("0")
            self.card_unmatched.set_value("0")
            self.card_suspicious.set_value("0")

    def export_library_reports(self):
        self.export_report("html")

    def on_suspicious_stat_changed(self, value: str):
        try:
            val_int = int(value)
            self.stats_row.update_stats(
                int(self.stats_row.lbl_total_val.text() or "0"),
                int(self.stats_row.lbl_matched_val.text() or "0"),
                int(self.stats_row.lbl_unmatched_val.text() or "0"),
                val_int
            )
        except Exception:
            self.stats_row.lbl_suspicious_val.setText(value)

    def render_lyrics_html(self, text: str) -> str:
        if not text:
            return "<span style='color:#94A3B8;'>No lyrics loaded.</span>"
        import re
        lines = []
        for line in text.splitlines():
            match = re.match(r'^(\[[0-9:.]+\])(.*)', line)
            if match:
                time_tag = match.group(1)
                content = match.group(2)
                lines.append(f"<span style='color:#3B82F6; font-family:Courier New; font-weight:bold;'>{time_tag}</span> <span style='color:#F3F4F6;'>{content}</span>")
            else:
                lines.append(f"<span style='color:#F3F4F6;'>{line}</span>")
        return "<br>".join(lines)

    def set_progress_smooth(self, bar, value):
        self.anim = QPropertyAnimation(bar, b"value", self)
        self.anim.setDuration(180)
        self.anim.setStartValue(bar.value())
        self.anim.setEndValue(value)
        self.anim.start()

    def show_table_context_menu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A2030;
                border: 1px solid #1f232d;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #F3F4F6;
            }
            QMenu::item:selected {
                background-color: #3B82F6;
                color: #ffffff;
            }
        """)
        
        act_verify = menu.addAction("Verify Lossless")
        act_verify.setEnabled(self.mode == "audio" and hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_tag = menu.addAction("Verify File Tag")
        act_tag.setEnabled(hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_match = menu.addAction("Manual Lyric Match...")
        act_match.setEnabled(self.mode == "lyrics" and hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_plot = menu.addAction("Plot Spectrum Graph")
        act_plot.setEnabled(hasattr(self, 'selected_song') and self.selected_song is not None)
        
        act_export = menu.addAction("Export Library Report")
        
        action = menu.exec(self.table.mapToGlobal(position))
        if action == act_verify:
            self.check_file_tags()
        elif action == act_tag:
            self.check_file_tags()
        elif action == act_match:
            self.manual_match_lyric()
        elif action == act_plot:
            self.plot_selected_spectrum()
        elif action == act_export:
            self.export_report("html")

    def switch_to_lyrics_mode(self):
        self.mode = "lyrics"
        self.title_bar.btn_tab_lyrics.setObjectName("tabButtonActive")
        self.title_bar.btn_tab_audio.setObjectName("tabButtonInactive")
        self.title_bar.btn_tab_lyrics.setStyleSheet(DARK_STYLE)
        self.title_bar.btn_tab_audio.setStyleSheet(DARK_STYLE)
        
        # Show lyrics items
        self.lyrics_dir_lbl.setVisible(True)
        self.lyrics_dir_txt.setVisible(True)
        self.lyrics_dir_btn.setVisible(True)
        self.preset_widget.setVisible(True)
        self.threshold_widget.setVisible(True)
        self.right_lyrics_frame.setVisible(True)
        
        self.scan_btn.setText("Scan & Match Library")
        self.load_table_data()

    def switch_to_audio_mode(self):
        self.mode = "audio"
        self.title_bar.btn_tab_lyrics.setObjectName("tabButtonInactive")
        self.title_bar.btn_tab_audio.setObjectName("tabButtonActive")
        self.title_bar.btn_tab_lyrics.setStyleSheet(DARK_STYLE)
        self.title_bar.btn_tab_audio.setStyleSheet(DARK_STYLE)
        
        # Hide lyrics items
        self.lyrics_dir_lbl.setVisible(False)
        self.lyrics_dir_txt.setVisible(False)
        self.lyrics_dir_btn.setVisible(False)
        self.preset_widget.setVisible(False)
        self.threshold_widget.setVisible(False)
        self.right_lyrics_frame.setVisible(False)
        
        self.scan_btn.setText("Inspect Audio Integrity")
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
        visible = self.advanced_widget.isVisible()
        self.advanced_widget.setVisible(not visible)
        if visible:
            self.btn_toggle_advanced.setText("Advanced Configuration ▶")
        else:
            self.btn_toggle_advanced.setText("Advanced Configuration ▼")

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
        self.logs_txt.clear()
        self.full_log_lines = []
        self.logs_search.clear()

        if self.mode == "audio":
            self.db.set_setting("keep_backup", "True" if self.backup_chk.isChecked() else "False")
            self.center_status_lbl.setText("Inspecting Audio Integrity...")
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

            self.center_status_lbl.setText("Scanning library...")
            
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

    def set_progress_smooth(self, progress_bar, val):
        if not hasattr(progress_bar, "_anim"):
            progress_bar._anim = QPropertyAnimation(progress_bar, b"value")
            progress_bar._anim.setDuration(200)
        progress_bar._anim.stop()
        progress_bar._anim.setStartValue(progress_bar.value())
        progress_bar._anim.setEndValue(val)
        progress_bar._anim.start()

    @Slot(int, str)
    def on_scan_progress(self, val: int, status_text: str):
        self.set_progress_smooth(self.center_progress, val)
        self.center_status_lbl.setText(status_text)

    @Slot(dict)
    def on_scan_finished(self, stats: dict):
        if "error" in stats:
            QMessageBox.critical(self, "Scan Error", f"Scan failed: {stats['error']}")
            return

        self.load_table_data()
        
        # Update metrics cards
        songs = self.db.get_all_songs()
        total = len(songs)
        matched = sum(1 for s in songs if s.get("lyric_id"))
        unmatched = total - matched
        suspicious = sum(1 for s in songs if s.get("legit") == 0 and s.get("spectral_cutoff"))
        
        self.card_total.set_value(str(total))
        self.card_matched.set_value(str(matched))
        self.card_unmatched.set_value(str(unmatched))
        self.card_suspicious.set_value(str(suspicious))

    def load_table_data(self):
        self.selected_song = None
        self.check_tags_btn.setEnabled(False)
        self.manual_match_btn.setEnabled(False)
        self.plot_btn.setEnabled(False)
        self.plot_img_lbl.setVisible(False)
        
        self.meta_info_lbl.setText("No track selected.")
        self.spec_verdict_lbl.setText("Select a song to review audio integrity verification.")
        if self.mode == "lyrics":
            self.lyric_preview.setPlainText("Select a song with matched lyrics to preview/edit.")
        else:
            self.lyric_preview.setPlainText("[Lyrics disabled in standalone Audio Inspector mode]")

        self.table.blockSignals(True)
        
        # Set headers depending on current mode
        if self.mode == "audio":
            self.table.setColumnCount(11)
            self.table.setHorizontalHeaderLabels([
                "", "File Name", "Sample Rate", "Bits", "Ch", "Duration", 
                "Size", "Bitrate", "Format", "Max Freq", "Integrity Status"
            ])
            self.table.setColumnWidth(0, 30)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 95)
            self.table.setColumnWidth(3, 50)
            self.table.setColumnWidth(4, 75)
            self.table.setColumnWidth(5, 75)
            self.table.setColumnWidth(6, 75)
            self.table.setColumnWidth(7, 85)
            self.table.setColumnWidth(8, 70)
            self.table.setColumnWidth(9, 95)
            self.table.setColumnWidth(10, 120)
            
            for col in range(11):
                self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Interactive)
        else:
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels(["", "Song Title", "Artist", "Album", "Duration", "Match Score", "Status"])
            self.table.setColumnWidth(0, 30)
            self.table.setColumnWidth(4, 75)
            self.table.setColumnWidth(5, 90)
            self.table.setColumnWidth(6, 110)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        songs = self.db.get_all_songs()
        self.table_songs = songs
        
        # Toggle Empty State Placeholder
        has_songs = len(songs) > 0
        self.empty_state_overlay.setVisible(not has_songs)
        self.table.setVisible(has_songs)
        self.table_frame.setVisible(has_songs)
        
        self.table.setRowCount(len(songs))

        for row, song in enumerate(songs):
            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if self.mode == "audio":
                chk_item.setCheckState(Qt.Checked)
            elif song["status"] in ["Matched", "Embedded"]:
                chk_item.setCheckState(Qt.Checked)
            else:
                chk_item.setCheckState(Qt.Unchecked)
            self.table.setItem(row, 0, chk_item)

            if self.mode == "audio":
                filename = Path(song["file_path"]).name
                self.table.setItem(row, 1, QTableWidgetItem(filename))
                
                sr_val = song.get("sample_rate")
                sr_txt = f"{sr_val:,} Hz" if sr_val else "-"
                self.table.setItem(row, 2, QTableWidgetItem(sr_txt))
                
                bits_val = song.get("bits_per_sample")
                bits_txt = str(bits_val) if bits_val else "-"
                self.table.setItem(row, 3, QTableWidgetItem(bits_txt))
                
                ch_val = song.get("channels")
                ch_txt = "Mono" if ch_val == 1 else "Stereo" if ch_val == 2 else f"{ch_val} Ch" if ch_val else "-"
                self.table.setItem(row, 4, QTableWidgetItem(ch_txt))
                
                dur = song.get("duration", 0.0)
                if dur > 0:
                    minutes = int(dur) // 60
                    seconds = int(dur) % 60
                    dur_txt = f"{minutes}:{seconds:02d}"
                else:
                    dur_txt = "-"
                self.table.setItem(row, 5, QTableWidgetItem(dur_txt))
                
                size_val = song.get("file_size")
                size_txt = f"{size_val / (1024 * 1024):.1f} MB" if size_val else "-"
                self.table.setItem(row, 6, QTableWidgetItem(size_txt))
                
                br_val = song.get("bitrate")
                br_txt = f"{int(br_val)} kbps" if br_val else "-"
                self.table.setItem(row, 7, QTableWidgetItem(br_txt))
                
                self.table.setItem(row, 8, QTableWidgetItem(Path(song["file_path"]).suffix.lower()))
                
                cutoff_val = song.get("spectral_cutoff")
                cutoff_txt = f"{int(cutoff_val):,} Hz" if cutoff_val else "-"
                self.table.setItem(row, 9, QTableWidgetItem(cutoff_txt))
                
                legit_val = song.get("legit")
                if song.get("spectral_cutoff"):
                    reason_str = song.get("legit_reason", "")
                    if legit_val == 1:
                        status_item = QTableWidgetItem("Genuine Hi-Res")
                        status_item.setForeground(QBrush(QColor("#4F8557")))
                    elif "upscale" in reason_str.lower() or "upscaled" in reason_str.lower():
                        status_item = QTableWidgetItem("Possible Upscale")
                        status_item.setForeground(QBrush(QColor("#A67C3B")))
                    else:
                        status_item = QTableWidgetItem("Fake Lossless")
                        status_item.setForeground(QBrush(QColor("#B85C5C")))
                else:
                    status_item = QTableWidgetItem("Unverified")
                    status_item.setForeground(QBrush(QColor("#868A91")))
                self.table.setItem(row, 10, status_item)
            else:
                title_text = song["title"] or Path(song["file_path"]).name
                title_item = QTableWidgetItem(title_text)
                if song.get("legit") == 0 and song.get("spectral_cutoff"):
                    title_item.setForeground(QBrush(QColor("#A67C3B")))
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
                score_txt = ""
                if song["lyric_id"]:
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT score FROM matches WHERE song_id = ? AND lyric_id = ?", (song["id"], song["lyric_id"]))
                        row_match = cursor.fetchone()
                        if row_match:
                            score_val = float(row_match['score'])
                            score_txt = f"{score_val:.1f}%"
                self.table.setItem(row, 5, QTableWidgetItem(score_txt))

                # Custom status badge mappings
                thresh = float(self.threshold_slider.value())
                if song["status"] in ["Embedded", "Matched"]:
                    if score_val >= 99.9:
                        status_str = "Matched"
                        status_color = "#4F8557"
                    elif score_val >= thresh:
                        status_str = "Partial Match"
                        status_color = "#A67C3B"
                    else:
                        status_str = "Unmatched"
                        status_color = "#B85C5C"
                else:
                    status_str = "Unmatched"
                    status_color = "#B85C5C"

                status_item = QTableWidgetItem(status_str)
                status_item.setForeground(QBrush(QColor(status_color)))
                self.table.setItem(row, 6, status_item)

        self.table.blockSignals(False)
        self.update_embed_btn_label()

    def on_table_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            self.update_embed_btn_label()

    def update_embed_btn_label(self):
        count = 0
        for row in range(self.table.rowCount()):
            chk_item = self.table.item(row, 0)
            if chk_item and chk_item.checkState() == Qt.Checked:
                if self.mode == "audio":
                    count += 1
                else:
                    song = self.table_songs[row]
                    if song["lyric_id"]:
                        count += 1
                        
        if self.mode == "audio":
            if count > 0:
                self.embed_selected_btn.setText(f"Write Integrity Tags ({count})")
                self.embed_selected_btn.setEnabled(True)
            else:
                self.embed_selected_btn.setText("Write Integrity Tags")
                self.embed_selected_btn.setEnabled(False)
        else:
            if count > 0:
                self.embed_selected_btn.setText(f"Embed {count} Songs")
                self.embed_selected_btn.setEnabled(True)
            else:
                self.embed_selected_btn.setText("Embed Selected Lyrics")
                self.embed_selected_btn.setEnabled(False)

    def table_row_clicked(self, item: QTableWidgetItem):
        row = item.row()
        if row >= len(self.table_songs):
            return
        
        song = self.table_songs[row]
        self.selected_song = song
        self.check_tags_btn.setEnabled(True)
        self.manual_match_btn.setEnabled(self.mode == "lyrics")
        self.plot_btn.setEnabled(True)
        self.plot_img_lbl.setVisible(False)
        self.plot_btn.setText("Plot Spectrum Graph")
        
        # Populate metadata properties
        ext = Path(song["file_path"]).suffix.upper()
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
            f"<b>File:</b> {Path(song['file_path']).name}<br>"
            f"<b>Path:</b> {song['file_path']}<br>"
            f"<b>Format:</b> {ext} ({bits_txt}, {ch_txt})<br>"
            f"<b>Sample Rate:</b> {sr_txt}<br>"
            f"<b>Bitrate:</b> {br_txt}<br>"
            f"<b>File Size:</b> {size_mb:.1f} MB<br>"
            f"<b>Modified:</b> {song.get('date_modified', 'N/A')}"
        )
        self.meta_info_lbl.setText(meta_txt)
        
        # Populate verification cutoff details
        cutoff_hz = song.get("spectral_cutoff")
        legit_val = song.get("legit")
        if cutoff_hz:
            reason_str = song.get("legit_reason", "")
            if legit_val == 1:
                verdict = "Genuine Hi-Res"
                verdict_color = "#4F8557"
            elif "upscale" in reason_str.lower() or "upscaled" in reason_str.lower():
                verdict = "Possible Upscale"
                verdict_color = "#A67C3B"
            else:
                verdict = "Fake Lossless"
                verdict_color = "#B85C5C"
            spec_txt = (
                f"<b>Verdict:</b> <span style='color:{verdict_color};'>{verdict}</span><br>"
                f"<b>Spectral Cutoff:</b> {cutoff_hz:.1f} Hz<br>"
                f"<b>Details:</b> {song.get('legit_reason', 'No additional details.')}"
            )
        else:
            spec_txt = "Enable verification to analyze track cutoff frequencies."
        self.spec_verdict_lbl.setText(spec_txt)

        # Populate lyrics preview editor
        if self.mode == "lyrics":
            lyrics = song.get("lyrics_text", "")
            if lyrics:
                self.lyric_preview.setHtml(self.render_lyrics_html(lyrics))
            else:
                self.lyric_preview.setPlainText("[No lyrics matched for this song.]")
            self.lyric_preview.setEnabled(True)
        else:
            self.lyric_preview.setPlainText("[Lyrics disabled in standalone Audio Inspector mode]")
            self.lyric_preview.setEnabled(False)

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
                # Parse lyric file
                lyr_data = LyricParser.parse_file(selected_file)
                # Add to DB
                lyric_id = self.db.add_lyric(
                    lyr_data["file_path"],
                    lyr_data["type"],
                    lyr_data["last_timestamp"],
                    lyr_data["plain_text_preview"]
                )
                
                # Save manual match (100% score)
                self.db.save_match(song_id, lyric_id, 100.0)
                
                # Reload table
                self.load_table_data()
                
                # Re-select the modified song row to show updated preview
                for row in range(self.table.rowCount()):
                    if self.table_songs[row]["id"] == song_id:
                        self.table.setCurrentCell(row, 1)
                        # Trigger click callback to update preview
                        self.table_row_clicked(self.table.item(row, 1))
                        break
                        
                QMessageBox.information(
                    self, "Lyrics Matched",
                    f"Successfully matched lyric file manually!\n\n"
                    f"Song: {self.selected_song['title'] or Path(self.selected_song['file_path']).name}\n"
                    f"Lyric File: {Path(selected_file).name}"
                )
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
        
        # We import dependencies locally to avoid startup overhead
        import matplotlib.pyplot as plt
        import scipy.io.wavfile as wavfile
        import subprocess
        import numpy as np
        
        temp_wav = tempfile.mktemp(suffix=".wav")
        temp_img = os.path.join(tempfile.gettempdir(), f"spectrum_{int(QThread.currentThreadId())}.png")
        
        try:
            # Decode 10s mono starting at 30s
            cmd = [
                'ffmpeg', '-y',
                '-ss', '30',
                '-t', '10',
                '-i', filepath,
                '-ac', '1',
                temp_wav
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Read WAV
            sample_rate, data = wavfile.read(temp_wav)
            n = len(data)
            
            # If empty retry 0s
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
                
                # Group frequencies into 250 Hz bands to calculate slopes (differences)
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
                
                # Find sliding differences (slopes)
                diffs = band_means[1:] - band_means[:-1]
                
                # Brickwall detection
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
                
                # Plot
                plt.figure(figsize=(6.5, 3.2))
                plt.plot(frequencies / 1000.0, magnitudes_db, color='#0a84ff', alpha=0.8)
                plt.axhline(y=threshold_db, color='#ff3b30', linestyle='--', alpha=0.7)
                plt.axvline(x=cutoff / 1000.0, color='#34c759', linestyle='-.', linewidth=1.5)
                
                plt.title(method_title, fontsize=9, color='white', fontweight='bold')
                plt.xlabel("Frequency (kHz)", fontsize=8, color='white')
                plt.ylabel("Magnitude (dB)", fontsize=8, color='white')
                plt.xlim(0, sample_rate / 2000.0)
                plt.ylim(-100, 5)
                
                # Styling
                fig = plt.gcf()
                fig.patch.set_facecolor('#1e1e1e')
                ax = plt.gca()
                ax.set_facecolor('#252527')
                ax.spines['bottom'].set_color('#3a3a3c')
                ax.spines['top'].set_color('#3a3a3c')
                ax.spines['left'].set_color('#3a3a3c')
                ax.spines['right'].set_color('#3a3a3c')
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(True, color='#2d2d2d', linestyle=':', alpha=0.6)
                
                plt.tight_layout()
                plt.savefig(temp_img, facecolor='#1e1e1e', dpi=100)
                plt.close()
                
                # Load image
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap(temp_img)
                self.plot_img_lbl.setPixmap(pixmap)
                self.plot_img_lbl.setVisible(True)
                
                # Cleanup temp image file
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
            self.plot_btn.setText("Plot Spectrum Graph")
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
            if self.mode == "audio":
                QMessageBox.information(self, "No Selection", "Please check at least one song to write integrity tags.")
            else:
                QMessageBox.information(self, "No Selection", "Please check at least one song with matched lyrics.")
            return

        self.logs_txt.clear()
        self.full_log_lines = []
        if hasattr(self, 'logs_search'):
            self.logs_search.clear()
        if self.mode == "audio":
            initial_msg = f"Ready. Initializing audio tag correction...\n"
        else:
            initial_msg = f"Ready. Initializing embedding process...\n"
        self.logs_txt.append(initial_msg)
        self.full_log_lines.append(initial_msg.strip())
        
        self.center_progress.setValue(0)
        if self.mode == "audio":
            self.center_status_lbl.setText("Writing Integrity Tags...")
        else:
            self.center_status_lbl.setText("Embedding Lyrics...")

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
        self.center_status_lbl.setText(f"Processing: {text}")

    @Slot(str)
    def on_embed_log(self, log_msg: str):
        self.full_log_lines.append(log_msg)
        filter_text = ""
        if hasattr(self, 'logs_search'):
            filter_text = self.logs_search.text().strip()
        if filter_text:
            self.filter_logs(filter_text)
        else:
            self.logs_txt.append(log_msg)

    @Slot(dict)
    def on_embed_finished(self, results: dict):
        if "error" in results:
            QMessageBox.critical(self, "Embedding Error", f"Embedding failed: {results['error']}")
            return

        # Prepare summary info
        embedded = results.get("embedded", 0)
        failed = results.get("failed", 0)
        
        all_songs = self.db.get_all_songs()
        
        # Count legitimacy stats if verification was run
        fake_count = sum(1 for s in all_songs if s.get("legit") == 0 and s.get("spectral_cutoff"))
        legit_count = sum(1 for s in all_songs if s.get("legit") == 1 and s.get("spectral_cutoff"))
        
        verify_summary = ""
        if fake_count + legit_count > 0:
            verify_summary = f"\n• Legit Lossless: {legit_count}\n• Upscaled / Corrupt: {fake_count}"

        self.center_progress.setValue(100)
        self.center_status_lbl.setText("Processing complete.")
        
        # Display completion box
        QMessageBox.information(
            self, 
            "Processing Complete", 
            f"Successfully processed tracks:\n"
            f"• Success: {embedded}\n"
            f"• Failed: {failed}{verify_summary}"
        )
        
        # Update metrics cards and reload table
        self.load_table_data()
        
        self.card_total.set_value(str(len(all_songs)))
        self.card_matched.set_value(str(sum(1 for s in all_songs if s.get("lyric_id"))))
        self.card_unmatched.set_value(str(len(all_songs) - sum(1 for s in all_songs if s.get("lyric_id"))))
        self.card_suspicious.set_value(str(fake_count))


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

        QMessageBox.information(
            self, "Report Exported", 
            f"Successfully exported {report_format.upper()} report to:\n{filepath}"
        )
        
        try:
            os.startfile(os.path.dirname(filepath))
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    window = LyricForgeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
