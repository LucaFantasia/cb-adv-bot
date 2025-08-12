"""
logger.py — Project-wide logging configuration

Sets up:
- Console logging with color-coded timestamps
- Rotating log file output
- Optional audible beeps per log level (debug/info/error)

Access via: from utils.logger import logger
"""

import logging
import os
import sys
import threading
from datetime import datetime

# Cross-platform sound function (uses winsound on Windows)
try:
    import winsound

    def beep(frequency: int, duration: int) -> None:
        threading.Thread(target=lambda: winsound.Beep(frequency, duration), daemon=True).start()

except ImportError:

    def beep(frequency: int, duration: int) -> None:
        print("\a", end="", file=sys.stderr)


class SoundHandler(logging.Handler):
    """
    A logging handler that triggers audible tones based on log level.
    """

    def __init__(self, level_map: dict[int, tuple[int, int]]) -> None:
        super().__init__()
        self.level_map = level_map

    def emit(self, record: logging.LogRecord) -> None:
        config = self.level_map.get(record.levelno)
        if config:
            frequency, duration = config
            beep(frequency, duration)


# Global logger used across the bot
logger = logging.getLogger("trading_bot")
logger.setLevel(logging.DEBUG)

# --- Console Handler ---
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)-5s %(name)s: %(message)s", "%H:%M:%S")
)
logger.addHandler(console_handler)

# --- File Handler ---
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
log_file_path = os.path.join(log_dir, f"TRADING_BOT_OUTPUT_{timestamp}.log")

file_handler = logging.FileHandler(log_file_path, mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s  %(name)s: %(message)s"))
logger.addHandler(file_handler)

# --- Sound Handler ---
sound_handler = SoundHandler(
    {logging.DEBUG: (1000, 150), logging.INFO: (1500, 200), logging.ERROR: (300, 300)}
)
sound_handler.setLevel(logging.DEBUG)
logger.addHandler(sound_handler)
