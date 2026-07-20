# LyricForge - Smart Lyrics Embedder & Audio Quality Inspector

Welcome to **LyricForge**! This is a simple, smart, and safe tool designed to help you organize your music library. 

If you have music files (like `.mp3` or `.flac`) and synchronized lyrics files (like `.lrc` or `.ttml`), LyricForge automatically matches them up and writes the lyrics directly into the music files. This allows music players on your phone or computer to display synchronized lyrics on screen while the song plays.

Additionally, LyricForge can analyze your music files' sound waves to verify if they are truly high-quality (lossless) or if they are low-quality files disguised as high-quality (fake upscales).

---

## 🌟 What does this app do? (In Simple Terms)

1. **Scans Folders:** You choose a folder with music and a folder with lyrics. LyricForge reads them all.
2. **Smart Word-Matching:** It compares the song title, artist name, and album name with the lyric files. Even if the files are named slightly differently (e.g. `01. Shape of You.mp3` vs `shape_of_you.lrc`), it matches them correctly.
3. **Quality Check (Spectrum Inspector):** It inspects the audio frequencies. If a song is labeled as high-quality (like FLAC) but actually sounds like a low-quality MP3, the app flags it with a warning.
4. **Safe Embedding:** It backs up your music files first. Then, it writes the lyrics inside the song file and double-checks if it succeeded. If something goes wrong, it restores your original file safely.
5. **Interactive Interface (GUI):** A clean dark-mode desktop window where you can drag-and-drop folders, preview matched lyrics side-by-side, view real-time progress, and check completion statistics.

---

## 🚀 How to Set Up (For Beginners)

To run this app on your computer, you need **Python** installed. 

### Step 1: Install Python
If you don't have Python, download it from [python.org](https://www.python.org/downloads/) (version 3.11 or newer). During installation, make sure to check the box that says **"Add Python to PATH"** (this is very important!).

### Step 2: Download the Project
Download this project as a ZIP folder and extract it somewhere on your computer (for example, on your Desktop).

### Step 3: Install Required Packages
Open your terminal or command prompt (search for `cmd` on Windows, or `Terminal` on Mac), navigate to this project folder, and run:
```bash
pip install -r requirements.txt
```
This automatically downloads the auxiliary libraries needed to run the app.

---

## 💻 How to Use the App

### 1. The Easy Way: Graphical Interface (GUI)
To open the user-friendly desktop window, run this command in your terminal:
```bash
python app.py
```
* **Step 1:** Select or **drag-and-drop** your Music and Lyrics folders directly into the app window.
* **Step 2:** Click **Scan & Match Library**. The app will scan the folders and match songs with lyrics.
* **Step 3:** Review the matches on the screen. Click on a song to preview its lyrics side-by-side.
* **Step 4:** Check the boxes next to the songs you want to modify, and click **Embed Selected Lyrics**.
* **Step 5:** View your results on the dashboard summary page.

### 2. The Advanced Way: Command Line (CLI)
If you prefer running the tool headlessly (without opening a window), you can pass parameters directly:
```bash
python app.py -m "/path/to/music" -l "/path/to/lyrics" --embed
```
* `-m`: Path to your music folder.
* `-l`: Path to your lyrics folder.
* `--embed`: Automatically embed matched lyrics immediately.
* `--verify`: Run quality checks on the audio frequencies.
* `-r html`: Generate a visual HTML summary report in the `exports` folder.

---

## 📁 Project Structure (What is inside?)

Here is a simple map of how this project is organized:

* [app.py](file:///d:/Lyrics-Ember/app.py) — The main door to the application. It launches either the graphical window or runs the command-line mode.
* **`core/`** (The brain of the app):
  * [scanner.py](file:///d:/Lyrics-Ember/core/scanner.py) — Finds and lists all the music and lyrics files in your folders.
  * [lyrics.py](file:///d:/Lyrics-Ember/core/lyrics.py) — Reads and parses timed lyric files.
  * [converter.py](file:///d:/Lyrics-Ember/core/converter.py) — Converts complex lyric formats (like `.ttml`) into standard format (`.lrc`).
  * [metadata.py](file:///d:/Lyrics-Ember/core/metadata.py) — Reads song tags (like title, artist name, and duration).
  * [matcher.py](file:///d:/Lyrics-Ember/core/matcher.py) — The matching engine that pairs the correct lyric file with each song.
  * [verifier.py](file:///d:/Lyrics-Ember/core/verifier.py) — The audio quality inspector that checks if audio streams are genuine or fake upscales.
  * [backup.py](file:///d:/Lyrics-Ember/core/backup.py) — Handles making safety backups and restoring files if needed.
  * [embedder.py](file:///d:/Lyrics-Ember/core/embedder.py) — Writes the lyrics directly into the music file tags.
  * [db_manager.py](file:///d:/Lyrics-Ember/core/db_manager.py) — Stores matching information in a local database so subsequent runs are instant.
  * [report.py](file:///d:/Lyrics-Ember/core/report.py) — Exports results into HTML, TXT, or JSON reports.
* **`ui/`** (The visual window):
  * [main_window.py](file:///d:/Lyrics-Ember/ui/main_window.py) — Draws the dark-mode layout, manages drag-and-drop actions, runs progress bar animations, and displays the stats dashboard cards.
* **`tests/`** (Safety checks):
  * [test_core.py](file:///d:/Lyrics-Ember/tests/test_core.py) — Automated tests to verify that every module functions correctly.
"# Lyrics_Embedder" 
