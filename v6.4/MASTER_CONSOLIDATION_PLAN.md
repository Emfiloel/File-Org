# MASTER CONSOLIDATION PLAN v6.4
## Complete Code Refactor + Intelligent Pattern Scanner

**Date:** November 8, 2025
**Goal:** Fix ALL duplication + Create unified intelligent pattern system
**Approach:** Aggressive consolidation for maximum maintainability

---

## 🎯 OBJECTIVES

### **1. Fix Basic Duplication** (Original 4 issues)
- ✅ Validation code (60 lines → 20 lines)
- ✅ Extract functions (146 lines → 80 lines)
- ✅ Messagebox patterns (consistency)
- ✅ Result displays (60 lines → 25 lines)

### **2. Consolidate Pattern Detection** (NEW - User Request)
- ✅ Merge Smart Pattern + Smart Pattern+ + Sequential Pattern
- ✅ Create ONE intelligent pattern scanner
- ✅ Learning capability (remembers user choices)
- ✅ Auto-detection with confidence scoring
- ✅ Preview before organizing

### **3. Reduce Function Bloat**
- ✅ by_detected() + by_detected_or_prompt() + by_sequential() → Unified
- ✅ analyze_filename_patterns() → Enhanced with learning
- ✅ Pattern scanner → Core organization method

---

## 📊 PATTERN DETECTION DUPLICATION ANALYSIS

### **Current State: 3 Separate Pattern Systems**

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM #1: Smart Pattern Detection                         │
│ Function: detect_folder_name() (lines 851-874)             │
│ Logic: Delimiter-based (-, _), capitalization rules        │
│ Handles: vacation-001 → Vacation, My_File → My File        │
│ Used by: "Smart Pattern" button                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SYSTEM #2: Smart Pattern+ (with user prompts)              │
│ Function: by_detected_or_prompt() (lines 1604-1620)        │
│ Logic: detect_folder_name() + user prompt for unknowns     │
│ Handles: Same as #1 + asks user for unrecognized patterns  │
│ Used by: "Smart Pattern+" button                           │
│ Saves: User choices to folder_mappings.json                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SYSTEM #3: Sequential Pattern Detection                    │
│ Function: detect_sequential_pattern() (lines 880-926)      │
│ Logic: Detects numbered sequences (file001, IMG_1234)      │
│ Handles: vacation-001 → Vacation, IMG_1234 → IMG           │
│ Used by: "Sequential Pattern" button                       │
└─────────────────────────────────────────────────────────────┘
```

### **Problem: Redundancy + User Confusion**

**Redundancy:**
- `detect_folder_name()` and `detect_sequential_pattern()` handle SIMILAR patterns
- vacation-001 → Both can detect this!
- IMG_1234 → Both can detect this!
- Code overlap: ~40%

**User Confusion:**
- "Which button should I click?"
- "What's the difference between Smart Pattern and Smart Pattern+?"
- "Should I try Sequential first or Smart?"

**Maintenance Burden:**
- Bug in pattern detection → Fix in 3 places
- New pattern type → Add to all 3 systems
- Testing → Test all 3 modes

---

## 🚀 SOLUTION: UNIFIED INTELLIGENT PATTERN SCANNER

### **New System Architecture:**

```
┌───────────────────────────────────────────────────────────────┐
│ INTELLIGENT PATTERN SCANNER (IPS)                            │
│ One system to rule them all                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Pattern Detection Engine                                │ │
│ │ ├─ Sequential patterns (file001, IMG_1234)             │ │
│ │ ├─ Delimiter patterns (My-File, vacation_photos)       │ │
│ │ ├─ Camera tags (IMG, DSC, DSCN)                        │ │
│ │ ├─ Date patterns (20240101, 2024-01-01)                │ │
│ │ └─ Custom learned patterns (user-defined)              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Confidence Scoring                                      │ │
│ │ ├─ High (90%+): Auto-organize                          │ │
│ │ ├─ Medium (50-89%): Show preview, ask confirm          │ │
│ │ └─ Low (<50%): Ask user, save choice                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Learning System                                         │ │
│ │ ├─ Remembers user corrections                          │ │
│ │ ├─ Builds pattern library                              │ │
│ │ ├─ Improves over time                                   │ │
│ │ └─ Exports/imports patterns                             │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Preview System                                          │ │
│ │ ├─ Shows detected patterns with confidence             │ │
│ │ ├─ Groups by pattern type                              │ │
│ │ ├─ Allows manual override before organizing            │ │
│ │ └─ Statistics: Files per folder, coverage %            │ │
│ └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### **Key Features:**

