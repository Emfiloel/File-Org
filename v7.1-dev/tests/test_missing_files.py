"""
Unit tests for Missing File Scanner (v7.1)

Tests pattern detection, gap finding, and placeholder file creation.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import file_organizer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_organizer import (
    detect_file_patterns,
    find_missing_files,
    create_placeholder_files,
    log_missing_files_operation
)


class TestMissingFileScanner(unittest.TestCase):
    """Test suite for missing file scanner functionality"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary test directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_files(self, filenames):
        """Helper: Create empty test files"""
        for filename in filenames:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                pass

    # ═══════════════════════════════════════════════════════════════════════
    # ── PATTERN DETECTION TESTS ───────────────────────────────────────────
    # ═══════════════════════════════════════════════════════════════════════

    def test_pure_numeric_pattern_detection(self):
        """Test detection of pure numeric files (001.jpg, 002.jpg)"""
        self.create_test_files(['001.jpg', '002.jpg', '005.jpg', '010.jpg'])

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 1)
        pattern_data = list(patterns.values())[0]

        self.assertTrue(pattern_data['is_pure_numeric'])
        self.assertEqual(pattern_data['padding'], 3)
        self.assertEqual(pattern_data['extension'], '.jpg')
        self.assertEqual(len(pattern_data['files']), 4)

    def test_prefixed_pattern_detection(self):
        """Test detection of prefixed files (IMG_001.jpg, IMG_003.jpg)"""
        self.create_test_files(['IMG_001.jpg', 'IMG_003.jpg', 'IMG_007.jpg'])

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 1)
        pattern_data = list(patterns.values())[0]

        self.assertFalse(pattern_data['is_pure_numeric'])
        self.assertEqual(pattern_data['prefix'], 'IMG_')
        self.assertEqual(pattern_data['padding'], 3)
        self.assertEqual(pattern_data['extension'], '.jpg')
        self.assertEqual(len(pattern_data['files']), 3)

    def test_multiple_patterns_in_same_folder(self):
        """Test detection when multiple patterns exist"""
        self.create_test_files([
            'IMG_001.jpg', 'IMG_003.jpg',
            'SCAN_010.pdf', 'SCAN_015.pdf',
            '001.png', '005.png'
        ])

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 3)  # IMG, SCAN, and pure numeric

    def test_no_padding_pattern(self):
        """Test files without zero-padding (file_1.jpg, file_20.jpg)"""
        self.create_test_files(['file_1.jpg', 'file_2.jpg', 'file_20.jpg'])

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 1)
        pattern_data = list(patterns.values())[0]

        self.assertEqual(pattern_data['prefix'], 'file_')
        # Padding should be 2 (from "20")
        self.assertEqual(pattern_data['padding'], 2)

    def test_pattern_with_suffix(self):
        """Test files with prefix + number + suffix (IMG_001_final.jpg)"""
        self.create_test_files([
            'IMG_001_final.jpg',
            'IMG_003_final.jpg',
            'IMG_005_final.jpg'
        ])

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 1)
        pattern_data = list(patterns.values())[0]

        self.assertEqual(pattern_data['prefix'], 'IMG_')
        self.assertEqual(pattern_data['suffix'], '_final')
        self.assertEqual(pattern_data['padding'], 3)

    def test_minimum_files_requirement(self):
        """Test that patterns need at least 2 files"""
        self.create_test_files(['001.jpg'])  # Only 1 file

        patterns = detect_file_patterns(self.test_dir)

        self.assertEqual(len(patterns), 0)  # Should be empty

    def test_mixed_extensions_separate_patterns(self):
        """Test that different extensions create separate patterns"""
        self.create_test_files(['001.jpg', '002.jpg', '001.pdf', '002.pdf'])

        patterns = detect_file_patterns(self.test_dir)

        # Should detect 2 patterns: .jpg and .pdf
        self.assertEqual(len(patterns), 2)

    # ═══════════════════════════════════════════════════════════════════════
    # ── GAP DETECTION TESTS ───────────────────────────────────────────────
    # ═══════════════════════════════════════════════════════════════════════

    def test_pure_numeric_starts_from_1(self):
        """Test that pure numeric files assume sequence starts at 1"""
        self.create_test_files(['010.jpg', '015.jpg', '020.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        # Should find 1-9, 11-14, 16-19
        self.assertIn(1, missing)
        self.assertIn(9, missing)
        self.assertIn(11, missing)
        self.assertIn(19, missing)
        self.assertEqual(len(missing), 9 + 4 + 4)  # 17 missing files

    def test_prefixed_fills_gaps_only(self):
        """Test that prefixed files only fill gaps between existing"""
        self.create_test_files(['IMG_010.jpg', 'IMG_015.jpg', 'IMG_020.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        # Should NOT include 1-9, only 11-14 and 16-19
        self.assertNotIn(1, missing)
        self.assertNotIn(9, missing)
        self.assertIn(11, missing)
        self.assertIn(19, missing)
        self.assertEqual(len(missing), 4 + 4)  # 8 missing files

    def test_find_missing_simple_gap(self):
        """Test finding simple gaps (1,2,5 -> missing 3,4)"""
        self.create_test_files(['001.jpg', '002.jpg', '005.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        self.assertEqual(missing, [3, 4])

    def test_no_missing_files(self):
        """Test when sequence is complete (no gaps)"""
        self.create_test_files(['001.jpg', '002.jpg', '003.jpg', '004.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        self.assertEqual(missing, [])

    def test_large_gap(self):
        """Test detection of large gaps"""
        self.create_test_files(['001.jpg', '100.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        self.assertEqual(len(missing), 98)  # 2-99

    # ═══════════════════════════════════════════════════════════════════════
    # ── PLACEHOLDER CREATION TESTS ────────────────────────────────────────
    # ═══════════════════════════════════════════════════════════════════════

    def test_create_placeholder_files(self):
        """Test creating placeholder files"""
        self.create_test_files(['001.jpg', '005.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        self.assertTrue(success)
        self.assertEqual(len(created), 3)  # 002, 003, 004

        # Verify files were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, '002.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, '003.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, '004.jpg')))

    def test_placeholder_preserves_padding(self):
        """Test that placeholders maintain zero-padding"""
        self.create_test_files(['001.jpg', '010.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        # Check that 002 has padding (not just "2.jpg")
        self.assertIn('002.jpg', created)
        self.assertIn('009.jpg', created)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, '002.jpg')))

    def test_placeholder_with_prefix(self):
        """Test placeholder creation with prefix"""
        self.create_test_files(['IMG_001.jpg', 'IMG_005.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        self.assertTrue(success)
        self.assertIn('IMG_002.jpg', created)
        self.assertIn('IMG_003.jpg', created)
        self.assertIn('IMG_004.jpg', created)

    def test_placeholder_with_suffix(self):
        """Test placeholder creation with suffix"""
        self.create_test_files(['IMG_001_final.jpg', 'IMG_003_final.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        self.assertTrue(success)
        self.assertIn('IMG_002_final.jpg', created)

    def test_placeholder_empty_file_size(self):
        """Test that placeholders are empty files (0 bytes)"""
        self.create_test_files(['001.jpg', '003.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        create_placeholder_files(self.test_dir, pattern_data, missing)

        placeholder_path = os.path.join(self.test_dir, '002.jpg')
        self.assertEqual(os.path.getsize(placeholder_path), 0)

    # ═══════════════════════════════════════════════════════════════════════
    # ── LOGGING TESTS ─────────────────────────────────────────────────────
    # ═══════════════════════════════════════════════════════════════════════

    def test_log_creation(self):
        """Test that missing_files.log is created"""
        self.create_test_files(['001.jpg', '003.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_key = list(patterns.keys())[0]
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)
        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        log_missing_files_operation(
            self.test_dir, pattern_key, pattern_data, missing, created
        )

        log_path = os.path.join(
            self.test_dir, '.file_organizer_data', 'missing_files.log'
        )
        self.assertTrue(os.path.exists(log_path))

    def test_log_content(self):
        """Test that log contains expected information"""
        self.create_test_files(['001.jpg', '005.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_key = list(patterns.keys())[0]
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)
        success, msg, created = create_placeholder_files(
            self.test_dir, pattern_data, missing
        )

        log_missing_files_operation(
            self.test_dir, pattern_key, pattern_data, missing, created
        )

        log_path = os.path.join(
            self.test_dir, '.file_organizer_data', 'missing_files.log'
        )

        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()

        self.assertIn('Pattern:', log_content)
        self.assertIn('Pure numeric', log_content)
        self.assertIn('Missing files:', log_content)
        self.assertIn('.jpg', log_content)

    # ═══════════════════════════════════════════════════════════════════════
    # ── EDGE CASES ────────────────────────────────────────────────────────
    # ═══════════════════════════════════════════════════════════════════════

    def test_empty_directory(self):
        """Test scanner on empty directory"""
        patterns = detect_file_patterns(self.test_dir)
        self.assertEqual(len(patterns), 0)

    def test_no_numeric_files(self):
        """Test directory with no numeric patterns"""
        self.create_test_files(['photo.jpg', 'image.png', 'document.pdf'])

        patterns = detect_file_patterns(self.test_dir)
        self.assertEqual(len(patterns), 0)

    def test_invalid_directory(self):
        """Test with non-existent directory"""
        patterns = detect_file_patterns('/nonexistent/path')
        self.assertEqual(len(patterns), 0)

    def test_sequence_starting_at_1(self):
        """Test pure numeric starting at 1 (no gaps before)"""
        self.create_test_files(['001.jpg', '002.jpg', '005.jpg'])

        patterns = detect_file_patterns(self.test_dir)
        pattern_data = list(patterns.values())[0]
        missing = find_missing_files(pattern_data)

        # Should only find 3, 4 (not before 1)
        self.assertEqual(missing, [3, 4])


if __name__ == '__main__':
    unittest.main()
