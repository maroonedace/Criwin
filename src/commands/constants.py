from pathlib import Path

SUPPORTED_DOMAINS = [
    "youtube.com",
    "youtu.be",
    "instagram.com",
    "reddit.com",
    "bluesky.app",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "vm.tiktok.com",
]

# Download Directory
DOWNLOAD_DIR = str(Path.home() / "Downloads")