**1. All-in-One Detection:**
```python
def detect_pattern(filename: str) -> Tuple[Optional[str], float, str]:
    """
    Unified pattern detection with confidence scoring.

    Returns:
        (folder_name, confidence_score, detection_method)

    Example:
        detect_pattern("vacation-001.jpg")
        → ("Vacation", 0.95, "sequential")

        detect_pattern("My-Photo-Gallery.jpg")
        → ("My-Photo-Gallery", 0.85, "delimiter")

        detect_pattern("unknown_file_xyz.txt")
        → (None, 0.0, "no_match")
    """
    # Try all detection methods in priority order
    # Return best match with confidence score
```

**2. Learning System:**
```python
class PatternLearner:
    """Learns from user corrections and improves over time"""

    def __init__(self):
        self.learned_patterns = load_learned_patterns()
        # Format: {
        #   "pattern_signature": {
        #       "folder": "Vacation",
        #       "confidence": 0.95,
        #       "uses": 15,
        #       "last_used": "2025-11-08"
        #   }
        # }

    def learn(self, filename: str, user_chosen_folder: str):
        """Learn from user's choice"""
        signature = self.extract_signature(filename)
        self.learned_patterns[signature] = {
            'folder': user_chosen_folder,
            'confidence': 0.99,  # User choice = high confidence
            'uses': self.learned_patterns.get(signature, {}).get('uses', 0) + 1,
            'last_used': datetime.now().isoformat()
        }
        self.save()

    def predict(self, filename: str) -> Tuple[Optional[str], float]:
        """Predict folder based on learned patterns"""
        signature = self.extract_signature(filename)
        if signature in self.learned_patterns:
            pattern = self.learned_patterns[signature]
            return pattern['folder'], pattern['confidence']
        return None, 0.0

    def extract_signature(self, filename: str) -> str:
        """Extract pattern signature from filename"""
        # vacation-001.jpg → "PREFIX-NNN"
        # My_Photo_Album.jpg → "WORD_WORD_WORD"
        # IMG_1234.jpg → "IMG_NNNN"
```

**3. Intelligent Preview:**
```python
def preview_intelligent_patterns(source_dirs: List[str]) -> dict:
    """
    Analyze files and show intelligent preview.

    Returns dict with:
    - detected_patterns: {pattern_name: {files: [...], confidence: 0.9}}
    - unrecognized: [list of files needing user input]
    - statistics: {total_files, coverage_percent, avg_confidence}
    """
```

---

## 📋 IMPLEMENTATION PLAN

### **PHASE 1: Core Helpers** (2 hours)

**1.1 Messages Class**
```python
class Messages:
    """Centralized user messaging"""

    # Common messages
    NO_SOURCE = "Please select at least one source directory."
    NO_TARGET = "Please select a target directory first."

    @staticmethod
    def error(msg: str, title: str = "Error"):
        messagebox.showerror(title, msg)

    @staticmethod
    def info(msg: str, title: str = "Info"):
        messagebox.showinfo(title, msg)

    @staticmethod
    def warning(msg: str, title: str = "Warning"):
        messagebox.showwarning(title, msg)

    @staticmethod
    def confirm(msg: str, title: str = "Confirm") -> bool:
        return messagebox.askyesno(title, msg)
```

