# DUPLICATION MAP - WHERE THE DUPLICATES ARE

**File:** `v6.4/file_organizer.py` (2,558 lines)
**Purpose:** Visual map showing EXACTLY where duplicate code exists

---

## 📍 FILE STRUCTURE OVERVIEW

```
file_organizer.py (2,558 lines)
│
├── IMPORTS & CONSTANTS (Lines 1-61)
│   └── Line 61: VERSION = "v6.4 Consolidation"
│
├── DATA MANAGEMENT (Lines 72-431)
│   ├── DataDirectory class (75-94)
│   ├── Config class (99-175)
│   ├── OperationLogger class (178-331) ← Has undo functionality
│   └── DuplicateDetector class (333-431)
│
├── UTILITY FUNCTIONS (Lines 434-929)
│   ├── Line 434: cancel_operation()
│   ├── Line 491: browse_source() ← Source directory selection
│   ├── Line 504: browse_target() ← Target directory selection
│   ├── Line 534: load_recent_directories() ← v6.3 feature
│   ├── Line 549: add_to_recent()
│   ├── Line 580: get_source_dirs() ⭐ USED 6 TIMES
│   ├── Line 583: should_skip_folder()
│   ├── Line 602: is_safe_directory() ⭐ VALIDATION - USED 13 TIMES
│   ├── Line 679: report_error()
│   ├── Line 687: get_file_size()
│   ├── Line 694: move_file() ← Core file moving
│   ├── Line 751: update_progress()
│   ├── Line 766: show_preview()
│   ├── Line 791: smart_title()
│   ├── Line 796: load_mappings()
│   ├── Line 804: save_mappings()
│   ├── Line 810: make_key()
│   ├── Line 820: sanitize_folder_name() ← Windows reserved names
│   └── Line 931: validate_operation() ← Validation helper
│
├── PATTERN DETECTION (Lines 851-1070)
│   ├── Line 851: detect_folder_name() ← Main pattern detection
│   ├── Line 876: extract_img_tag() ← IMG/DSC detection
│   └── Line 880: detect_sequential_pattern() ← Sequential detection
│
├── CORE OPERATION (Lines 1073-1205)
│   └── Line 1073: run_organizer() ⭐ MAIN ORGANIZER
│       └── Has validation duplication (lines 1076-1083)
│
├── EXTRACT FUNCTIONS (Lines 1208-1355) ⭐ 80% DUPLICATE
│   ├── Line 1208: extract_all_to_parent()
│   │   ├── 1210-1220: ⚠️ VALIDATION DUPLICATE #1
│   │   ├── 1223: Logger setup
│   │   ├── 1225-1234: File collection loop
│   │   ├── 1241: Progress bar setup
│   │   ├── 1245-1250: Move loop
│   │   ├── 1253-1261: Empty folder cleanup
│   │   └── 1266-1271: ⚠️ RESULT DISPLAY DUPLICATE
│   │
│   └── Line 1273: extract_up_levels()
│       ├── 1276-1284: User input for levels
│       ├── 1287-1296: ⚠️ VALIDATION DUPLICATE #2
│       ├── 1302: Logger setup (SAME as 1223)
│       ├── 1304-1320: File collection loop (90% same)
│       ├── 1322: Progress bar setup (SAME as 1241)
│       ├── 1326-1331: Move loop (SAME as 1245-1250)
│       ├── 1334-1342: Empty folder cleanup (SAME as 1253-1261)
│       └── 1347-1352: ⚠️ RESULT DISPLAY DUPLICATE
│
├── V6.3 NEW FEATURES (Lines 1357-1570)
│   ├── Line 1357: create_alphanumeric_folders()
│   │   ├── 1366-1370: ⚠️ ERROR MESSAGE DUPLICATE
│   │   └── 1417-1428: ⚠️ RESULT DISPLAY DUPLICATE
│   │
│   └── Line 1431: search_and_collect()
│       ├── 1436-1444: ⚠️ VALIDATION DUPLICATE #3
│       └── 1560-1569: ⚠️ RESULT DISPLAY DUPLICATE
│
├── ORGANIZATION MODES (Lines 1574-1624)
│   ├── Line 1574: by_extension()
│   ├── Line 1579: by_alphabet()
│   ├── Line 1585: by_numeric_simple()
│   ├── Line 1598: by_img_dsc() ← Thin wrapper (OK)
│   ├── Line 1601: by_detected() ← Thin wrapper (OK)
│   ├── Line 1604: by_detected_or_prompt()
│   └── Line 1622: by_sequential() ← Thin wrapper (OK)
│
├── PATTERN SCANNER (Lines 1629-1889)
│   └── Line 1629: analyze_filename_patterns()
│       └── Line 1826-1833: ⚠️ VALIDATION DUPLICATE #4
│
├── GUI FUNCTIONS (Lines 1891-2557)
│   ├── Line 1891: organize_by_patterns()
│   │   └── Line 1901-1908: ⚠️ VALIDATION DUPLICATE #5
│   │
│   ├── Line 1920: scan_patterns()
│   │   └── Line 1826-1833: ⚠️ VALIDATION DUPLICATE #6
│   │
│   └── Line 2000+: GUI setup (tabs, widgets, etc.)
│
└── END (Line 2558)
```

