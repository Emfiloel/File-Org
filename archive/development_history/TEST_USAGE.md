# File Organizer v6.3 - Test Suite Usage Guide

## Quick Start

### Running the Test Executable

1. **Locate the executable:**
   - `dist/FileOrganizerTest.exe`

2. **Run it:**
   - Double-click the executable
   - OR run from command line: `FileOrganizerTest.exe`

3. **View results:**
   - Tests run automatically
   - Results displayed in console window
   - Detailed report saved as `test_report_YYYYMMDD_HHMMSS.txt`

## What Happens When You Run It

### Phase 1: Environment Setup (2-3 seconds)
```
✓ Successfully imported File Organizer v6.3
✓ Created test environment:
  Source: C:\Temp\file_org_test_XXXXX\source
  Target: C:\Temp\file_org_test_XXXXX\target
  Test files: 40+
```

### Phase 2: Test Execution (30-60 seconds)

#### Category 1: Organization Modes
Tests all 7 ways to organize files:
- By Extension (.pdf → PDF folder)
- By Alphabet (apple.txt → A folder)
- By Numeric (42.txt → 42 folder)
- By IMG/DSC Tags (IMG_001.jpg → IMG folder)
- Smart Pattern (vacation-001.jpg → vacation folder)
- Sequential Pattern (report-001.pdf → report folder)

#### Category 2: v6.3 New Features
Tests the 4 major enhancements in v6.3:
- Auto-create A-Z folders (26 folders)
- Auto-create 0-9 folders (10 folders)
- Pattern search & collect (IMG*, *-001-*, etc.)
- Recent directories tracking (last 10 paths)
- Tabbed interface structure

#### Category 3: Core Features
Tests essential functionality:
- Duplicate detection (hash-based MD5)
- Reserved name sanitization (CON → CON_safe)
- Pattern scanner (7 pattern types)
- Operation logging (JSONL format)
- Configuration management
- Extract files from subfolders
- Collision handling (file.txt → file (2).txt)

#### Category 4: v6.1 & v6.2 Features
Tests backward compatibility:
- In-place organization (v6.2)
- Skip folders with # prefix (v6.2)
- VERSION constant verification (v6.1)

#### Category 5: Performance
Tests optimization features:
- Generator efficiency (memory-efficient file collection)
- Batch processing (10,000 files per batch)

#### Category 6: Edge Cases
Tests unusual scenarios:
- Empty source directories
- Special characters in filenames
- Deeply nested directory structures

### Phase 3: Cleanup & Reporting (1-2 seconds)
```
✓ Cleaned up test environment
✓ Test report saved: test_report_20251106_143022.txt
```

## Understanding Test Results

### Result Indicators

```
[PASSED] ✓ Test Name
  └─ Success message with details

[FAILED] ✗ Test Name
  └─ Error message explaining failure

[SKIPPED] ⚠ Test Name
  └─ Reason for skipping (GUI tests, etc.)
```

### Example Output

```
================================================================================
CATEGORY 1: ORGANIZATION MODES (7 tests)
================================================================================
[PASSED] Organization Mode: By Extension
  └─ PDF→.pdf, JPG→.jpg, None→no_extension

[PASSED] Organization Mode: By Alphabet
  └─ A→A, B→B, Num→0-9, Spec→!@#$

[PASSED] Organization Mode: By Numeric
  └─ 1→1, 42→42, Text→Others
```

## Summary Report

At the end, you'll see:

```
================================================================================
TEST SUMMARY
================================================================================
Total Tests: 27
Passed: 25
Failed: 0
Skipped: 2
Duration: 45.32s
================================================================================
```

### Success Criteria

- **All Passed (0 Failed):** ✓ All features working perfectly
- **Some Failed:** ✗ Issues detected - check detailed report
- **Some Skipped:** ⚠ GUI tests or optional features

## Detailed Report File

### Location
- Same directory as the executable
- Named: `test_report_YYYYMMDD_HHMMSS.txt`

### Contents

```
================================================================================
FILE ORGANIZER v6.3 - TEST REPORT
================================================================================

Test Date: 2025-11-06 14:30:22
Total Tests: 27
Passed: 25
Failed: 0
Skipped: 2
Duration: 45.32s

================================================================================

DETAILED RESULTS:

[14:30:25] [PASSED] Organization Mode: By Extension
    PDF→.pdf, JPG→.jpg, None→no_extension

[14:30:26] [PASSED] Organization Mode: By Alphabet
    A→A, B→B, Num→0-9, Spec→!@#$

... (all test results with timestamps)
```

## What Each Test Verifies

### Organization Mode Tests

| Test | Verifies | Example |
|------|----------|---------|
| By Extension | Files grouped by extension | document.pdf → .pdf/ |
| By Alphabet | First letter organization | apple.txt → A/ |
| By Numeric | Pure number files | 42.txt → 42/ |
| IMG/DSC | Camera tag detection | IMG_001.jpg → IMG/ |
| Smart Pattern | Automatic pattern detection | vacation-001.jpg → vacation/ |
| Sequential | Number sequence detection | report-001.pdf → report/ |

### v6.3 Feature Tests