**1.2 Validation Helpers**
```python
def validate_sources(show_errors: bool = True) -> Tuple[bool, List[str]]:
    """Validate source directories"""
    source_dirs = get_source_dirs()

    if not source_dirs:
        if show_errors:
            Messages.error(Messages.NO_SOURCE)
        return False, []

    for src in source_dirs:
        is_safe, reason = is_safe_directory(src)
        if not is_safe:
            if show_errors:
                Messages.error(reason, "Unsafe Directory")
            return False, []

    return True, source_dirs

def validate_target(target_dir: str, show_errors: bool = True) -> bool:
    """Validate target directory"""
    if not target_dir:
        if show_errors:
            Messages.error(Messages.NO_TARGET)
        return False

    if not os.path.exists(target_dir):
        if show_errors:
            Messages.error(f"Target directory does not exist:\n{target_dir}")
        return False

    is_safe, reason = is_safe_directory(target_dir)
    if not is_safe:
        if show_errors:
            Messages.error(reason, "Unsafe Directory")
        return False

    return True
```

**1.3 Operation Result Builder**
```python
class OperationResult:
    """Build and display operation results"""

    def __init__(self, operation_name: str):
        self.operation = operation_name
        self.stats = {}

    def add(self, label: str, value: int, condition: bool = True):
        """Add statistic if condition is true"""
        if condition:
            self.stats[label] = value
        return self

    def build(self) -> str:
        """Build message string"""
        msg = f"✓ {self.operation} Complete!\n\n"
        for label, value in self.stats.items():
            msg += f"{label}: {value}\n"
        return msg

    def show(self, title: str = None):
        """Show result dialog"""
        Messages.info(self.build(), title or f"{self.operation} Complete")
```

---

### **PHASE 2: Extract Consolidation** (1 hour)

**2.1 Unified Extract Function**
```python
def extract_files(levels: Optional[int] = None):
    """
    Unified file extraction.

    Args:
        levels: None = extract to parent, int = extract N levels up
    """
    is_valid, source_dirs = validate_sources()
    if not is_valid:
        return

    operation_name = "Extract All to Parent" if levels is None else f"Extract Up {levels} Levels"
    LOGGER.start_operation(operation_name, source_dirs, source_dirs[0])

    # File collection
    plan = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for f in files:
                src = os.path.join(dirpath, f)

                # Calculate destination
                if levels is None:
                    # Extract to parent
                    if os.path.abspath(dirpath) == os.path.abspath(source):
                        continue
                    dst_folder = source
                else:
                    # Extract N levels up
                    dst_folder = dirpath
                    for _ in range(levels):
                        parent = os.path.dirname(dst_folder)
                        if parent == dst_folder:
                            break
                        dst_folder = parent

                if os.path.abspath(src) != os.path.join(dst_folder, f):
                    plan.append((src, dst_folder, f))

    if not plan:
        Messages.info("No files found to extract.")
        LOGGER.end_operation()
        return

    # Execute moves
    progress_bar["maximum"] = len(plan)
    succeeded = failed = 0

    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        if move_file(src, dst_folder, fname):
            succeeded += 1
        else:
            failed += 1
        update_progress(i, len(plan))

    # Cleanup empty folders
    removed = 0
    for source in source_dirs:
        for dpath, _, _ in os.walk(source, topdown=False):
            if os.path.abspath(dpath) != os.path.abspath(source) and not os.listdir(dpath):
                try:
                    os.rmdir(dpath)
                    removed += 1
                except (OSError, PermissionError):
                    pass

    LOGGER.end_operation()

    # Show results
    OperationResult(operation_name)
        .add("Files moved", succeeded)
        .add("Files failed", failed, condition=failed > 0)
        .add("Empty folders removed", removed)
        .show()

# Wrappers
def extract_all_to_parent():
    extract_files(levels=None)

def extract_up_levels():
    try:
        levels_str = simpledialog.askstring("Extract Up", "How many levels up? (1-10):", initialvalue="1")
        if not levels_str:
            return
        levels = int(levels_str)
        if levels < 1 or levels > 10:
            raise ValueError("Levels must be between 1 and 10")
    except ValueError as e:
        Messages.error(str(e), "Invalid Input")
        return
    extract_files(levels=levels)
```