---

## 🎯 DUPLICATION #1: VALIDATION CODE (6 LOCATIONS)

### **Pattern Found:**
```python
source_dirs = get_source_dirs()
if not source_dirs:
    messagebox.showerror("Error", "Please select at least one source directory.")
    return

for src in source_dirs:
    is_safe, reason = is_safe_directory(src)
    if not is_safe:
        messagebox.showerror("Unsafe Directory", reason)
        return
```

### **Location Map:**

```
┌─────────────────────────────────────────────────────────────┐
│ Location #1: run_organizer()                                │
│ Lines: 1076-1083                                            │
│ Function starts: Line 1073                                  │
│ Context: Main organization function                         │
├─────────────────────────────────────────────────────────────┤
│ Location #2: extract_all_to_parent()                        │
│ Lines: 1210-1220                                            │
│ Function starts: Line 1208                                  │
│ Context: Extract files to parent folder                     │
├─────────────────────────────────────────────────────────────┤
│ Location #3: extract_up_levels()                            │
│ Lines: 1287-1296                                            │
│ Function starts: Line 1273                                  │
│ Context: Extract files N levels up                          │
├─────────────────────────────────────────────────────────────┤
│ Location #4: search_and_collect()                           │
│ Lines: 1436-1444                                            │
│ Function starts: Line 1431                                  │
│ Context: v6.3 pattern search feature                        │
├─────────────────────────────────────────────────────────────┤
│ Location #5: scan_patterns() [nested in GUI function]       │
│ Lines: 1826-1833                                            │
│ Context: Pattern scanner tool                               │
├─────────────────────────────────────────────────────────────┤
│ Location #6: organize_by_patterns() [nested in GUI]         │
│ Lines: 1901-1908                                            │
│ Context: Pattern-based organization                         │
└─────────────────────────────────────────────────────────────┘

TOTAL: ~10 lines × 6 locations = ~60 lines of duplicate code
```

### **What Will Change:**
- **Create:** New helper function `validate_sources()` around line 930
- **Update:** All 6 functions above will call the helper instead
- **Result:** 60 lines → ~20 lines (saves 40 lines)

---

## 🎯 DUPLICATION #2: EXTRACT FUNCTIONS (2 FUNCTIONS, 80% OVERLAP)

### **Side-by-Side Comparison:**

