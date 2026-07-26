"""
Unit tests for JarvisLogger structured daily observability logger.
"""

import os
import unittest
from datetime import datetime
from services.logger import logger

class TestJarvisLogger(unittest.TestCase):
    def test_logger_file_creation(self):
        """Verify logger creates daily log file and writes structured entries."""
        logger.info("TEST", "Test log message line")
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        expected_file = os.path.join(os.getcwd(), "logs", f"{today_str}.log")
        
        self.assertTrue(os.path.exists(expected_file))
        
        with open(expected_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Test log message line", content)

if __name__ == "__main__":
    unittest.main()