---

### **PHASE 3: Intelligent Pattern Scanner** (3 hours) 🌟

**3.1 Unified Pattern Detector**
```python
class IntelligentPatternDetector:
    """Unified pattern detection with learning"""

    def __init__(self):
        self.learner = PatternLearner()

    def detect(self, filename: str) -> Tuple[Optional[str], float, str]:
        """
        Detect pattern with confidence scoring.

        Returns:
            (folder_name, confidence, method)

        Detection order (stops at first high-confidence match):
        1. Learned patterns (confidence 0.99)
        2. Camera tags (IMG, DSC - confidence 0.95)
        3. Sequential patterns (file001 - confidence 0.90)
        4. Delimiter patterns (My-File - confidence 0.80)
        5. No match (None, 0.0, "unknown")
        """
        # 1. Check learned patterns first
        learned_folder, learned_conf = self.learner.predict(filename)
        if learned_conf > 0.9:
            return learned_folder, learned_conf, "learned"

        # 2. Camera tags (high confidence)
        camera_tag = extract_img_tag(filename)
        if camera_tag:
            return camera_tag, 0.95, "camera"

        # 3. Sequential pattern (high confidence)
        seq_folder = detect_sequential_pattern(filename)
        if seq_folder:
            return seq_folder, 0.90, "sequential"

        # 4. Delimiter pattern (medium confidence)
        delim_folder = detect_folder_name(filename)
        if delim_folder:
            return delim_folder, 0.80, "delimiter"

        # 5. No match
        return None, 0.0, "unknown"

    def batch_analyze(self, files: List[str]) -> dict:
        """
        Analyze multiple files and group by detected pattern.

        Returns:
            {
                "Vacation": {
                    "files": ["vacation-001.jpg", ...],
                    "confidence": 0.90,
                    "method": "sequential",
                    "count": 25
                },
                ...
                "__UNKNOWN__": {
                    "files": ["weird_file.txt", ...],
                    "count": 5
                }
            }
        """
        patterns = {}

        for filename in files:
            folder, conf, method = self.detect(filename)

            if folder is None:
                folder = "__UNKNOWN__"
                method = "needs_input"

            if folder not in patterns:
                patterns[folder] = {
                    'files': [],
                    'confidence': conf,
                    'method': method,
                    'count': 0
                }

            patterns[folder]['files'].append(filename)
            patterns[folder]['count'] += 1

        return patterns
```

