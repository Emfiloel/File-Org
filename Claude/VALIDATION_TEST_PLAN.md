# VALIDATION TEST PLAN
## File Organizer - Tickets #1-7

**Validator:** Please execute these test cases and report PASS/FAIL for each.

---

## 🔐 TICKET #1: PATH TRAVERSAL VULNERABILITY

### Test Case 1.1: Block Windows System Directory
**Setup:**
- OS: Windows
- Source: `C:\Windows`
- Target: `C:\Users\Test\Organized`

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error dialog: "Cannot organize system directory: C:\Windows"
- Error logged in `file_organizer.log`
- No files moved

**Pass Criteria:** System directory blocked with clear error message

---

### Test Case 1.2: Block Program Files
**Setup:**
- OS: Windows
- Source: `C:\Users\Test\Photos`
- Target: `C:\Program Files`

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error dialog: "Cannot organize system directory: C:\Program Files"
- No files moved

**Pass Criteria:** System directory blocked

---

### Test Case 1.3: Allow User Directory
**Setup:**
- OS: Windows
- Source: `C:\Users\Test\Photos`
- Target: `C:\Users\Test\Organized`

**Action:** Click "Preview Extension"

**Expected Result:**
- ✅ Operation allowed
- Preview shows file organization plan
- No errors

**Pass Criteria:** User directory accepted

---

### Test Case 1.4: Symlink Following
**Setup:**
- Create symlink: `C:\Users\Test\MyLink` → `C:\Windows`
- Source: `C:\Users\Test\MyLink`

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error shows real path: "Cannot organize system directory: C:\Windows"

**Pass Criteria:** Symlinks resolved to real paths and blocked if system directory

---

## 🚫 TICKET #2: SILENT EXCEPTION SWALLOWING

### Test Case 2.1: Save Mappings Failure (Disk Full)
**Setup:**
- Fill disk to 100% (or make folder read-only)
- Use "Smart Pattern +" mode
- Classify a file (triggers save)

**Action:** Enter folder name for unclassified file

**Expected Result:**
- ❌ Error dialog shown: "Failed to save folder mappings: [error details]"
- Error printed to console
- Error logged in `file_organizer.log`
- User KNOWS save failed

**Pass Criteria:** User is alerted (not silent failure)

---

### Test Case 2.2: Load Mappings Failure (Corrupted File)
**Setup:**
- Create `folder_mappings.json` with invalid JSON: `{invalid json`

**Action:** Start application

