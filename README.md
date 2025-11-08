# File Organizer v6.3

> **Professional-grade file organization tool with intelligent pattern detection, GUI interface, and complete undo capability.**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen.svg)](tests/)

---

## 🎯 What is File Organizer?

File Organizer is a desktop application that automatically organizes your files into logical folder structures based on various criteria. Perfect for cleaning up Downloads folders, organizing photo collections, or managing large document libraries.

**Key Features:**
- 🗂️ **7 Organization Modes** - Extension, Alphabet, Patterns, IMG/DSC detection, Sequential, and more
- 🎨 **Modern Tabbed GUI** - Clean, intuitive interface built with tkinter
- ↩️ **Full Undo Support** - Every operation is logged and reversible
- 🔍 **Pattern Search & Collect** - Find and collect files matching custom patterns
- 📁 **Quick Folder Creation** - Auto-create A-Z, 0-9 folder structures
- 🛡️ **Safe Operations** - Path traversal protection, atomic file moves, TOCTOU protection
- 📊 **Operation History** - Complete logging with statistics
- 🚀 **High Performance** - Memory-efficient generator pattern handles 100,000+ files

---

## 📸 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────┐
│  File Organizer v6.3 GUI Enhancements               │
├─────────────────────────────────────────────────────┤
│  Source: [Recent Directories Dropdown        ] 📂   │
│  Target: [Recent Directories Dropdown        ] 📂   │
│                                                     │
│  [📂 Organize] [🔧 Tools] [⚙️ Advanced]            │
│  ├─ By Extension                                    │
│  ├─ Alphabetize                                     │
│  ├─ IMG/DSC Detection                               │
│  ├─ Smart Pattern                                   │
│  └─ Sequential Pattern                              │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

**Option 1: Run from source**
```bash
# Clone repository
git clone https://github.com/Emfiloel/my-monetization-project.git
cd my-monetization-project

# Run the application
python src/file_organizer.py
```

**Option 2: Download executable**
```bash
# Download from Releases page (Windows only)
# Double-click file_organizer.exe
```

### Basic Usage

1. **Select Source Folder** - Where your unorganized files are
2. **Select Target Folder** - Where organized folders will be created
3. **Choose Organization Mode** - Click the mode you want
4. **Preview** (optional) - See what will happen before organizing
5. **Organize** - Click to execute

**Example: Organize Downloads by extension**
```
Before:
Downloads/
├─ vacation.jpg
├─ document.pdf
├─ photo.png
└─ report.docx

After:
Organized/
├─ JPG/
│  └─ vacation.jpg
├─ PDF/
│  └─ document.pdf
├─ PNG/
│  └─ photo.png
└─ DOCX/
   └─ report.docx
```

---

## 📋 Organization Modes

### 1. By Extension
Groups files by file type (JPG/, PDF/, TXT/, etc.)

