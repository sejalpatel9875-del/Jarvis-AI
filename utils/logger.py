"""
Purpose:
Structured Production Logger for Jarvis AI OS.

Responsibilities:
- Standardized logging (INFO, WARNING, ERROR) to console and daily log files

Dependencies:
- None
"""

import os
import logging
import datetime

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

today_str = datetime.date.today().strftime("%Y-%m-%d")
log_filepath = os.path.join(LOGS_DIR, f"jarvis_{today_str}.log")

logger = logging.getLogger("JarvisLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Console Handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s', datefmt='%H:%M:%S')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    f_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
