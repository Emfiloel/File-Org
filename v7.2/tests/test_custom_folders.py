"""
Test Suite for Custom Folder Hierarchy Creation Feature
Tests hierarchical folder creation with numbered subfolders for v7.0
"""

import unittest
import sys
import os
import tempfile
import shutil

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


class TestParseHierarchy(unittest.TestCase):
    """Test parsing of hierarchy strings"""

    def test_parse_hierarchy_function_exists(self):
        """Should have parse_folder_hierarchy function"""
        try:
            from file_organizer import parse_folder_hierarchy
            self.assertTrue(callable(parse_folder_hierarchy))
        except ImportError:
            self.skipTest("parse_folder_hierarchy not yet implemented")

    def test_parse_single_level(self):
        """Should parse single-level hierarchy"""
        try:
            from file_organizer import parse_folder_hierarchy
            result = parse_folder_hierarchy("TMC")
            self.assertEqual(result, ["TMC"])
        except ImportError:
            self.skipTest("parse_folder_hierarchy not yet implemented")

    def test_parse_multi_level(self):
        """Should parse multi-level hierarchy with dash delimiter"""
        try:
            from file_organizer import parse_folder_hierarchy
            result = parse_folder_hierarchy("TMC-Aileron-LH")
            self.assertEqual(result, ["TMC", "Aileron", "LH"])
        except ImportError:
            self.skipTest("parse_folder_hierarchy not yet implemented")

    def test_parse_with_spaces(self):
        """Should handle spaces in folder names"""
        try:
            from file_organizer import parse_folder_hierarchy
            result = parse_folder_hierarchy("My Project-Sub Folder-Final")
            self.assertEqual(result, ["My Project", "Sub Folder", "Final"])
        except ImportError:
            self.skipTest("parse_folder_hierarchy not yet implemented")


class TestNumberedFolderGeneration(unittest.TestCase):
    """Test numbered folder generation"""

    def test_generate_numbered_folders_function_exists(self):
        """Should have generate_numbered_folder_names function"""
        try:
            from file_organizer import generate_numbered_folder_names
            self.assertTrue(callable(generate_numbered_folder_names))
        except ImportError:
            self.skipTest("generate_numbered_folder_names not yet implemented")

    def test_generate_numbered_folders_single_digit(self):
        """Should generate numbered folders with proper padding for single digits"""
        try:
            from file_organizer import generate_numbered_folder_names
            result = generate_numbered_folder_names(5)
            self.assertEqual(result, ["001", "002", "003", "004", "005"])
        except ImportError:
            self.skipTest("generate_numbered_folder_names not yet implemented")

    def test_generate_numbered_folders_double_digit(self):
        """Should generate numbered folders for double digits"""
        try:
            from file_organizer import generate_numbered_folder_names
            result = generate_numbered_folder_names(12)
            self.assertEqual(len(result), 12)
            self.assertEqual(result[0], "001")
            self.assertEqual(result[11], "012")
        except ImportError:
            self.skipTest("generate_numbered_folder_names not yet implemented")

    def test_generate_numbered_folders_triple_digit(self):
        """Should generate numbered folders for triple digits"""
        try:
            from file_organizer import generate_numbered_folder_names
            result = generate_numbered_folder_names(100)
            self.assertEqual(len(result), 100)
            self.assertEqual(result[0], "001")
            self.assertEqual(result[99], "100")
        except ImportError:
            self.skipTest("generate_numbered_folder_names not yet implemented")

    def test_generate_zero_folders(self):
        """Should handle zero folders gracefully"""
        try:
            from file_organizer import generate_numbered_folder_names
            result = generate_numbered_folder_names(0)
            self.assertEqual(result, [])
        except ImportError:
            self.skipTest("generate_numbered_folder_names not yet implemented")


class TestHierarchyCreation(unittest.TestCase):
    """Test actual folder hierarchy creation"""

    def setUp(self):
        """Create temp directory for tests"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_hierarchy_function_exists(self):
        """Should have create_custom_hierarchy function"""
        try:
            from file_organizer import create_custom_hierarchy
            self.assertTrue(callable(create_custom_hierarchy))
        except ImportError:
            self.skipTest("create_custom_hierarchy not yet implemented")

    def test_create_single_level_hierarchy(self):
        """Should create single-level folder"""
        try:
            from file_organizer import create_custom_hierarchy
            create_custom_hierarchy(self.test_dir, "TestFolder", 0)

            expected_path = os.path.join(self.test_dir, "TestFolder")
            self.assertTrue(os.path.exists(expected_path))
            self.assertTrue(os.path.isdir(expected_path))
        except ImportError:
            self.skipTest("create_custom_hierarchy not yet implemented")

    def test_create_nested_hierarchy(self):
        """Should create nested folder structure"""
        try:
            from file_organizer import create_custom_hierarchy
            create_custom_hierarchy(self.test_dir, "TMC-Aileron-LH", 0)

            # Check all levels exist
            level1 = os.path.join(self.test_dir, "TMC")
            level2 = os.path.join(level1, "Aileron")
            level3 = os.path.join(level2, "LH")

            self.assertTrue(os.path.exists(level1))
            self.assertTrue(os.path.exists(level2))
            self.assertTrue(os.path.exists(level3))
        except ImportError:
            self.skipTest("create_custom_hierarchy not yet implemented")

    def test_create_numbered_subfolders(self):
        """Should create numbered subfolders in final level"""
        try:
            from file_organizer import create_custom_hierarchy
            create_custom_hierarchy(self.test_dir, "TMC-Aileron-LH", 5)

            # Check numbered folders exist
            lh_path = os.path.join(self.test_dir, "TMC", "Aileron", "LH")

            for i in range(1, 6):
                numbered_folder = os.path.join(lh_path, f"{i:03d}")
                self.assertTrue(os.path.exists(numbered_folder),
                              f"Folder {numbered_folder} should exist")
        except ImportError:
            self.skipTest("create_custom_hierarchy not yet implemented")

    def test_create_50_numbered_folders(self):
        """Should create 50 numbered folders as per user example"""
        try:
            from file_organizer import create_custom_hierarchy
            create_custom_hierarchy(self.test_dir, "TMC-Aileron-LH", 50)

            lh_path = os.path.join(self.test_dir, "TMC", "Aileron", "LH")

            # Check first and last folder
            first_folder = os.path.join(lh_path, "001")
            last_folder = os.path.join(lh_path, "050")

            self.assertTrue(os.path.exists(first_folder))
            self.assertTrue(os.path.exists(last_folder))

            # Count total folders
            folders = os.listdir(lh_path)
            self.assertEqual(len(folders), 50)
        except ImportError:
            self.skipTest("create_custom_hierarchy not yet implemented")


def run_tests():
    """Run all custom folder tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("FILE ORGANIZER v7.0 - CUSTOM FOLDER HIERARCHY TEST SUITE")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("[PASS] ALL CUSTOM FOLDER TESTS PASSED")
    else:
        print("[FAIL] SOME CUSTOM FOLDER TESTS FAILED")
    print("=" * 70)

    sys.exit(0 if success else 1)
