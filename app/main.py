import os
import sys
import argparse
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from app.core.constants import APP_NAME, APP_VERSION
from app.core.application import setup_platform_integration, get_database_path
from app.core.config import config_manager
from app.core.logging import logger
from app.database.database import DatabaseManager
from app.services.library_service import LibraryService
from app.services.lyric_service import LyricService
from app.services.analysis_service import AnalysisService
from app.audio.spectrum import SpectrumImageProvider

def run_qml_gui():
    setup_platform_integration()

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("LyricForge")
    app.setApplicationName(APP_NAME)

    # Initialize Database & Core Services
    db_path = get_database_path()
    db_manager = DatabaseManager(db_path)

    library_service = LibraryService(db_manager)
    lyric_service = LyricService(db_manager, library_service)
    analysis_service = AnalysisService()

    # Instantiate QML Engine
    engine = QQmlApplicationEngine()

    # Register Spectrum Image Provider Bridge (image://spectrum/file_path)
    engine.addImageProvider("spectrum", SpectrumImageProvider())

    # Expose Services to QML Context
    context = engine.rootContext()
    context.setContextProperty("libraryService", library_service)
    context.setContextProperty("lyricService", lyric_service)
    context.setContextProperty("analysisService", analysis_service)
    context.setContextProperty("configManager", config_manager)

    # Load root Main.qml file
    qml_file = Path(__file__).parent.parent / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file.resolve())))

    if not engine.rootObjects():
        logger.error("Failed to load root QML Main.qml object. Exiting.")
        sys.exit(1)

    logger.info(f"{APP_NAME} v{APP_VERSION} QML engine running successfully.")
    sys.exit(app.exec())


def main():
    parser = argparse.ArgumentParser(description="LyricForge Pro - Smart synchronized lyrics matching, embedding, and spectral analysis desktop application.")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch QML GUI mode.")
    parser.add_argument("-m", "--music-dir", type=str, help="Music library folder path.")
    parser.add_argument("-l", "--lyrics-dir", type=str, help="Lyrics folder path.")
    args = parser.parse_args()

    run_qml_gui()

if __name__ == "__main__":
    main()
