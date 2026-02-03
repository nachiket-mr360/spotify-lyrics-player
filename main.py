from faster_whisper import WhisperModel
import pygame
import time
import os
import json
import tkinter as tk
from tkinter import filedialog, ttk
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from tkinter import messagebox
import re
import sys

# -----------------------------
# SCRIPT DETECTION
# -----------------------------
def is_devanagari(text):
    return re.search(r'[\u0900-\u097F]', text)

def is_urdu(text):
    return re.search(r'[\u0600-\u06FF]', text)


# -----------------------------
# SELECT SONG
# -----------------------------
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select a Song",
    filetypes=[("MP3 files", "*.mp3")]
)

if not file_path:
    sys.exit()

song_name = os.path.splitext(os.path.basename(file_path))[0]
json_file = song_name + ".json"


# -----------------------------
# LOAD OR CREATE TRANSCRIPT
# -----------------------------
if os.path.exists(json_file):
    print("Loading cached transcript...")
    with open(json_file, "r", encoding="utf-8") as f:
        segments = json.load(f)
else:
    print("Transcribing (first time only)...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

    segments_generator, _ = model.transcribe(file_path, beam_size=5)

    segments = []
    for segment in segments_generator:
        segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print("Transcript saved.")


# -----------------------------
# TKINTER WINDOW
# -----------------------------
app = tk.Tk()
app.title("Lyrics Player")
app.geometry("900x600")

SPOTIFY_BG = "#121212"
SPOTIFY_LIGHT = "#1DB954"
SPOTIFY_TEXT = "#FFFFFF"
SPOTIFY_SUBTEXT = "#B3B3B3"

app.configure(bg=SPOTIFY_BG)


# -----------------------------
# AUDIO SETUP
# -----------------------------
pygame.mixer.init()
pygame.mixer.music.load(file_path)
pygame.mixer.music.play()

song_length = pygame.mixer.Sound(file_path).get_length()

start_time = time.time()
segment_index = 0
paused = False
pause_offset = 0


# -----------------------------
# MAIN LAYOUT
# -----------------------------
main_frame = tk.Frame(app, bg=SPOTIFY_BG)
main_frame.pack(fill="both", expand=True)

# TOP SPACER
top_spacer = tk.Frame(main_frame, bg=SPOTIFY_BG)
top_spacer.pack(expand=True)

# CONTENT FRAME (actual UI)
content_frame = tk.Frame(main_frame, bg=SPOTIFY_BG)
content_frame.pack()

# BOTTOM SPACER
bottom_spacer = tk.Frame(main_frame, bg=SPOTIFY_BG)
bottom_spacer.pack(expand=True)


# --- Title ---
title_label = tk.Label(
    content_frame,
    text=song_name,
    font=("Segoe UI", 14),
    fg=SPOTIFY_SUBTEXT,
    bg=SPOTIFY_BG
)
title_label.pack(pady=(0, 8))


# --- Current lyric ---
current_label = tk.Label(
    content_frame,
    text="",
    font=("Segoe UI", 28, "bold"),
    fg=SPOTIFY_TEXT,
    bg=SPOTIFY_BG,
    wraplength=800,
    justify="center"
)
current_label.pack(pady=(0, 4))


# --- Next lyric ---
next_label = tk.Label(
    content_frame,
    text="",
    font=("Segoe UI", 18),
    fg=SPOTIFY_SUBTEXT,
    bg=SPOTIFY_BG,
    wraplength=800,
    justify="center"
)
next_label.pack(pady=(0, 10))


# -----------------------------
# CONTROLS
# -----------------------------
control_frame = tk.Frame(content_frame, bg=SPOTIFY_BG)
control_frame.pack(pady=(6,12))


def toggle_pause():
    global paused, start_time, pause_offset

    if not paused:
        pygame.mixer.music.pause()
        paused = True
        pause_offset = time.time() - start_time
        pause_button.config(text="Resume",
        fg="white",
        bg=SPOTIFY_LIGHT
        )
    else:
        pygame.mixer.music.unpause()
        paused = False
        start_time = time.time() - pause_offset
        pause_button.config(text="Pause",
        fg=SPOTIFY_LIGHT,
        bg="#1E1E1E"
        )


def load_new_song():
    pygame.mixer.music.stop()
    app.destroy()
    os.system("python main.py")


def exit_app():
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    app.destroy()
    sys.exit()


def create_button(text, command):
    return tk.Button(
        control_frame,
        text=text,
        command=command,
        bg="#1E1E1E",
        fg=SPOTIFY_LIGHT,
        activebackground="#333333",
        activeforeground="white",
        bd=0,
        padx=18,
        pady=6,
        font=("Segoe UI", 11)
    )


pause_button = create_button("Pause", toggle_pause)
pause_button.pack(side="left", padx=8)
if not pygame.mixer.music.get_busy():
    pause_button.config(text="Play")


load_button = create_button("Load Song", load_new_song)
load_button.pack(side="left", padx=8)

exit_button = create_button("Exit", exit_app)
exit_button.pack(side="left", padx=8)


# -----------------------------
# PROGRESS SECTION
# -----------------------------
# -----------------------------
# CUSTOM PROGRESS BAR (Spotify Style)
# -----------------------------
progress_canvas = tk.Canvas(
    content_frame,
    width=850,
    height=8,
    bg=SPOTIFY_BG,
    highlightthickness=0
)
progress_canvas.pack(pady=(4,6))

# Background bar
progress_bg = progress_canvas.create_rectangle(
    0, 0, 850, 8,
    fill="#2A2A2A",
    outline=""
)

# Filled portion
progress_fill = progress_canvas.create_rectangle(
    0, 0, 0, 8,
    fill=SPOTIFY_LIGHT,
    outline=""
)

def reset_player():
    global start_time, segment_index, paused
    start_time = time.time()
    segment_index = 0
    paused = False


def show_end_dialog():
    response = messagebox.askyesnocancel(
        "Song Finished",
        "Song finished.\n\nYes = Replay\nNo = Load New Song\nCancel = Exit"
    )

    if response is True:  # Replay
        pygame.mixer.music.play()
        reset_player()

    elif response is False:  # Load new
        load_new_song()

    else:  # Cancel = Exit
        exit_app()

# -----------------------------
# UPDATE LOOP
# -----------------------------
def update_lyrics():
    global segment_index, paused, start_time

    if not paused and segment_index < len(segments):
        current_time = time.time() - start_time
        segment = segments[segment_index]

        if current_time >= segment["start"]:

            text = segment["text"]

            if is_devanagari(text):
                text = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
            elif is_urdu(text):
                text = transliterate(text, sanscript.ARABIC, sanscript.ITRANS)

            current_label.config(text=text)

            if segment_index + 1 < len(segments):
                next_text = segments[segment_index + 1]["text"]

                if is_devanagari(next_text):
                    next_text = transliterate(next_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                elif is_urdu(next_text):
                    next_text = transliterate(next_text, sanscript.ARABIC, sanscript.ITRANS)

                next_label.config(text=next_text)

            segment_index += 1

    # Progress handling
    # Check if music finished
    if not pygame.mixer.music.get_busy() and not paused:
        current_time = song_length
    else:
        if not paused:
            current_time = time.time() - start_time
        else:
            current_time = pause_offset

    # Prevent overflow
    if current_time > song_length:
        current_time = song_length

    progress_width = 850
    fill_width = (current_time / song_length) * progress_width

    progress_canvas.coords(
        progress_fill,
        0, 0,
        fill_width, 8
    )
    
    mins = int(current_time // 60)
    secs = int(current_time % 60)
    total_mins = int(song_length // 60)
    total_secs = int(song_length % 60)

    time_label.config(text=f"{mins}:{secs:02d} / {total_mins}:{total_secs:02d}")
    # If song ended
    if not pygame.mixer.music.get_busy() and not paused:
         show_end_dialog()
         return


    app.after(100, update_lyrics)
    # progress.state(["disabled"])

# -----------------------------
# TIME LABEL
# -----------------------------
time_label = tk.Label(
    content_frame,
    text="0:00 / 0:00",
    fg=SPOTIFY_SUBTEXT,
    bg=SPOTIFY_BG,
    font=("Segoe UI", 10)
)
time_label.pack(pady=(0, 0))

    

update_lyrics()
app.mainloop()
