"""
Unit tests for core package (constants, exceptions, interfaces).
"""

import unittest
from core.constants import APP_NAME, APP_VERSION
from core.exceptions import JarvisException, ToolExecutionError, PlannerError

class TestCorePackage(unittest.TestCase):
    def test_core_constants(self):
        self.assertEqual(APP_NAME, "J.A.R.V.I.S. AI OS")
        self.assertEqual(APP_VERSION, "1.7.0")

    def test_custom_exceptions(self):
        with self.assertRaises(JarvisException):
            raise ToolExecutionError("Test tool exception")

if __name__ == "__main__":
    unittest.main()
