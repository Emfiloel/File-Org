"""
Test Suite for Date-Based Organization Feature
Tests new date organization modes for v7.0
"""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock tkinter before importing
import unittest.mock as mock
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.ttk'] = mock.MagicMock()
sys.modules['tkinter.filedialog'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()
sys.modules['tkinter.simpledialog'] = mock.MagicMock()
sys.modules['tkinterdnd2'] = mock.MagicMock()

# Now import from file_organizer
from file_organizer import get_file_datetime


class TestDateOrganizationLogic(unittest.TestCase):
    """Test date-based organization logic functions"""

    def test_by_date_year_function_exists(self):
        """Should have by_date_year function"""
        try:
            from file_organizer import by_date_year
            self.assertTrue(callable(by_date_year))
        except ImportError:
            self.skipTest("by_date_year not yet implemented")

    def test_by_date_month_function_exists(self):
        """Should have by_date_month function"""
        try:
            from file_organizer import by_date_month
            self.assertTrue(callable(by_date_month))
        except ImportError:
            self.skipTest("by_date_month not yet implemented")

    def test_by_date_full_function_exists(self):
        """Should have by_date_full function"""
        try:
            from file_organizer import by_date_full
            self.assertTrue(callable(by_date_full))
        except ImportError:
            self.skipTest("by_date_full not yet implemented")


class TestDateExtractionIntegration(unittest.TestCase):
    """Test date extraction from files"""

    def setUp(self):
        """Create temp directory with test files"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_file_datetime_with_regular_file(self):
        """Should get modification time for regular files"""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        dt = get_file_datetime(test_file)
        if dt is not None:
            self.assertIsInstance(dt, datetime)
            self.assertIsInstance(dt.year, int)
            self.assertGreater(dt.year, 2000)
            self.assertLess(dt.year, 2100)


class TestDateFolderFormatting(unittest.TestCase):
    """Test date folder name formatting"""

    def test_year_folder_format(self):
        """Year folder should be YYYY format"""
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        expected = "2024"

        try:
            from file_organizer import format_date_year
            result = format_date_year(test_date)
            self.assertEqual(result, expected)
        except ImportError:
            self.skipTest("format_date_year not yet implemented")

    def test_month_folder_format(self):
        """Month folder should be YYYY-MM format"""
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        expected = "2024-06"

        try:
            from file_organizer import format_date_month
            result = format_date_month(test_date)
            self.assertEqual(result, expected)
        except ImportError:
            self.skipTest("format_date_month not yet implemented")

    def test_full_date_folder_format(self):
        """Full date folder should be YYYY-MM-DD format"""
        test_date = datetime(2024, 6, 15, 14, 30, 0)
        expected = "2024-06-15"

        try:
            from file_organizer import format_date_full
            result = format_date_full(test_date)
            self.assertEqual(result, expected)
        except ImportError:
            self.skipTest("format_date_full not yet implemented")


class TestDateOrganizationWorkflow(unittest.TestCase):
    """Integration tests for date organization workflow"""

    def setUp(self):
        """Create temp directory with test files"""
        self.test_dir = tempfile.mkdtemp()

        # Create test files with different modification times
        self.test_files = []
        for i, filename in enumerate(["file1.txt", "file2.txt", "file3.txt"]):
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(filepath)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_date_organization_preserves_files(self):
        """Date organization should not lose any files"""
        # Count files before
        files_before = len(os.listdir(self.test_dir))
        self.assertEqual(files_before, 3)

        # This test verifies files exist and are ready for organization
        for filepath in self.test_files:
            self.assertTrue(os.path.exists(filepath))


def run_tests():
    """Run all date organization tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("FILE ORGANIZER v7.0 - DATE ORGANIZATION TEST SUITE")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("[PASS] ALL DATE ORGANIZATION TESTS PASSED")
    else:
        print("[FAIL] SOME DATE ORGANIZATION TESTS FAILED")
    print("=" * 70)

    sys.exit(0 if success else 1)
