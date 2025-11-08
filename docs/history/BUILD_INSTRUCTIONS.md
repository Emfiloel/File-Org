# File Organizer v6.3 - Test Suite Build Instructions

## Overview

This document explains how to build the standalone test executable for File Organizer v6.3.

## Prerequisites

### 1. Install Python
- Python 3.8 or higher
- Download from: https://www.python.org/downloads/

### 2. Install PyInstaller
```bash
pip install pyinstaller
```

### 3. Verify Installation
```bash
pyinstaller --version
```

## Building the Executable

### Method 1: Using the Spec File (Recommended)

1. Open Command Prompt or Terminal
2. Navigate to the v6.3 directory:
   ```bash
   cd "I:\Templates\Previous Versions\v6.3"
   ```

3. Run PyInstaller with the spec file:
   ```bash
   pyinstaller build_test_exe.spec
   ```

4. Find the executable:
   - Location: `dist/FileOrganizerTest.exe`
   - This is a standalone executable that can be run on any Windows machine

### Method 2: Quick Build (Without Spec File)

```bash
pyinstaller --onefile --console --name FileOrganizerTest test_all_features.py
```

## Running the Test Executable

### Option 1: Double-Click
- Simply double-click `FileOrganizerTest.exe`
- A console window will open and run all tests
- Results will be displayed in the console
- A detailed report file will be generated in the same directory

### Option 2: Command Line
```bash
cd dist
FileOrganizerTest.exe
```

## Test Output

### Console Output
The test program will display:
- Real-time test progress
- Color-coded results (PASSED/FAILED/SKIPPED)
- Detailed summary at the end
- Total execution time

### Test Report File
- Filename: `test_report_YYYYMMDD_HHMMSS.txt`
- Location: Same directory as the executable
- Contains: Complete test results with timestamps

## What Gets Tested

### Organization Modes (7 tests)
1. ✓ By Extension (.pdf, .jpg, etc.)
2. ✓ By Alphabet (A-Z, 0-9, special)
3. ✓ By Numeric (1, 2, 3...)
4. ✓ By IMG/DSC Tags
5. ✓ Smart Pattern Detection
6. ✓ Sequential Pattern
7. ✓ Smart Pattern with Prompts

### v6.3 New Features (5 tests)
1. ✓ Auto-Create A-Z Folders
2. ✓ Auto-Create 0-9 Folders
3. ✓ Pattern Search & Collect
4. ✓ Recent Directories
5. ✓ Tabbed Interface

### Core Features (7 tests)
1. ✓ Duplicate Detection (Hash-based)
2. ✓ Reserved Name Sanitization (CON, PRN, etc.)
3. ✓ Pattern Scanner (7 pattern types)
4. ✓ Operation Logging
5. ✓ Configuration Management
6. ✓ Extract Functionality
7. ✓ Collision Handling

### v6.1 & v6.2 Features (3 tests)
1. ✓ In-Place Organization (v6.2)
2. ✓ Skip Folders (# prefix) (v6.2)
3. ✓ VERSION Constant (v6.1)

### Performance (2 tests)
1. ✓ Generator Efficiency
2. ✓ Batch Processing

### Edge Cases (3 tests)
1. ✓ Empty Source Directory
2. ✓ Special Characters in Names
3. ✓ Deeply Nested Structures

## Total: 27 Comprehensive Tests

## Troubleshooting

### Issue: "Module not found" errors during build
**Solution:**
```bash
pip install tkinter hashlib sqlite3 pathlib
```

### Issue: Executable doesn't run
**Solution:**
- Make sure you're running on Windows
- Check antivirus - it may block unsigned executables
- Try running as Administrator

### Issue: Tests fail
**Solution:**
- Check that `master_file_6_3.py` is in the same directory
- Verify write permissions in the test directory
- Check available disk space (tests create temporary files)

### Issue: PyInstaller not found
**Solution:**
```bash
python -m pip install --upgrade pip
pip install pyinstaller
```

## Advanced Options

### Creating a Windowed Executable (No Console)
Edit `build_test_exe.spec`:
```python
console=False  # Change from True to False
```

### Adding an Icon
1. Create or download an .ico file
2. Edit `build_test_exe.spec`:
```python
icon='path/to/your/icon.ico'
```

### Optimizing Size
Use UPX compression (already enabled in spec file):
```bash
# UPX is automatically applied if available
# To install UPX: https://upx.github.io/
```

## Distribution

The generated `FileOrganizerTest.exe` is completely standalone:
- ✓ No Python installation required on target machine
- ✓ No external dependencies
- ✓ Can be copied to any Windows computer
- ✓ Can be distributed via USB, email, or network share
- ✓ Approximately 10-20 MB in size

## File Structure After Build

```
v6.3/
├── test_all_features.py          # Source test program
├── build_test_exe.spec            # PyInstaller spec file
├── BUILD_INSTRUCTIONS.md          # This file
├── TEST_USAGE.md                  # Usage instructions
├── build/                         # Build artifacts (can be deleted)
├── dist/                          # Output directory
│   └── FileOrganizerTest.exe     # ★ STANDALONE EXECUTABLE ★
└── test_report_*.txt              # Generated after running tests
```

## Notes

- The executable includes the test program and all necessary dependencies
- Tests are non-destructive and use temporary directories
- All test files are automatically cleaned up after execution
- The executable is portable and can run from any location
- No installation required - just run the .exe

## Support

If you encounter any issues:
1. Check the test report file for detailed error messages
2. Verify all prerequisites are installed
3. Ensure you have proper permissions
4. Check antivirus settings (may block PyInstaller executables)

---

**Last Updated:** 2025-11-06
**Version:** 1.0
**Compatible with:** File Organizer v6.3
