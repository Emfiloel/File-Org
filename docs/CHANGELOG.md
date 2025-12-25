# Changelog

All notable changes to File Organizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.3.0] - 2025-11-02

### Added
- ✨ **Auto-Create A-Z + 0-9 Folders**: One-click creation of alphabetical folder structures
  - Configurable options (A-Z, 0-9, special characters)
  - Uppercase/lowercase toggle
  - Skips existing folders gracefully
  - Shows creation summary
- ✨ **Custom Pattern Search & Collect**: User-specified pattern search with wildcards
  - Search across all source directories recursively
  - Preview matches before moving
  - Wildcard support via fnmatch
  - Automatic folder name sanitization
  - Collision handling
- ✨ **Tabbed Interface**: Organized GUI into 3 logical tabs
  - 📂 Organize: All organization modes
  - 🔧 Tools: Utility functions (Extract, Folder Tools, Pattern Search)
  - ⚙️ Advanced: Pattern Scanner, Statistics, History & Undo
  - Scrollable tabs with mouse wheel support
- ✨ **Recent Directories Dropdown**: Quick access to recent paths
  - Remembers last 10 source and target directories
  - Persists across sessions in config.json
  - Deduplication (no repeated entries)
  - Auto-populated on startup

### Changed
- Source/Target entry widgets replaced with Combobox dropdowns
- Footer label now uses VERSION constant dynamically
- Help text updated with v6.3 features

### Tests
- Added 2 new tests (total: 17 tests)
- All backward compatibility tests passing
- 100% test pass rate maintained

### Documentation
- V6.3_DELIVERY.md - Complete delivery documentation
- ARCHITECT_REVIEW.md - Architectural review and approval
- BUILD_INSTRUCTIONS.md - Build instructions for standalone executable
- Multiple guides for new features

---

## [6.2.0] - 2025-11-01

### Added
- ✨ **In-Place Organization Mode**: Organize files within the same parent directory
  - Toggle via checkbox in GUI
  - Creates subfolders in source directory
  - Useful for organizing without separate target
- ✨ **Skip Folders with # Prefix**: Mark folders to skip during scanning
  - Folders starting with # are automatically skipped
  - Prevents organizing already-organized folders
  - Configurable in config.json

### Changed
- Updated validation process to catch documentation inaccuracies
- Improved error handling for edge cases

### Tests
- Added tests for in-place organization
- Added tests for skip folder functionality
- Total: 15 tests passing

### Documentation
- V6.2_FEATURE_SPEC.md - Feature specification
- MENTOR_FEATURE_REQUESTS_v6.3.md - Feature requests for next version

---

## [6.1.0] - 2025-11-01

### Added
- ✨ **Undo Progress Window**: Real-time progress feedback during undo operations
  - Shows "Restoring 1/150, 2/150..." with progress bar
  - Improves user experience during long undo operations
- ✨ **Comprehensive Unit Tests**: 30+ tests across 7 test classes
  - TestVersionConstant
  - TestPathSecurity
  - TestPatternDetection
  - TestDuplicateDetection
  - TestOperationLogging
  - TestExtractFunctions
  - TestGUIComponents
- ✨ **Type Hints**: Comprehensive type annotations throughout codebase
  - Improved IDE support
  - Better code documentation
  - Easier maintenance

### Changed
- Enhanced code quality with type checking
- Improved maintainability with better documentation

### Tests
- 30+ comprehensive unit tests
- 100% pass rate
- Coverage across all major features

### Documentation
- VERSION_6.1_DELIVERY.md - Delivery document
- V6.1_FIX_REPORT.md - Bug fixes and improvements
- test_file_organizer.py - Comprehensive test suite

---

## [6.0.0] - 2025-10-31

### Added - Major Production Release

**All 7 Architectural Blockers Addressed:**

