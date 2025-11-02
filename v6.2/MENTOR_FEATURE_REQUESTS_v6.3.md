# FILE ORGANIZER v6.3 - FEATURE REQUESTS FOR MENTOR

**Date:** November 2, 2025
**Prepared By:** User + Claude Code
**Status:** 📋 READY FOR IMPLEMENTATION
**Priority:** HIGH - User-Requested Features

---

## 🎯 CONFIRMED USER REQUIREMENTS (MUST HAVE)

### ✅ FEATURE #1: Auto-Create A-Z, 0-9 Folder Structure
**Priority:** P0 (Must Have)
**User Request:** "create a set parent folders alpha numeric"

**What it does:**
- One-click button: "📁 Create A-Z + 0-9 Folders"
- Creates all 37 folders instantly:
  - A through Z (26 folders)
  - 0-9 (10 folders)
  - !@#$ (1 special character folder)
- Skips folders that already exist
- Shows summary: "Created 25 folders, 12 already existed"

**Where to place:**
- New section in GUI: "Quick Setup" or "Folder Tools"
- Button text: "📁 Create Alphabetic Structure"

**Implementation details:**
```python
def create_alphanumeric_folders(target_dir):
    """Create A-Z, 0-9, and special char folders"""
    folders = []

    # A-Z
    folders.extend([chr(i) for i in range(ord('A'), ord('Z')+1)])

    # 0-9
    folders.extend([str(i) for i in range(10)])

    # Special
    folders.append("!@#$")

    created = 0
    existing = 0

    for folder in folders:
        path = os.path.join(target_dir, folder)
        if os.path.exists(path):
            existing += 1
        else:
            os.makedirs(path)
            created += 1

    return created, existing
```