**3.2 Pattern Learner**
```python
class PatternLearner:
    """Machine learning for file patterns"""

    def __init__(self):
        self.pattern_file = DATA_DIR.get_path("learned_patterns.json")
        self.patterns = self._load()

    def _load(self) -> dict:
        """Load learned patterns from file"""
        if self.pattern_file.exists():
            try:
                with open(self.pattern_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        """Save learned patterns to file"""
        with open(self.pattern_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)

    def extract_signature(self, filename: str) -> str:
        """
        Extract pattern signature from filename.

        Examples:
            vacation-001.jpg → "TEXT-NNN"
            My_Photo_Album.jpg → "TEXT_TEXT_TEXT"
            IMG_1234.jpg → "IMG_NNNN"
            2024-01-15.pdf → "NNNN-NN-NN"
        """
        base = os.path.splitext(filename)[0]

        # Replace numbers with N, letters with T
        signature = ""
        for char in base:
            if char.isdigit():
                if not signature or signature[-1] != 'N':
                    signature += 'N'
            elif char.isalpha():
                if not signature or signature[-1] != 'T':
                    signature += 'T'
            else:
                signature += char

        return signature

    def learn(self, filename: str, folder: str):
        """Learn from user's choice"""
        sig = self.extract_signature(filename)

        if sig not in self.patterns:
            self.patterns[sig] = {
                'folder': folder,
                'examples': [],
                'uses': 0,
                'confidence': 0.99
            }

        self.patterns[sig]['uses'] += 1
        if filename not in self.patterns[sig]['examples']:
            self.patterns[sig]['examples'].append(filename)
            # Keep only last 5 examples
            self.patterns[sig]['examples'] = self.patterns[sig]['examples'][-5:]

        self._save()

    def predict(self, filename: str) -> Tuple[Optional[str], float]:
        """Predict folder from learned patterns"""
        sig = self.extract_signature(filename)

        if sig in self.patterns:
            pattern = self.patterns[sig]
            return pattern['folder'], pattern['confidence']

        return None, 0.0

    def get_statistics(self) -> dict:
        """Get learning statistics"""
        return {
            'total_patterns': len(self.patterns),
            'total_uses': sum(p['uses'] for p in self.patterns.values()),
            'most_used': max(self.patterns.items(), key=lambda x: x[1]['uses'])[0] if self.patterns else None
        }
```

**3.3 Intelligent Organization Mode**
```python
def organize_intelligent():
    """
    Intelligent pattern-based organization with preview and learning.

    Workflow:
    1. Scan all files
    2. Detect patterns with confidence scoring
    3. Show preview with detected patterns
    4. Ask user for unrecognized files
    5. Learn user's choices
    6. Organize files
    """
    is_valid, source_dirs = validate_sources()
    if not is_valid:
        return

    target_dir = (target_entry.get() or "").strip()
    if not validate_target(target_dir):
        return

    # Step 1: Collect all files
    all_files = []
    for source in source_dirs:
        for dirpath, dirnames, files in os.walk(source):
            dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]
            all_files.extend(files)

    if not all_files:
        Messages.info("No files found to organize.")
        return

    # Step 2: Analyze patterns
    detector = IntelligentPatternDetector()
    patterns = detector.batch_analyze(all_files)

    # Step 3: Show preview
    preview_text = "Intelligent Pattern Detection Results:\n\n"

    high_conf = {k: v for k, v in patterns.items() if v.get('confidence', 0) >= 0.8 and k != "__UNKNOWN__"}
    low_conf = {k: v for k, v in patterns.items() if v.get('confidence', 0) < 0.8 and k != "__UNKNOWN__"}
    unknown = patterns.get("__UNKNOWN__", {}).get('files', [])

    if high_conf:
        preview_text += "✓ HIGH CONFIDENCE (will auto-organize):\n"
        for folder, info in sorted(high_conf.items(), key=lambda x: -x[1]['count']):
            preview_text += f"  {folder}/ → {info['count']} files ({info['method']}, {info['confidence']*100:.0f}%)\n"
        preview_text += "\n"

    if low_conf:
        preview_text += "⚠ MEDIUM CONFIDENCE (please review):\n"
        for folder, info in sorted(low_conf.items(), key=lambda x: -x[1]['count']):
            preview_text += f"  {folder}/ → {info['count']} files ({info['method']}, {info['confidence']*100:.0f}%)\n"
        preview_text += "\n"

    if unknown:
        preview_text += f"❓ UNRECOGNIZED ({len(unknown)} files):\n"
        for file in unknown[:5]:
            preview_text += f"  {file}\n"
        if len(unknown) > 5:
            preview_text += f"  ... and {len(unknown)-5} more\n"
        preview_text += "\nYou will be asked to classify these.\n\n"

    preview_text += f"\nTotal: {len(all_files)} files\n"
    preview_text += f"Coverage: {((len(all_files) - len(unknown)) / len(all_files) * 100):.1f}%\n"

    # Ask to proceed
    if not Messages.confirm(preview_text + "\nProceed with organization?", "Intelligent Pattern Detection"):
        return

    # Step 4: Handle unknown files (learning)
    if unknown:
        for file in unknown:
            answer = simpledialog.askstring(
                "Unrecognized File",
                f"Where should this file go?\n\n{file}\n\nEnter folder name (or leave blank to skip):"
            )
            if answer and answer.strip():
                folder = answer.strip()
                detector.learner.learn(file, folder)
                # Update patterns
                if folder not in patterns:
                    patterns[folder] = {'files': [], 'confidence': 0.99, 'method': 'learned', 'count': 0}
                patterns[folder]['files'].append(file)
                patterns[folder]['count'] += 1

    # Step 5: Organize using detected patterns
    def intelligent_logic(filename: str) -> Optional[str]:
        folder, _, _ = detector.detect(filename)
        return folder

    # Use existing run_organizer with intelligent logic
    run_organizer(intelligent_logic, preview=False, operation_name="Intelligent Pattern Organization")
```