1. ✅ **Transaction Logging & Undo**
   - OperationLogger class with complete operation tracking
   - JSONL-based operation log (.file_organizer_data/operations.jsonl)
   - Full undo capability in Tools menu
   - Timestamped operations with statistics

2. ✅ **Memory Efficiency**
   - Generator pattern (collect_files_generator)
   - No memory bombs (all_files=[])
   - Handles 100,000+ files efficiently
   - Stream processing architecture

3. ✅ **TOCTOU Protection**
   - Atomic file operations
   - Double-check pattern (verify → move → verify)
   - Graceful handling of race conditions
   - FileExistsError handling with auto-rename

4. ✅ **Path Traversal Security**
   - is_safe_directory() function
   - Blocks system directories (Windows/macOS/Linux)
   - Symlink resolution
   - OS-specific forbidden directory lists

5. ✅ **GUI Threading**
   - Worker thread for file operations
   - Main thread for GUI responsiveness
   - Queue-based progress monitoring
   - Cancellable operations with Cancel button

6. ✅ **Silent Failure Prevention**
   - Comprehensive logging to operations.jsonl
   - No bare except statements
   - Detailed error messages
   - User-visible error reporting

7. ✅ **Undo Functionality**
   - Complete operation reversal
   - File-by-file restoration
   - Original path preservation
   - Operation history view

### Security Features
- Windows reserved name sanitization (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- Path validation and normalization
- Safe directory checks
- Atomic operations

### Organization Modes
- By Extension (.jpg, .pdf, .txt, etc.)
- Alphabetize (A-Z, 0-9, special)
- IMG/DSC Detection (camera files)
- Smart Pattern Detection (delimiter-based)
- Sequential Pattern Detection (numbered files)
- Extract All to Parent (flatten)
- Extract Up N Levels (reduce nesting)

### GUI Features
- Modern, clean interface
- Comprehensive help menu
- Preview before organize
- Real-time progress updates
- Pattern tester tool
- Statistics dashboard

### Documentation
- VERSION_6_COMPLETE.md - Complete implementation guide
- VALIDATOR_HANDOVER_V6.md - Validation workflow
- VALIDATOR_FAQ.md - Common questions
- SAME_FOLDER_EXPLANATION.md - Technical explanations

---

## [5.0.0] - 2025-10-30

### Added
- Initial production edition
- Advanced architecture
- Multiple organization modes
- Basic GUI

### Issues
- Missing: Path traversal protection
- Missing: GUI threading
- Missing: Extract functions
- Missing: Comprehensive undo

### Notes
- Foundation for v6.0 improvements
- Identified architectural gaps

---

## [4.0.0] and earlier

Historical versions archived in `archive/legacy/`

### Evolution
- v1.0: Basic file organizer with CLI
- v2.0: Added GUI with tkinter
- v3.0: Pattern detection added
- v4.0: Multiple organization modes

---

## Unreleased

### Planned for v6.4 - Consolidation
- [ ] Modular architecture refactor
- [ ] Increase test coverage to 50%
- [ ] CI/CD with GitHub Actions
- [ ] Automated release process
- [ ] Performance benchmarking suite

### Planned for v7.0 - Innovation
- [ ] Plugin architecture
- [ ] ML-based pattern learning
- [ ] Cloud storage integration (Dropbox, Google Drive, OneDrive)
- [ ] Web interface
- [ ] Multi-language support
- [ ] Metadata-based organization (EXIF, ID3 tags)

---

## Version Naming Convention

- **Major version** (x.0.0): Significant architectural changes or breaking changes
- **Minor version** (6.x.0): New features, no breaking changes
- **Patch version** (6.3.x): Bug fixes, documentation updates

---

**Legend:**
- ✨ New feature
- 🐛 Bug fix
- 🔒 Security fix
- 📝 Documentation
- ⚡ Performance improvement
- 🔧 Maintenance
- ✅ Tests added

---

*This changelog is maintained as part of the File Organizer project.*

*Last updated: November 2025*