```
extract_all_to_parent()           extract_up_levels()
Lines: 1208-1272 (64 lines)      Lines: 1273-1355 (82 lines)
═══════════════════════════════════════════════════════════════

1210: source_dirs = get_source   1287: source_dirs = get_source
1211: if not source_dirs:        1288: if not source_dirs:
1212:     error message           1289:     error message (SAME)

1215: for src in source_dirs:    1292: for src in source_dirs:
1216:     is_safe check           1293:     is_safe check (SAME)

1223: LOGGER.start_operation()   1302: LOGGER.start_operation() (SAME)

1225: plan = []                  1304: plan = [] (SAME)
1226: for source in sources:     1305: for source in sources: (SAME)
1227:     for dirpath...:         1306:     for dirpath...: (SAME)

       [File collection logic]          [File collection logic]
       (slightly different)             (slightly different)

1241: progress_bar["maximum"]    1322: progress_bar["maximum"] (SAME)
1242: succeeded = 0              1323: succeeded = 0 (SAME)
1243: failed = 0                 1324: failed = 0 (SAME)

1245: for i, (src, dst...) in:   1326: for i, (src, dst...) in: (SAME)
1246:     if move_file():         1327:     if move_file(): (SAME)
1247:         succeeded += 1      1328:         succeeded += 1 (SAME)
1248:     else:                   1329:     else: (SAME)
1249:         failed += 1         1330:         failed += 1 (SAME)
1250:     update_progress()       1331:     update_progress() (SAME)

1253: removed = 0                1334: removed = 0 (SAME)
1254: for source in sources:     1335: for source in sources: (SAME)
       [cleanup empty folders]          [cleanup empty folders] (SAME)

1263: LOGGER.end_operation()     1344: LOGGER.end_operation() (SAME)

1266: msg = "✓ Extract..."       1347: msg = "✓ Extract..." (SAME FORMAT)
1271: messagebox.showinfo()      1352: messagebox.showinfo() (SAME)
```

### **What Will Change:**
- **Create:** New unified function `extract_files(levels=None)` around line 1208
- **Update:** Both functions will become thin wrappers calling `extract_files()`
- **Result:** 146 lines → ~80 lines (saves 66 lines)

---

## 🎯 DUPLICATION #3: MESSAGEBOX CALLS (34 LOCATIONS)

### **Error Messages:**

```
Line 764:  messagebox.showinfo("Operation Complete", ...)
Line 1083: messagebox.showerror("Validation Error", ...)
Line 1180: messagebox.showinfo("Complete", ...)
Line 1188: messagebox.showinfo("Cancelled", ...)
Line 1195: messagebox.showerror("Error", ...)
Line 1212: messagebox.showerror("Error", "Please select...")  ⭐ DUPLICATE
Line 1219: messagebox.showerror("Unsafe Directory", ...)
Line 1237: messagebox.showinfo("Extract", "No files found...")
Line 1271: messagebox.showinfo("Extract Complete", ...)
Line 1284: messagebox.showerror("Invalid Input", ...)
Line 1289: messagebox.showerror("Error", "Please select...")  ⭐ DUPLICATE
Line 1296: messagebox.showerror("Unsafe Directory", ...)  ⭐ DUPLICATE
Line 1316: messagebox.showinfo("Extract Up", "No files found...")
Line 1352: messagebox.showinfo("Extract Up Complete", ...)
Line 1366: messagebox.showerror("Error", "Please select...")  ⭐ DUPLICATE
Line 1370: messagebox.showerror("Error", "Target does not exist...")
Line 1380: messagebox.showwarning("No Selection", ...)
Line 1428: messagebox.showinfo("Folder Creation Complete", ...)
Line 1438: messagebox.showerror("Error", "Please select...")  ⭐ DUPLICATE
Line 1443: messagebox.showwarning("No Pattern", ...)
... (14 more)

TOTAL: 34 messagebox calls
```

### **Common Patterns:**

