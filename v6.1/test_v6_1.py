"""
Test Suite for File Organizer v6.1
Tests v6.1 Quick Wins:
- VERSION constant
- Windows reserved name sanitization (Critical #36)
- Case-insensitive Windows path security check
"""

import unittest
import sys
import os

# Mock tkinter before importing
import unittest.mock as mock
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.ttk'] = mock.MagicMock()
sys.modules['tkinter.filedialog'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()
sys.modules['tkinter.simpledialog'] = mock.MagicMock()
sys.modules['tkinterdnd2'] = mock.MagicMock()

# Now import from master_file_6_1
from master_file_6_1 import VERSION, sanitize_folder_name, is_safe_directory

class TestVersionConstant(unittest.TestCase):
    """Test that VERSION constant exists and is correct"""

    def test_version_exists(self):
        """VERSION constant should exist"""
        self.assertIsNotNone(VERSION)

    def test_version_value(self):
        """VERSION should be v6.1"""
        self.assertIn("6.1", VERSION)
        self.assertIn("Enhanced", VERSION)


class TestCritical36_ReservedNames(unittest.TestCase):
    """Test Critical #36 fix: Windows reserved folder name sanitization"""

    def test_con_sanitized(self):
        """CON should be sanitized to CON_"""
        result = sanitize_folder_name("CON")
        self.assertEqual(result, "CON_")

    def test_prn_sanitized(self):
        """PRN should be sanitized to PRN_"""
        result = sanitize_folder_name("PRN")
        self.assertEqual(result, "PRN_")

    def test_aux_sanitized(self):
        """AUX should be sanitized to AUX_"""
        result = sanitize_folder_name("AUX")
        self.assertEqual(result, "AUX_")

    def test_com1_sanitized(self):
        """COM1 should be sanitized to COM1_"""
        result = sanitize_folder_name("COM1")
        self.assertEqual(result, "COM1_")

    def test_lpt1_sanitized(self):
        """LPT1 should be sanitized to LPT1_"""
        result = sanitize_folder_name("LPT1")
        self.assertEqual(result, "LPT1_")

    def test_case_insensitive(self):
        """Reserved names should be detected case-insensitively"""
        self.assertEqual(sanitize_folder_name("con"), "con_")
        self.assertEqual(sanitize_folder_name("Con"), "Con_")
        self.assertEqual(sanitize_folder_name("CON"), "CON_")

    def test_safe_names_unchanged(self):
        """Safe folder names should pass through unchanged"""
        self.assertEqual(sanitize_folder_name("Photos"), "Photos")
        self.assertEqual(sanitize_folder_name("Documents"), "Documents")
        self.assertEqual(sanitize_folder_name("IMG"), "IMG")


class TestCaseInsensitivePathSecurity(unittest.TestCase):
    """Test case-insensitive path security check on Windows"""

    def test_lowercase_windows_blocked(self):
        """c:\\windows should be blocked (lowercase)"""
        if os.name != 'nt':  # Windows only
            self.skipTest("Windows-specific test")

        is_safe, reason = is_safe_directory("c:\\windows")
        self.assertFalse(is_safe)
        self.assertIn("system directory", reason.lower())

    def test_mixed_case_windows_blocked(self):
        """C:\\WiNdOwS should be blocked (mixed case)"""
        if os.name != 'nt':
            self.skipTest("Windows-specific test")

        is_safe, reason = is_safe_directory("C:\\WiNdOwS")
        self.assertFalse(is_safe)
        self.assertIn("system directory", reason.lower())

    def test_uppercase_windows_blocked(self):
        """C:\\WINDOWS should be blocked (uppercase)"""
        if os.name != 'nt':
            self.skipTest("Windows-specific test")

        is_safe, reason = is_safe_directory("C:\\WINDOWS")
        self.assertFalse(is_safe)
        self.assertIn("system directory", reason.lower())


def run_tests():
    """Run all v6.1 tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVersionConstant))
    suite.addTests(loader.loadTestsFromTestCase(TestCritical36_ReservedNames))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseInsensitivePathSecurity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("FILE ORGANIZER v6.1 - TEST SUITE")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("[PASS] ALL v6.1 TESTS PASSED")
    else:
        print("[FAIL] SOME v6.1 TESTS FAILED")
    print("=" * 70)

    sys.exit(0 if success else 1)