**User workflow:**
1. Select target folder (e.g., `D:\Photos\`)
2. Click "Create Alphabetic Structure"
3. All folders created
4. Run "Alphabetize" mode
5. Files distributed into A-Z folders

**UI Mockup:**
```
┌─────────────────────────────────────┐
│ FOLDER TOOLS                        │
├─────────────────────────────────────┤
│ [📁 Create A-Z + 0-9 Folders]       │
│                                     │
│ Options:                            │
│ ☑ Include A-Z (26 folders)         │
│ ☑ Include 0-9 (10 folders)         │
│ ☑ Include !@#$ (1 folder)          │
│ ○ Uppercase  ● Lowercase           │
└─────────────────────────────────────┘
```

---

### ✅ FEATURE #2: Custom Pattern Search & Move
**Priority:** P0 (Must Have)
**User Request:** "search button where i can input the specific pattern myself"

**What it does:**
- Search tab with input field
- User types pattern (e.g., "vacation")
- Searches ALL files in source folders/subfolders
- Shows preview: "Found 127 files matching 'vacation'"
- Creates folder named after pattern
- Moves all matches to that folder
- One operation, solves scattered files problem

**UI Location:**
- New "Search" tab in tabbed interface
- Or separate section: "Pattern Search & Collect"

**Features:**
- Case-insensitive search
- Regex support (optional)
- Preview before moving
- Undo-able operation
- Progress bar for large searches

**Implementation details:**
```python
def search_and_collect(source_dirs, pattern, target_parent, case_sensitive=False):
    """
    Search for pattern in all files and collect them

    Args:
        source_dirs: List of directories to search
        pattern: Search pattern (string or regex)
        target_parent: Where to create collection folder
        case_sensitive: Match case or not

    Returns:
        (matches_found, files_moved, folder_created)
    """
    matches = []

    # Search phase
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for filename in files:
                if case_sensitive:
                    if pattern in filename:
                        matches.append(os.path.join(dirpath, filename))
                else:
                    if pattern.lower() in filename.lower():
                        matches.append(os.path.join(dirpath, filename))

    # Create target folder
    target_folder = os.path.join(target_parent, sanitize_folder_name(pattern))
    os.makedirs(target_folder, exist_ok=True)

    # Move phase
    moved = 0
    for file_path in matches:
        filename = os.path.basename(file_path)
        if move_file(file_path, target_folder, filename):
            moved += 1

    return len(matches), moved, target_folder
```

**UI Mockup:**
```
┌─────────────────────────────────────────────┐
│ PATTERN SEARCH & COLLECT                    │
├─────────────────────────────────────────────┤
│ Search Pattern: [vacation____________]      │
│                 [🔍 Search]  [📦 Collect]   │
│                                             │
│ Options:                                    │
│ ☐ Case sensitive                           │
│ ☐ Use regex pattern                        │
│ ☐ Search in subfolders ✓                   │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ SEARCH RESULTS                      │   │
│ │                                     │   │
│ │ Found 127 files matching 'vacation' │   │
│ │                                     │   │
│ │ Sample matches:                     │   │
│ │ • vacation-2024-001.jpg             │   │
│ │ • summer_vacation.png               │   │
│ │ • vacation_photos_final.jpg         │   │
│ │ • my_vacation_video.mp4             │   │
│ │ ... and 123 more                    │   │
│ │                                     │   │
│ │ [📦 Collect to 'Vacation' folder]  │   │
│ └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**User workflow:**
1. Go to "Search" tab
2. Type "vacation" in search box
3. Click "Search" → shows preview
4. Review matches
5. Click "Collect" → creates `Vacation/` folder
6. All 127 files moved to `Vacation/`
7. Operation logged for undo

---

## 🎨 ADDITIONAL GUI IMPROVEMENTS (HIGHLY RECOMMENDED)

### 💡 FEATURE #3: Tabbed Interface
**Priority:** P1 (Should Have)
**Why:** Cleaner UI, room for growth, modern UX

**Proposed Tabs:**

```
┌─────────────────────────────────────────────────┐
│ [Organize] [Search] [Tools] [Stats] [Settings] │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Tab content here]                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Tab 1: Organize** (current main UI)
- Source/Target selection
- Organization modes
- Preview/Organize buttons

**Tab 2: Search** (NEW - Feature #2)
- Pattern search & collect
- Advanced search options

**Tab 3: Tools**
- Create A-Z folders (Feature #1)
- Batch folder creation
- Extract functions
- Undo/History

**Tab 4: Stats**
- Operation history
- Statistics dashboard
- Charts and summaries

**Tab 5: Settings**
- Configuration UI (instead of editing JSON)
- Theme selection
- Performance settings

**Implementation:**
```python
# Use ttk.Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Tab 1: Organize
organize_frame = ttk.Frame(notebook)
notebook.add(organize_frame, text="📂 Organize")

# Tab 2: Search
search_frame = ttk.Frame(notebook)
notebook.add(search_frame, text="🔍 Search")

# Tab 3: Tools
tools_frame = ttk.Frame(notebook)
notebook.add(tools_frame, text="🔧 Tools")

# etc.
```

---

### 💡 FEATURE #4: Recent Directories Dropdown
**Priority:** P1 (Should Have)
**Why:** Save time, improve UX

**What it does:**
- Dropdown replaces text entry for source/target
- Shows last 10 used directories
- User can select from dropdown OR type new path
- Persists across sessions

**UI Change:**
```
Before:
┌──────────────────────────────────┐
│ Source: [C:\Photos\_________]    │
└──────────────────────────────────┘

After:
┌──────────────────────────────────┐
│ Source: [▼ C:\Photos\______]     │
│         │ C:\Photos              │
│         │ D:\Downloads           │
│         │ E:\Archive             │
│         └─────────────────       │
└──────────────────────────────────┘
```

**Implementation:**
```python
# Use ttk.Combobox instead of Entry
recent_sources = load_recent_directories("sources")  # From config
source_combo = ttk.Combobox(frame, values=recent_sources)
source_combo.set(recent_sources[0] if recent_sources else "")

# Save on each use
def save_recent_directory(path, key="sources"):
    recents = load_recent_directories(key)
    if path in recents:
        recents.remove(path)
    recents.insert(0, path)
    recents = recents[:10]  # Keep last 10
    save_to_config(f"recent_{key}", recents)
```

---

### 💡 FEATURE #5: Preset Workflows
**Priority:** P2 (Nice to Have)
**Why:** Automate common multi-step processes

**What it does:**
- Save common organization sequences
- One-click replay
- Example presets:
  1. "Initial Sort" → Create A-Z folders → Alphabetize
  2. "Photo Organization" → By Extension → IMG files by date
  3. "Cleanup" → Extract to parent → Remove empty folders

**UI:**
```
┌──────────────────────────────────┐
│ WORKFLOW PRESETS                 │
├──────────────────────────────────┤
│ [▶ Initial Sort (A-Z)]           │
│ [▶ Photo Cleanup]                │
│ [▶ Video Organization]           │
│                                  │
│ [+ Create New Preset]            │
└──────────────────────────────────┘
```

---

### 💡 FEATURE #6: Batch Folder Creation from List
**Priority:** P2 (Nice to Have)
**Why:** Flexible alternative to Feature #1

**What it does:**
- Text area to paste folder names (one per line)
- Creates all folders at once
- Useful for project-specific structures

**Example:**
```
Input:
Design
Development
Marketing
Sales
Support

Creates:
D:\Project\Design\
D:\Project\Development\
D:\Project\Marketing\
D:\Project\Sales\
D:\Project\Support\
```

---

### 💡 FEATURE #7: Keyboard Shortcuts
**Priority:** P2 (Nice to Have)
**Why:** Power user efficiency

**Suggested shortcuts:**
- `Ctrl+P` - Preview
- `Ctrl+Enter` - Organize
- `Ctrl+Z` - Undo (in Tools tab)
- `Ctrl+,` - Settings
- `Ctrl+Tab` - Switch tabs
- `Ctrl+1/2/3/4/5` - Jump to specific tab

---

### 💡 FEATURE #8: Enhanced Preview Window
**Priority:** P2 (Nice to Have)
**Why:** Better understand what will happen

**What it shows:**
```
┌──────────────────────────────────────────┐
│ PREVIEW: By Extension                    │
├──────────────────────────────────────────┤
│ Source: C:\Downloads (1,247 files)       │
│                                          │
│ Will create:                             │
│   JPG/     (523 files)                   │
│   PNG/     (201 files)                   │
│   PDF/     (189 files)                   │
│   MP4/     (87 files)                    │
│   TXT/     (143 files)                   │
│   _NOEXT/  (104 files)                   │
│                                          │
│ Estimated time: ~30 seconds              │
│ Disk space needed: 15.2 GB               │
│                                          │
│ [✓ Looks good - Organize]  [Cancel]     │
└──────────────────────────────────────────┘
```

---

### 💡 FEATURE #9: Dark Mode / Theme Support
**Priority:** P3 (Low Priority)
**Why:** User preference, modern UX

**Themes:**
- Light (default)
- Dark
- High contrast
- Custom (user-defined colors)

---

### 💡 FEATURE #10: Configuration GUI
**Priority:** P2 (Nice to Have)
**Why:** No manual JSON editing

**Settings to expose:**
- Max files per folder
- Skip folders list (editable)
- Duplicate detection method
- Performance settings (batch size)
- UI theme
- Auto-backup config

---

## 📊 PRIORITY ROADMAP

### v6.3 - Core Features (Target: 4-5 days)
**MUST HAVE:**
1. ✅ Feature #1: Auto-Create A-Z Folders
2. ✅ Feature #2: Custom Pattern Search
3. ✅ Feature #3: Tabbed Interface
4. ✅ Feature #4: Recent Directories

**Why these 4:**
- Features #1 & #2 are user-requested (critical)
- Feature #3 prepares UI for future growth
- Feature #4 is quick win with high impact

### v6.4 - Enhanced UX (Target: 2-3 days)
**SHOULD HAVE:**
5. Feature #5: Preset Workflows
6. Feature #7: Keyboard Shortcuts
8. Feature #8: Enhanced Preview

### v6.5 - Nice to Have (Target: 2-3 days)
**COULD HAVE:**
6. Feature #6: Batch Folder Creation
10. Feature #10: Configuration GUI
9. Feature #9: Dark Mode

### v7.0 - Advanced Features (Future)
- Metadata-based organization (EXIF dates)
- Batch rename functionality
- File preview with thumbnails
- Cloud integration
- Scheduled auto-organization
- Plugin system

---

## 🎯 IMPLEMENTATION CHECKLIST FOR MENTOR

### Phase 1: Planning (1 day)
- [ ] Review all feature requests
- [ ] Design tabbed UI layout
- [ ] Design database schema for recent dirs
- [ ] Create UI mockups
- [ ] Estimate effort for each feature

### Phase 2: Feature #1 - Auto-Create Folders (0.5 days)
- [ ] Implement `create_alphanumeric_folders()` function
- [ ] Add "Folder Tools" section to GUI
- [ ] Add button with icon
- [ ] Add options checkboxes (uppercase/lowercase, etc.)
- [ ] Show creation summary dialog
- [ ] Write 3 unit tests
- [ ] Update help text

### Phase 3: Feature #2 - Pattern Search (1 day)
- [ ] Implement `search_and_collect()` function
- [ ] Create Search tab UI
- [ ] Add pattern input field
- [ ] Add search button with progress bar
- [ ] Add results preview area
- [ ] Add collect button
- [ ] Add case-sensitive checkbox
- [ ] Add regex support checkbox
- [ ] Write 5 unit tests
- [ ] Update help text

### Phase 4: Feature #3 - Tabbed Interface (1 day)
- [ ] Refactor main UI to use ttk.Notebook
- [ ] Create 5 tab frames (Organize, Search, Tools, Stats, Settings)
- [ ] Move existing UI to "Organize" tab
- [ ] Move search UI to "Search" tab
- [ ] Move undo/history to "Tools" tab
- [ ] Move statistics to "Stats" tab
- [ ] Create basic settings UI in "Settings" tab
- [ ] Test tab switching
- [ ] Update help text

### Phase 5: Feature #4 - Recent Directories (0.5 days)
- [ ] Replace Entry widgets with Combobox
- [ ] Implement `load_recent_directories()` function
- [ ] Implement `save_recent_directory()` function
- [ ] Store in config.json (recent_sources, recent_targets)
- [ ] Limit to 10 most recent
- [ ] Test persistence across sessions
- [ ] Write 2 unit tests

### Phase 6: Testing & Integration (1 day)
- [ ] Run all existing tests (ensure no regressions)
- [ ] Run all new tests (15+ new tests)
- [ ] Manual testing of each feature
- [ ] Test tab switching and UI responsiveness
- [ ] Test with large datasets
- [ ] Fix any bugs found
- [ ] Update VERSION to "v6.3"

### Phase 7: Documentation (0.5 days)
- [ ] Update help text for all new features
- [ ] Create V6.3_DELIVERY.md
- [ ] Update README with new features
- [ ] Create user guide with screenshots
- [ ] Document keyboard shortcuts

---

## 🧪 TEST REQUIREMENTS

### New Tests Needed (15+ tests)

**Feature #1 Tests (3):**
```python
def test_create_alphanumeric_folders_all()
def test_create_alphanumeric_folders_uppercase()
def test_create_alphanumeric_folders_skip_existing()
```

**Feature #2 Tests (5):**
```python
def test_search_pattern_case_insensitive()
def test_search_pattern_case_sensitive()
def test_search_pattern_regex()
def test_collect_files_to_folder()
def test_search_with_no_matches()
```

**Feature #3 Tests (2):**
```python
def test_tab_switching()
def test_all_tabs_render()
```

**Feature #4 Tests (3):**
```python
def test_recent_directories_save()
def test_recent_directories_load()
def test_recent_directories_limit_10()
```

**Integration Tests (2):**
```python
def test_full_workflow_create_and_organize()
def test_search_collect_and_undo()
```

---

## 📋 ACCEPTANCE CRITERIA

v6.3 is complete when:

### Feature #1 (Auto-Create Folders):
- [ ] Button creates all 37 folders (A-Z, 0-9, !@#$)
- [ ] Options work (uppercase/lowercase, include/exclude)
- [ ] Skips existing folders
- [ ] Shows creation summary
- [ ] All tests pass

### Feature #2 (Pattern Search):
- [ ] Search finds all matching files in source + subfolders
- [ ] Preview shows count and samples
- [ ] Collect creates folder and moves files
- [ ] Case-sensitive toggle works
- [ ] Regex support works
- [ ] Operation is undo-able
- [ ] All tests pass

### Feature #3 (Tabbed Interface):
- [ ] All 5 tabs render correctly
- [ ] Tab switching works smoothly
- [ ] All existing features still work
- [ ] No UI regressions

### Feature #4 (Recent Directories):
- [ ] Dropdowns show last 10 used paths
- [ ] Selection populates field
- [ ] Typing custom path still works
- [ ] Persists across sessions
- [ ] All tests pass

### General:
- [ ] All v6.2 tests still pass (no regressions)
- [ ] All new tests pass
- [ ] Syntax valid
- [ ] Help text updated
- [ ] Documentation complete

---

## 💡 ADDITIONAL IDEAS FOR FUTURE (v7.0+)

### Advanced Organization:
1. **Metadata-based Organization**
   - EXIF date for photos → Year/Month/ folders
   - MP3 tags for music → Artist/Album/
   - Document properties for Office files

2. **Smart Suggestions**
   - AI analyzes files
   - Suggests organization structure
   - "I see 1000 photos spanning 2020-2024, suggest Year/Month folders?"

3. **Batch Rename**
   - Rename files in sequence
   - Add prefix/suffix
   - Replace text
   - Use metadata in names

### File Preview:
4. **Thumbnail View**
   - Show image previews in preview window
   - Video thumbnails
   - PDF first page preview

5. **Quick View**
   - Select file → press Space → preview pops up
   - Like macOS Quick Look

### Automation:
6. **Watched Folders**
   - Auto-organize new files in watched folder
   - Run in background
   - Configurable rules

7. **Scheduled Organization**
   - Run organization at scheduled times
   - Daily cleanup of Downloads folder
   - Weekly photo organization

### Collaboration:
8. **Cloud Integration**
   - Organize Google Drive folders
   - Organize Dropbox
   - Remote file access

9. **Shared Presets**
   - Import/export workflow presets
   - Share with team
   - Community preset library

### Extensibility:
10. **Plugin System**
    - Custom organization modes via plugins
    - Python API for extensions
    - Community plugins

11. **Web Interface**
    - Access via browser
    - Remote organization
    - Mobile-friendly UI

12. **CLI Mode**
    - Command-line interface
    - Scriptable operations
    - Batch processing via scripts

---

## 🎯 RECOMMENDED NEXT STEPS

**For Mentor:**

1. **Review this document** (15 min)
   - Understand all feature requests
   - Note any questions/concerns

2. **Create v6.3 branch** (2 min)
   ```bash
   git checkout -b feature/v6.3-enhancements
   ```

3. **Start with Feature #1** (easiest, quick win)
   - Implement `create_alphanumeric_folders()`
   - Add button to UI
   - Test thoroughly

4. **Continue with roadmap**
   - Feature #2 (pattern search)
   - Feature #3 (tabs)
   - Feature #4 (recent dirs)

5. **Test everything** (1 day)
   - All new tests
   - All old tests (regression check)
   - Manual testing

6. **Document and deliver** (0.5 days)
   - V6.3_DELIVERY.md
   - Updated help text
   - Screenshots

**Total estimated time: 4-5 days for v6.3**

---

## 📞 QUESTIONS FOR CLARIFICATION

**Before starting, Mentor should clarify:**

1. **Feature #1:** Should folders be uppercase (A-Z) or allow user choice?
2. **Feature #2:** Should regex be on by default or opt-in?
3. **Feature #3:** Preferred tab order? (Current: Organize, Search, Tools, Stats, Settings)
4. **Feature #4:** Should recent dirs be global or per-operation-type?
5. **Testing:** What's the minimum test coverage requirement?

---

## ✅ HANDOVER CHECKLIST

**User has confirmed:**
- [x] Feature #1 (Auto-create A-Z folders) - YES, must have
- [x] Feature #2 (Pattern search) - YES, must have
- [x] Additional GUI improvements - Welcomed, Architect provided ideas

**Mentor should have:**
- [x] This requirements document
- [x] Access to v6.2 codebase
- [x] Understanding of current architecture
- [x] Test suite (test_v6_2.py as reference)

**Ready to begin:** ✅ YES

---

**Status:** 📋 READY FOR MENTOR IMPLEMENTATION

**Priority:** HIGH - User-requested features

**Estimated completion:** 4-5 days for v6.3 core features

---

**End of Feature Request Document**