```
Pattern A (repeated 5 times):
messagebox.showerror("Error", "Please select at least one source directory.")
Found at: 1212, 1289, 1438, + 2 more

Pattern B (repeated 3 times):
messagebox.showerror("Unsafe Directory", reason)
Found at: 1219, 1296, + 1 more

Pattern C (repeated 8 times):
msg = f"✓ {operation} Complete!\n\nFiles moved: {succeeded}\n"
messagebox.showinfo("Complete", msg)
Found at: 764, 1180, 1271, 1352, 1428, + 3 more
```

### **What Will Change:**
- **Create:** New `Messages` class around line 680
- **Update:** All 34 messagebox calls will use the class
- **Result:** More consistent messaging, easier to maintain

---

## 🎯 DUPLICATION #4: RESULT DISPLAY (5 LOCATIONS)

### **Pattern Found:**
```python
msg = f"✓ {operation_name} Complete!\n\n"
msg += f"Files moved: {succeeded}\n"
if failed > 0:
    msg += f"Files failed: {failed}\n"
if extra_stat:
    msg += f"{extra_label}: {extra_value}\n"
messagebox.showinfo("Complete", msg)
```

### **Location Map:**

```
┌─────────────────────────────────────────────────────────────┐
│ Location #1: run_organizer()                                │
│ Lines: 1177-1180                                            │
│ Shows: Files moved, files failed                            │
├─────────────────────────────────────────────────────────────┤
│ Location #2: extract_all_to_parent()                        │
│ Lines: 1266-1271                                            │
│ Shows: Files moved, files failed, folders removed           │
├─────────────────────────────────────────────────────────────┤
│ Location #3: extract_up_levels()                            │
│ Lines: 1347-1352                                            │
│ Shows: Files moved, files failed, folders removed           │
├─────────────────────────────────────────────────────────────┤
│ Location #4: create_alphanumeric_folders()                  │
│ Lines: 1417-1428                                            │
│ Shows: Created, already existed, failed                     │
├─────────────────────────────────────────────────────────────┤
│ Location #5: search_and_collect()                           │
│ Lines: 1560-1569                                            │
│ Shows: Files moved, duplicates skipped                      │
└─────────────────────────────────────────────────────────────┘

TOTAL: ~12 lines × 5 locations = ~60 lines of similar code
```

### **What Will Change:**
- **Create:** New `OperationResult` class around line 770
- **Update:** All 5 functions will use the result builder
- **Result:** ~60 lines → ~25 lines (saves 35 lines)

---

## 📊 CONSOLIDATION IMPACT MAP

### **Before Consolidation:**
```
file_organizer.py (2,558 lines)
│
├── Lines 1-930:   Utilities & Classes
│                  └── is_safe_directory() used everywhere
│
├── Lines 931-1070: validate_operation() (exists but not used everywhere)
│
├── Lines 1073-1205: run_organizer()
│                    └── Has validation duplication
│
├── Lines 1208-1355: EXTRACT FUNCTIONS (80% duplicate) ⭐
│                    ├── extract_all_to_parent() (64 lines)
│                    └── extract_up_levels() (82 lines)
│
├── Lines 1357-1570: v6.3 features
│                    └── Has validation duplication
│
└── Lines 1574-2558: Rest of code
                     └── 34 scattered messagebox calls ⭐
```

### **After Consolidation:**
```
file_organizer.py (~2,300 lines)
│
├── Lines 1-930:   Utilities & Classes
│                  ├── is_safe_directory()
│                  ├── NEW: Messages class ⭐
│                  ├── NEW: validate_sources() ⭐
│                  └── NEW: OperationResult class ⭐
│
├── Lines 931-1070: validate_operation()
│
├── Lines 1073-1150: run_organizer() (cleaned up)
│
├── Lines 1151-1235: EXTRACT FUNCTIONS (consolidated) ⭐
│                    ├── extract_files(levels=None) (70 lines)
│                    ├── extract_all_to_parent() (wrapper, 3 lines)
│                    └── extract_up_levels() (wrapper, 8 lines)
│
├── Lines 1236-1400: v6.3 features (cleaned up)
│
└── Lines 1401-2300: Rest of code (cleaned up)
                     └── All using Messages class ⭐
```