**Expected Result:**
- ⚠️ Warning printed to console
- Application continues (doesn't crash)
- Empty mappings used

**Pass Criteria:** Graceful handling with warning

---

### Test Case 2.3: Theme Loading Failure
**Setup:**
- Modify code temporarily to force theme error
- Or run on system with no themes available

**Action:** Start application

**Expected Result:**
- ✅ Application starts normally
- Falls back to default theme
- No crash

**Pass Criteria:** Specific exception caught (tk.TclError only)

---

### Test Case 2.4: Ctrl+C Interruption
**Setup:**
- Start long operation (organize 1000+ files)

**Action:** Press Ctrl+C in console

**Expected Result:**
- ✅ Application stops immediately
- KeyboardInterrupt NOT caught
- Clean exit

**Pass Criteria:** User can still interrupt with Ctrl+C

---

## ⚠️ TICKET #3: MISSING INPUT VALIDATION

### Test Case 3.1: Source == Target
**Setup:**
- Source: `C:\Users\Test\Photos`
- Target: `C:\Users\Test\Photos`

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error dialog: "Source and target directories cannot be the same!"
- Error logged
- No files moved

**Pass Criteria:** Same directory rejected

---

### Test Case 3.2: Target Inside Source (Infinite Loop)
**Setup:**
- Source: `C:\Users\Test\Photos`
- Target: `C:\Users\Test\Photos\Organized`

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error dialog: "Target cannot be inside source!"
- Shows both paths in error
- No files moved

**Pass Criteria:** Recursive operation blocked

---

### Test Case 3.3: Low Disk Space Warning
**Setup:**
- Ensure < 1GB free space on target drive
- Or check logs after any operation

**Action:** Click any organize button

**Expected Result:**
- ⚠️ Warning in `file_organizer.log`: "Low disk space: X.XX GB free"
- Operation continues (just warning, not blocking)

**Pass Criteria:** Low space logged (not blocking, just warning)

---

### Test Case 3.4: No Write Permission
**Setup:**
- Target: Folder with read-only permissions
- Or system folder (if not already blocked by Ticket #1)

**Action:** Click any organize button

**Expected Result:**
- ❌ Operation blocked
- Error dialog mentions permission issue

**Pass Criteria:** Permission check works

---

## 🏃 TICKET #4: RACE CONDITIONS

### Test Case 4.1: File Deleted Mid-Operation
**Setup:**
- Source folder with 100 files
- Start organizing to target

**Action:** **While operation is running**, delete 10 source files manually

**Expected Result:**
- ✅ Operation completes
- Final message: "X succeeded, Y failed" (where Y = 10)
- Errors logged: "Source file no longer exists"
- No crash

**Pass Criteria:** Graceful handling of disappeared files

---

### Test Case 4.2: File Modified During Operation
**Setup:**
- Source folder with files
- Start organizing

**Action:** **While running**, open a source file in editor and save it

**Expected Result:**
- ✅ File either moved successfully or skipped
- No crash or corruption
- Status reported correctly

**Pass Criteria:** No crashes or data corruption

---

### Test Case 4.3: Folder Creation Fails
**Setup:**
- Make target directory read-only
- Or use invalid target path

**Action:** Try to organize files

**Expected Result:**
- ❌ Errors reported for each file
- Clear error messages
- Logged: "Cannot create destination folder"

**Pass Criteria:** Folder creation failures reported

---

## 📝 TICKET #5: LOGGING INFRASTRUCTURE

### Test Case 5.1: Log File Created
**Setup:**
- Fresh install (delete `file_organizer.log` if exists)

**Action:** Run application, perform any operation

**Expected Result:**
- ✅ `file_organizer.log` created in application directory
- Contains timestamped entries
- Readable format

**Pass Criteria:** Log file exists and is properly formatted

---

### Test Case 5.2: Log Contents
**Setup:**
- Perform various operations (success and failure)

**Action:** Open `file_organizer.log`

**Expected Result:**
Log contains:
```
2025-10-31 XX:XX:XX - INFO - Starting organization: X source(s) -> [path]
2025-10-31 XX:XX:XX - WARNING - Low disk space: X.XX GB free
2025-10-31 XX:XX:XX - ERROR - Failed to move file.jpg: [error]
2025-10-31 XX:XX:XX - INFO - Operation complete: X succeeded, Y failed
```

**Pass Criteria:** All key events logged with levels (INFO/WARNING/ERROR)

---

### Test Case 5.3: Multiple Sessions
**Setup:**
- Run application multiple times
- Perform operations each time

**Action:** Check log file

**Expected Result:**
- ✅ Log appends (doesn't overwrite)
- Each session's operations visible
- Chronological order maintained

**Pass Criteria:** Log persists across sessions

---

## ✈️ TICKET #6: PRE-FLIGHT VALIDATION

### Test Case 6.1: All Validation Gates
**Setup:**
- Various invalid configurations

**Action:** Try each:
1. No source selected
2. No target selected
3. Source is system directory
4. Target is system directory
5. Source == Target
6. Target inside Source

**Expected Result:**
- Each blocked with specific error
- Fast response (< 1 second)
- No partial operations
- Clear error messages

**Pass Criteria:** All validation gates work, fail fast

---

### Test Case 6.2: Validation Order
**Setup:**
- Source: `C:\Windows`
- Target: Same as Source

**Action:** Click organize

**Expected Result:**
- ✅ First error shown (whichever check runs first)
- Only ONE error dialog (not multiple)
- No partial validation

**Pass Criteria:** Validation stops at first failure

---

## 📚 TICKET #7: DOCUMENTATION

### Test Case 7.1: Docstring Coverage
**Setup:**
- Open `master_file_2.py` in IDE/editor

**Action:** Hover over key functions:
- `validate_operation()`
- `is_safe_directory()`
- `move_file()`
- `detect_folder_name()`
- `run_organizer()`

**Expected Result:**
- ✅ IDE shows docstring with:
  - Description
  - Args/parameters
  - Returns
  - Examples (where applicable)

**Pass Criteria:** Key functions have comprehensive docstrings

---

### Test Case 7.2: Code Comments
**Setup:**
- Open `master_file_2.py`

**Action:** Review exception handlers

**Expected Result:**
- ✅ Each exception handler has comment explaining:
  - What error is being caught
  - Why it's expected
  - What happens when caught

**Pass Criteria:** Exception handlers documented

---

## 🔄 INTEGRATION TESTS

### Test Case INT-1: Full Happy Path
**Setup:**
- Source: `C:\Users\Test\TestPhotos` (100 test files)
- Target: `C:\Users\Test\Organized`
- Files named: `IMG_001.jpg` through `IMG_100.jpg`

**Action:** Click "IMG/DSC Only"

**Expected Result:**
- ✅ All validations pass
- 100 files moved to `Organized\IMG\`
- Success message: "Successfully organized 100 files"
- Logged: "Operation complete: 100 succeeded, 0 failed"

**Pass Criteria:** Full operation succeeds with proper logging and feedback

---

### Test Case INT-2: Full Failure Path
**Setup:**
- Source: `C:\Windows`
- Target: `C:\Windows\Organized`

**Action:** Click any organize button

**Expected Result:**
- ❌ Multiple validation failures caught:
  - System directory detected
  - Possibly others
- Clear error shown
- No partial operation
- Everything logged

**Pass Criteria:** Multiple validation issues handled gracefully

---

### Test Case INT-3: Partial Success Path
**Setup:**
- Source: Mix of:
  - 50 normal files (movable)
  - 10 locked files (read-only)
- Target: Valid directory

**Action:** Organize files

**Expected Result:**
- ⚠️ Operation completes with warnings
- Final message: "50 files moved, 10 files failed"
- Each failure logged with reason
- User informed

**Pass Criteria:** Partial failures handled and reported

---

## 🚨 STRESS TESTS

### Stress Test 1: Large File Count
**Setup:**
- 10,000+ files in source

**Action:** Organize to target

**Expected Result:**
- ✅ Completes without crash
- Memory usage reasonable
- Progress bar updates
- All operations logged

**Pass Criteria:** Handles large datasets

---

### Stress Test 2: Deep Directory Structure
**Setup:**
- Source with 20+ levels of nested folders

**Action:** Organize recursively

**Expected Result:**
- ✅ All files found and organized
- No stack overflow
- Reasonable performance

**Pass Criteria:** Handles deep recursion

---

### Stress Test 3: Rapid Operations
**Setup:**
- Queue multiple operations quickly

**Action:** Click organize buttons rapidly 5 times

**Expected Result:**
- ✅ Each operation completes in order
- No race conditions between operations
- Progress bars accurate

**Pass Criteria:** Handles rapid user input

---

## 📊 VALIDATION CHECKLIST

Mark each as PASS/FAIL:

### Security (Ticket #1)
- [ ] Test 1.1: Block Windows System Directory
- [ ] Test 1.2: Block Program Files
- [ ] Test 1.3: Allow User Directory
- [ ] Test 1.4: Symlink Following

### Exception Handling (Ticket #2)
- [ ] Test 2.1: Save Mappings Failure
- [ ] Test 2.2: Load Mappings Failure
- [ ] Test 2.3: Theme Loading Failure
- [ ] Test 2.4: Ctrl+C Interruption

### Input Validation (Ticket #3)
- [ ] Test 3.1: Source == Target
- [ ] Test 3.2: Target Inside Source
- [ ] Test 3.3: Low Disk Space Warning
- [ ] Test 3.4: No Write Permission

### Race Conditions (Ticket #4)
- [ ] Test 4.1: File Deleted Mid-Operation
- [ ] Test 4.2: File Modified During Operation
- [ ] Test 4.3: Folder Creation Fails

### Logging (Ticket #5)
- [ ] Test 5.1: Log File Created
- [ ] Test 5.2: Log Contents
- [ ] Test 5.3: Multiple Sessions

### Pre-flight (Ticket #6)
- [ ] Test 6.1: All Validation Gates
- [ ] Test 6.2: Validation Order

### Documentation (Ticket #7)
- [ ] Test 7.1: Docstring Coverage
- [ ] Test 7.2: Code Comments

### Integration
- [ ] INT-1: Full Happy Path
- [ ] INT-2: Full Failure Path
- [ ] INT-3: Partial Success Path

### Stress Tests
- [ ] Stress 1: Large File Count
- [ ] Stress 2: Deep Directory Structure
- [ ] Stress 3: Rapid Operations

---

## 🎯 ACCEPTANCE CRITERIA

**For PASS verdict on each ticket:**

### Ticket #1: PASS if
- ✅ All system directories blocked
- ✅ Symlinks resolved and validated
- ✅ User directories allowed
- ✅ Clear error messages

### Ticket #2: PASS if
- ✅ No bare `except:` statements
- ✅ All exceptions specific
- ✅ Critical failures show user dialogs
- ✅ Ctrl+C still works

### Ticket #3: PASS if
- ✅ Source == Target rejected
- ✅ Target inside Source rejected
- ✅ Disk space checked
- ✅ Permissions validated

### Ticket #4: PASS if
- ✅ File disappearance handled
- ✅ Success/failure counts accurate
- ✅ No crashes on race conditions
- ✅ All failures logged

### Ticket #5: PASS if
- ✅ Log file created
- ✅ All operations logged
- ✅ Timestamped entries
- ✅ Multiple sessions supported

### Ticket #6: PASS if
- ✅ All validations run before operations
- ✅ Fast failure (< 1 second)
- ✅ Clear error messages
- ✅ No partial operations

### Ticket #7: PASS if
- ✅ Key functions documented
- ✅ Docstrings include examples
- ✅ Exception handlers commented
- ✅ IDE shows helpful tooltips

---

## 📝 REPORT FORMAT

Please provide results in this format:

```
=================================================================
VALIDATION REPORT - File Organizer Tickets #1-7
=================================================================
Date: [DATE]
Validator: [NAME]
Environment: [OS, Python Version]

TICKET #1: Path Traversal Vulnerability
Status: [PASS/FAIL]
Tests Passed: X/4
Issues Found: [List any issues]
Notes: [Any observations]

TICKET #2: Silent Exception Swallowing
Status: [PASS/FAIL]
Tests Passed: X/4
Issues Found: [List any issues]
Notes: [Any observations]

[...continue for all tickets...]

OVERALL VERDICT: [PASS/FAIL/CONDITIONAL PASS]
Recommendation: [Ship / Fix Issues / Major Rework Needed]

Blocker Issues: [List any showstoppers]
Minor Issues: [List any non-critical issues]
Suggestions: [Any improvements]
```

---

## 🚀 READY FOR VALIDATION

All code changes are committed and ready for testing.

**Good luck, Validator!**
