# YouTube Audio Player CLI (Textual + MPV)

This project is a terminal-based YouTube audio player (TUI) built using Textual, yt-dlp, and MPV.
It allows the user to paste a YouTube link and play only the audio directly in the terminal.

## Features

TUI interface built with Textual

Supports YouTube links

Audio extraction using yt-dlp

Audio playback using MPV

## Requirements
- Python 3.10+
- MPV installed on the system
- pip to install dependencies

## Installation

Clone the repository:

git clone https://github.com/Diogojlq/youtube-player-cli.git
cd youtube-player-cli

Create a virtual environment and install dependencies:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Verify that MPV is available:

mpv --version

## How It Works

- Textual controls the terminal user interface
- yt-dlp extracts the direct audio stream URL
- MPV is launched through a subprocess
- The TUI is temporarily suspended while MPV runs