| Test | Verifies | Details |
|------|----------|---------|
| Create A-Z Folders | Auto-folder creation | 26 folders (A-Z) |
| Create 0-9 Folders | Numeric folders | 10 folders (0-9) |
| Pattern Search | Wildcard matching | IMG*, *-001-*, *.jpg |
| Recent Directories | Path history | Last 10 used paths |
| Tabbed Interface | UI structure | 3 tabs verified |

### Core Feature Tests

| Test | Verifies | Purpose |
|------|----------|---------|
| Duplicate Detection | Hash matching | Find identical files |
| Reserved Names | Security | Prevent Windows issues |
| Pattern Scanner | Analysis | Detect 7 pattern types |
| Operation Logging | Audit trail | Track all changes |
| Config Management | Settings | Load/save configuration |
| Extract Files | Pull from subfolders | Flatten directory |
| Collision Handling | Naming conflicts | file.txt → file (2).txt |

## Running from Command Line

### Basic Usage
```bash
FileOrganizerTest.exe
```

### Capture Output to File
```bash
FileOrganizerTest.exe > test_output.txt 2>&1
```

### Automated Testing
```batch
@echo off
echo Running File Organizer Tests...
FileOrganizerTest.exe
if %ERRORLEVEL% EQU 0 (
    echo All tests passed!
) else (
    echo Some tests failed. Check test_report.txt
)
pause
```

## Interpreting Results

### All Tests Passed ✓
- The File Organizer is working correctly
- All 27 features are functional
- Safe to use for production

### Some Tests Failed ✗
- Check the detailed report for specifics
- Failed tests indicate broken functionality
- Review error messages for troubleshooting

### Some Tests Skipped ⚠
- Usually GUI-related tests (can't test without display)
- Not a problem - these are informational
- Core functionality still validated

## Temporary Files

### During Testing
The test program creates temporary files in:
- `%TEMP%\file_org_test_XXXXX\`

### After Testing
- All temporary files are automatically deleted
- Only the test report remains
- No cleanup required

## Performance Notes

### Expected Duration
- **Fast:** 30-45 seconds on modern systems
- **Slow:** 60-90 seconds on older systems
- **Very Slow (>2 minutes):** Possible disk or antivirus issues

### Disk Space Required
- Temporary: ~50 MB during test
- Final: <1 MB (just the report)

## Troubleshooting

### Test Failures

**Duplicate Detection Failed**
- Ensure write permissions in temp directory
- Check available disk space

**Reserved Name Sanitization Failed**
- Windows-specific test
- Should pass on Windows, may skip on Linux

**Pattern Tests Failed**
- Check master_file_6_3.py is present
- Verify file is not corrupted

### Performance Issues

**Tests Running Slowly**
- Close other programs
- Check antivirus (may scan temp files)
- Ensure sufficient RAM available

**Executable Won't Start**
- Right-click → Run as Administrator
- Check antivirus quarantine
- Verify Windows compatibility

## Advanced Usage

### Integration with CI/CD
```batch
REM Run tests and check exit code
FileOrganizerTest.exe
if %ERRORLEVEL% NEQ 0 exit /b 1
```

### Automated Reporting
The test report is machine-readable and can be parsed for:
- Test counts
- Pass/fail status
- Duration metrics
- Individual test results

### Scheduled Testing
Create a Windows Task to run tests daily:
```batch
schtasks /create /tn "FileOrganizerTest" /tr "C:\path\to\FileOrganizerTest.exe" /sc daily /st 02:00
```

## Best Practices

1. **Run Before Updates:** Test before deploying new versions
2. **Keep Reports:** Archive reports for regression testing
3. **Regular Testing:** Run weekly or after major changes
4. **Clean Environment:** Close other programs during testing
5. **Review Failures:** Don't ignore failed tests

## Getting Help

If tests fail consistently:

1. Check `test_report_*.txt` for details
2. Verify `master_file_6_3.py` is present and updated
3. Ensure write permissions in program directory
4. Try running as Administrator
5. Check Windows Event Viewer for errors

## Example Complete Run

```
File Organizer v6.3 - Comprehensive Test Suite
Generated: 2025-11-06 14:30:22

================================================================================
FILE ORGANIZER v6.3 - COMPREHENSIVE TEST SUITE
================================================================================

Starting test execution...

Setting up test environment...
✓ Created test environment:
  Source: C:\Temp\file_org_test_abc123\source
  Target: C:\Temp\file_org_test_abc123\target
  Test files: 40

================================================================================
CATEGORY 1: ORGANIZATION MODES (7 tests)
================================================================================
[PASSED] Organization Mode: By Extension
[PASSED] Organization Mode: By Alphabet
[PASSED] Organization Mode: By Numeric
[PASSED] Organization Mode: By IMG/DSC Tags
[PASSED] Organization Mode: Smart Pattern Detection
[PASSED] Organization Mode: Sequential Pattern

... (all categories) ...

Cleaning up...
✓ Cleaned up test environment

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 27
Passed: 25
Failed: 0
Skipped: 2
Duration: 45.32s
================================================================================

✓ Test report saved: test_report_20251106_143022.txt

Press Enter to exit...
```

---

**Last Updated:** 2025-11-06
**Version:** 1.0
**For:** File Organizer v6.3 Test Suite
