# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a **File Organizer** tool - a Python-based GUI application for organizing large collections of files using various pattern detection strategies. The project has evolved through multiple versions, with the current production version (`master_file_5.py`) being the most feature-complete.

## Key Files

- **master_file_5.py**: Production-ready version with full features (recommended)
- **master_file_unified.py**: Consolidated version combining best features from earlier iterations
- **Previous/**: Legacy versions for reference

## Architecture

### Core Components

1. **Data Management Layer**
   - `DataDirectory`: Centralized storage in `.file_organizer_data/` directory
   - `Config`: JSON-based configuration system with dot-notation access
   - `OperationLogger`: JSONL-based operation logging for undo functionality
   - `DuplicateDetector`: SQLite-based hash storage for duplicate detection

2. **Pattern Detection Engine**
   - Multiple detection strategies (sequential, prefix, delimiter, camera tags, dates, numeric ranges)
   - Smart pattern detection with user mapping persistence
   - Automatic pattern scanner that analyzes millions of files efficiently

3. **File Organization Engine**
   - Generator-based file collection for memory efficiency
   - Batch processing in configurable chunks (default: 10,000 files)
   - Pre-flight validation before operations
   - Duplicate detection (hash-based or size-based)

4. **GUI Layer**
   - Tkinter-based interface with optional drag-and-drop (tkinterdnd2)
   - Scrollable action sections for multiple organization modes
   - Real-time preview and progress tracking
   - Statistics and history windows

### Pattern Detection Strategies

The tool supports 7+ pattern detection strategies:

1. **Sequential Pattern** (NEW in v5): Detects `base-001`, `file_123`, `031204-0022` → `Base/`, `File/`, `031204/`
2. **Extension-based**: Groups by file type (`.jpg` → `JPG/`)
3. **Alphabetic**: First character grouping (`A-Z`, `0-9`, special chars)
4. **Smart Pattern**: Detects delimiter patterns with capitalization rules
5. **IMG/DSC Detection**: Camera file patterns (IMG, DSC, DSCN, etc.)
6. **Name-Set-File Family**: Strict pattern matching for `NAME-SET-FILENUMBER` formats
7. **Numeric Bucketing**: Intelligent grouping of numeric files into ranges (0-999, 1000-1999)

### Memory Efficiency

The codebase is designed to handle millions of files:
- Generator-based file traversal (`collect_files_generator`)
- Chunked processing to avoid loading entire file lists into memory
- Progress updates at configurable intervals
- SQLite for persistent duplicate tracking

### Data Directory Structure

```
.file_organizer_data/
├── config.json              # User configuration
├── operations.jsonl         # Operation log (one JSON per line)
├── duplicates.db            # SQLite hash database
├── folder_mappings.json     # Smart Pattern+ user choices
└── statistics.json          # Usage analytics
```

## Development Workflow

### Running the Application

```bash
# Run the production version
python master_file_5.py

# Run the unified version
python master_file_unified.py
```

### Dependencies

Required:
- Python 3.7+
- tkinter (usually bundled with Python)

Optional:
- tkinterdnd2 (for drag-and-drop functionality)

### Configuration

Configuration is stored in `.file_organizer_data/config.json`. Key settings:

```json
{
  "max_files_per_folder": 500,
  "skip_folders": ["Sort", ".git", "node_modules", "__pycache__"],
  "duplicate_detection": {
    "method": "hash",  // or "size_only"
    "hash_algorithm": "md5",
    "chunk_size": 8192
  },
  "performance": {
    "batch_size": 10000,
    "progress_update_interval": 1000,
    "use_generators": true
  }
}
```

## Important Implementation Details

### Pattern Detection Logic

When adding or modifying pattern detection:

1. **Detection functions** should return `Optional[str]` (folder name or None)
2. **Naming conventions**:
   - Underscores → `Smart_Title` format
   - Hyphens → `Capitalized-Words` format
   - Mixed delimiters are preserved as markers (e.g., `[-]`, `[_]`)
3. **Duplicate markers** like `(2)`, `(3)` are stripped before pattern analysis
4. **Sequential pattern** requires minimum 2 trailing digits to avoid false positives

### File Collection Flow

```python
collect_files_generator(source_dirs, logic_func)
  → walks directories (skipping configured folders)
  → applies pattern detection logic_func
  → checks for duplicates (hash or size-based)
  → yields (src_path, dest_folder, filename)
```

### Operation Logging & Undo

- Every operation creates an entry with timestamp, moved files, and statistics
- Undo works by reversing moves in reverse order from the operation log
- Maximum 10 undo operations kept (configurable via `safety.max_undo_operations`)

### Duplicate Detection

Two modes available:
1. **Hash-based** (recommended): MD5 hash comparison, 100% accuracy
   - Same name + same hash → `DUPES/` folder
   - Same name + different hash → `DUPE SIZE/` folder
2. **Size-only**: Faster but less accurate

### Pre-flight Validation

Before any operation, the system validates:
- Source directories exist and are readable
- Target directory exists and is writable
- Target is not inside source (prevents recursion)
- Sufficient disk space available (warns if < 1GB)

## Version Evolution

- **v2**: Basic organization modes
- **v3**: Added advanced UI, pattern tester
- **v4**: Added numeric bucketing, extract functions
- **v5** (Production): Added centralized data directory, operation logging, undo, hash-based duplicates, pattern scanner, sequential pattern detection

## Common Patterns for Development

### Adding a New Organization Mode

1. Create detection function in "LOGIC FUNCTIONS" section:
   ```python
   def by_custom(filename: str) -> Optional[str]:
       # Return folder name or None
       return folder_name
   ```

2. Add to `sections` dictionary:
   ```python
   "Custom Mode": [
       ("Custom", lambda: run_organizer(by_custom, operation_name="Custom")),
       ("Preview", lambda: run_organizer(by_custom, preview=True)),
   ]
   ```

### Adding Pattern Type to Scanner

Add pattern detection in `analyze_filename_patterns()` function following the existing pattern structure:

```python
# Pattern N: Custom Pattern
m_custom = re.match(r'your_pattern', base)
if m_custom:
    pattern_key = f"CUSTOM:{value}"
    if pattern_key not in patterns:
        patterns[pattern_key] = {
            'type': 'custom',
            'name': value,
            'files': [],
            'folder_name': value
        }
    patterns[pattern_key]['files'].append(filename)
    continue
```

## Testing Patterns

Use the built-in Pattern Tester tool (available in GUI) to test filename patterns without moving files. It supports testing:
- Single mode with sample filenames
- All modes at once for comparison
- Real-time result preview

## Safety Considerations

- Always use **Preview** before running organization operations
- The tool automatically handles file collisions by appending `(2)`, `(3)`, etc.
- Operations are logged and can be undone
- Skip folders are configurable to avoid organizing system directories
- Same-source-as-target operations are safe (files won't move to themselves)