---

### **PHASE 4: Update GUI** (1 hour)

**4.1 Replace 3 Buttons with 1**

**Before:**
```python
sections = {
    "Organize": [
        ("By Extension", lambda: run_organizer(by_extension)),
        ("Alphabetize", lambda: run_organizer(by_alphabet)),
        ("Smart Pattern", lambda: run_organizer(by_detected)),      # ← Remove
        ("Smart Pattern+", lambda: run_organizer(by_detected_or_prompt)),  # ← Remove
        ("Sequential Pattern", lambda: run_organizer(by_sequential)),  # ← Remove
        ("IMG/DSC", lambda: run_organizer(by_img_dsc)),
    ]
}
```

**After:**
```python
sections = {
    "Organize": [
        ("By Extension", lambda: run_organizer(by_extension)),
        ("Alphabetize", lambda: run_organizer(by_alphabet)),
        ("🧠 Intelligent Pattern", organize_intelligent),  # ← ONE BUTTON!
        ("IMG/DSC", lambda: run_organizer(by_img_dsc)),
    ]
}
```

---

## 📊 IMPACT SUMMARY

### **Before Consolidation:**
```
Total lines: 2,558
Functions: 78
Pattern detection systems: 3 (separate)
Duplicate code: ~290 lines
User buttons for patterns: 3
  - "Smart Pattern"
  - "Smart Pattern+"
  - "Sequential Pattern"
```

### **After Consolidation:**
```
Total lines: ~2,100 (-458 lines, -18%)
Functions: ~65 (-13 functions)
Pattern detection systems: 1 (unified)
Duplicate code: ~50 lines (-82%)
User buttons for patterns: 1
  - "🧠 Intelligent Pattern" (does everything)
```

### **Feature Improvements:**
```
✅ Learns from user corrections
✅ Improves over time
✅ Confidence scoring
✅ Intelligent preview
✅ Exportable pattern library
✅ Less user confusion (one button!)
✅ Better accuracy (combines all detection methods)
```

---

## 🎯 ACCEPTANCE CRITERIA

**v6.4 consolidation complete when:**

- [ ] Messages class created and all 34 messagebox calls use it
- [ ] validate_sources() and validate_target() created
- [ ] All 6 validation duplicates replaced with helper calls
- [ ] extract_files() unified function created
- [ ] extract_all_to_parent() and extract_up_levels() are thin wrappers
- [ ] OperationResult class created
- [ ] All 5 result displays use OperationResult
- [ ] IntelligentPatternDetector class created
- [ ] PatternLearner class created with JSON persistence
- [ ] organize_intelligent() function created
- [ ] GUI updated: 3 pattern buttons → 1 intelligent button
- [ ] All tests pass
- [ ] New tests added for intelligent pattern detection
- [ ] Pattern learning saves/loads correctly
- [ ] Code reduced to ~2,100 lines

---

**Ready to implement!** 🚀

This will transform the codebase from "working" to "professional-grade intelligent system".
