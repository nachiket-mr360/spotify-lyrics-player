--- AI Lyrics Player ---

    This is a simple desktop lyrics player built using Python.

    It plays any .mp3 file and shows the lyrics in sync while the song is playing.
    The lyrics are generated automatically using Faster-Whisper (AI speech recognition).

I built this to learn about:

    Audio processing

    Speech-to-text

    Tkinter UI design

    Working with JSON

    Handling real-time synchronization

What It Does

    Select any MP3 file

    Automatically transcribes the song (first time only)

    Saves transcript as .json file

    Shows lyrics in sync with the music

    Pause / Resume button

    Load new song option

    Proper Exit button

    Spotify-style minimal UI

    Romanizes Hindi / Urdu lyrics into English letters

    If the transcript already exists, it loads instantly without reprocessing.


Tech Used

    Python 3.11

    Faster-Whisper

    Pygame

    Tkinter

    Indic Transliteration

    How To Run

    Install Python 3.11

Requirements

    Python 3.11 (recommended, because some libraries may not work properly on newer versions)

    FFmpeg installed and added to system PATH

    Internet connection (only required the first time for model download)

Install required packages:

    pip install faster-whisper pygame indic-transliteration


Run:

python main.py


Then select your song.