### 2. Alphabetize
Organizes by first letter/number (A-Z/, 0-9/, !@#$/)

### 3. IMG/DSC Detection
Identifies camera files (IMG_1234 → IMG/, DSC_5678 → DSC/)

### 4. Smart Pattern Detection
Detects delimiters and groups files:
- `Project-Report-2024.pdf` → `Project-Report/`
- `Vacation_Photos_Summer.jpg` → `Vacation_Photos/`

### 5. Sequential Pattern
Groups numbered sequences:
- `file001.txt, file002.txt` → `File/`

### 6. Extract All to Parent
Flattens nested directory structures

### 7. Extract Up N Levels
Reduces nesting depth by N levels

---

## ✨ v6.3 New Features

### 🆕 Auto-Create A-Z + 0-9 Folders
One-click creation of alphabetical folder structure (A-Z, 0-9, !@#$)

### 🆕 Custom Pattern Search
Search for files matching patterns (wildcards supported) and collect them into a folder

### 🆕 Tabbed Interface
Organized into 3 tabs: Organize, Tools, Advanced

### 🆕 Recent Directories
Dropdown menus remember your last 10 source/target folders

---

## 🛡️ Safety Features

### Path Traversal Protection
- Blocks system directories (C:\Windows, /System, /usr)
- Prevents organizing critical system folders
- Symlink resolution to prevent bypass

### TOCTOU Protection
- Atomic file operations
- Double-check pattern before moves
- Graceful handling of race conditions

### Windows Reserved Names
- Sanitizes folder names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- Prevents Windows filesystem errors

### Complete Undo
- Every operation logged to `.file_organizer_data/operations.jsonl`
- Undo restores files to original locations
- Operation history with timestamps

---

## 🧪 Testing

### Run Unit Tests
```bash
cd tests/
python test_v6_3.py
```

**Expected output:**
```
======================================================================
FILE ORGANIZER v6.3 - TEST SUITE
======================================================================
Ran 17 tests in 1.267s
OK
[PASS] ALL v6.3 TESTS PASSED
```

### Run Comprehensive Feature Tests
```bash
python tests/test_all_features.py
```

Runs 27 comprehensive tests covering all modes, features, and edge cases.

---

## 📁 Project Structure

```
file-organizer/
├── src/
│   └── file_organizer.py          # Main application (v6.3)
├── tests/
│   ├── test_v6_3.py                # Unit tests
│   └── test_all_features.py        # Comprehensive test suite
├── tools/
│   ├── file_generator.py           # Test file generator
│   └── build/                      # Build scripts for executables
├── docs/
│   ├── guides/                     # User guides
│   ├── architecture/               # Technical documentation
│   └── history/                    # Version history docs
├── archive/
│   ├── v6.1/                       # Previous versions
│   ├── v6.2/
│   └── legacy/                     # Historical versions
├── README.md                       # This file
├── CHANGELOG.md                    # Version history
└── LICENSE                         # MIT License
```

---

## 🔧 Configuration

Configuration is stored in `.file_organizer_data/config.json`

**Default settings:**
```json
{
  "max_files_per_folder": 0,
  "duplicate_detection_method": "hash",
  "skip_folders": [
    ".git", "node_modules", "__pycache__",
    ".file_organizer_data"
  ],
  "batch_size": 100,
  "recent_directories": {
    "source": [],
    "target": []
  }
}
```

---

## 📊 Version History

### v6.3 (Current) - GUI Enhancements
- ✨ Auto-create A-Z + 0-9 folder structures
- ✨ Custom pattern search and collect
- ✨ Tabbed interface (Organize, Tools, Advanced)
- ✨ Recent directories dropdown
- ✅ 17 tests passing

### v6.2 - In-Place Organization
- ✨ In-place organization mode
- ✨ Skip folders with # prefix
- ✅ 15 tests passing

### v6.1 - Enhanced Architecture
- ✨ Undo progress bar
- ✨ Comprehensive unit tests (30+ tests)
- ✨ Type hints throughout

### v6.0 - Production Release
- ✅ All 7 architectural blockers addressed
- ✅ Transaction logging & undo
- ✅ Memory efficiency (generator pattern)
- ✅ TOCTOU protection
- ✅ Path traversal security
- ✅ GUI threading
- ✅ Silent failure prevention

**See [CHANGELOG.md](CHANGELOG.md) for complete history**

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- 🧪 More test coverage (currently 17 tests, target 50+)
- 🌍 Internationalization (multi-language support)
- 🎨 UI/UX improvements
- 📱 Cross-platform testing (Linux, macOS)
- 🔌 Plugin architecture
- 🤖 ML-based pattern learning

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with Python and tkinter
- Inspired by need for efficient file organization
- Developed through multi-agent architecture validation process
- Documentation generated with assistance from Claude AI

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Emfiloel/my-monetization-project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Emfiloel/my-monetization-project/discussions)

---

## 🎯 Roadmap

### v6.4 - Consolidation (Planned)
- 🔄 Modular architecture refactor
- 🧪 50% test coverage
- 🤖 CI/CD with GitHub Actions

### v7.0 - Innovation (Future)
- 🔌 Plugin architecture
- 🤖 ML pattern learning
- ☁️ Cloud storage integration
- 🌐 Web interface

---

**Made with ❤️ by the File Organizer team**

*Last updated: November 2025*
