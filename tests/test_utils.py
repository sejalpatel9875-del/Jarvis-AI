"""
Unit tests for Environment Validator and Production Logger.
"""

import unittest
from utils.env_validator import validate_environment
from utils.logger import logger

class TestUtils(unittest.TestCase):
    def test_env_validation(self):
        """Verify environment validation returns structured dictionary."""
        status = validate_environment()
        self.assertIsInstance(status, dict)
        self.assertIn("groq_configured", status)
        self.assertIn("gemini_configured", status)

    def test_structured_logger(self):
        """Verify structured logger executes cleanly."""
        logger.info("Test logging message")
        self.assertIsNotNone(logger)

if __name__ == "__main__":
    unittest.main()