---

## 🎯 WHAT GETS CREATED (NEW CODE)

### **New Helper #1: validate_sources()**
**Location:** Will be added around line 930 (after validate_operation)
**Size:** ~15 lines
**Used by:** 6 functions

### **New Helper #2: Messages class**
**Location:** Will be added around line 680 (after report_error)
**Size:** ~30 lines
**Used by:** 34 locations

### **New Helper #3: OperationResult class**
**Location:** Will be added around line 770 (after show_preview)
**Size:** ~25 lines
**Used by:** 5 functions

### **New Helper #4: extract_files()**
**Location:** Will replace extract_all_to_parent at line 1208
**Size:** ~70 lines
**Replaces:** 2 functions totaling 146 lines

---

## 🔍 WHAT GETS MODIFIED (EXISTING CODE)

### **Modified Functions (Will call new helpers):**

```
Function                    Lines      What Changes
══════════════════════════════════════════════════════════════
run_organizer()            1073-1205  Use validate_sources()
extract_all_to_parent()    1208-1272  Becomes 3-line wrapper
extract_up_levels()        1273-1355  Becomes 8-line wrapper
create_alphanumeric_folders() 1357-1429  Use Messages class
search_and_collect()       1431-1570  Use validate_sources()
                                      Use Messages class
organize_by_patterns()     1891+      Use validate_sources()
scan_patterns()            1920+      Use validate_sources()
```

### **Modified Lines (Messagebox calls):**
- 34 lines will change from `messagebox.xxx()` to `Messages.xxx()`

---

## 📍 EXACT LINE NUMBERS FOR CHANGES

### **Phase 1: Messages Class** (Day 1)

**Will modify these EXACT lines:**
```
764:  messagebox.showinfo       → Messages.info
1083: messagebox.showerror      → Messages.error
1180: messagebox.showinfo       → Messages.info
1188: messagebox.showinfo       → Messages.info
1195: messagebox.showerror      → Messages.error
1212: messagebox.showerror      → Messages.error(Messages.NO_SOURCE)
1219: messagebox.showerror      → Messages.error
1237: messagebox.showinfo       → Messages.info
1271: messagebox.showinfo       → Messages.info
... (25 more lines)
```

### **Phase 2: Validation Helper** (Day 2)

**Will replace these EXACT line ranges:**
```
Lines 1076-1083  → validate_sources() call (3 lines)
Lines 1210-1220  → validate_sources() call (3 lines)
Lines 1287-1296  → validate_sources() call (3 lines)
Lines 1436-1444  → validate_sources() call (3 lines)
Lines 1826-1833  → validate_sources() call (3 lines)
Lines 1901-1908  → validate_sources() call (3 lines)
```

### **Phase 3: Extract Consolidation** (Day 3)

**Will completely rewrite:**
```
Lines 1208-1272  → extract_all_to_parent() becomes 3 lines
Lines 1273-1355  → extract_up_levels() becomes 8 lines
NEW: Lines 1208-1278 → extract_files() unified function (70 lines)
```

---

## ✅ SUMMARY

**Duplicate code is in these RANGES:**

| Issue | Line Ranges | Functions Affected |
|-------|-------------|-------------------|
| **Validation** | 1076-1083, 1210-1220, 1287-1296, 1436-1444, 1826-1833, 1901-1908 | 6 functions |
| **Extract twins** | 1208-1272, 1273-1355 | 2 functions |
| **Messageboxes** | 34 scattered lines throughout file | All functions |
| **Results** | 1177-1180, 1266-1271, 1347-1352, 1417-1428, 1560-1569 | 5 functions |

**After consolidation, these ranges will be SMALLER and call shared helpers.**

---

Ready to see the consolidation happen? I can start with Phase 1 (Messages class) which is the safest and easiest!