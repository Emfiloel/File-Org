# File Organizer v7.0

> **Professional-grade file organization tool with AI-powered pattern learning, intelligent duplicate detection, and complete undo capability.**

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen.svg)](tests/)

---

## 🎯 What is File Organizer?

File Organizer is a desktop application that automatically organizes your files into logical folder structures based on various criteria. Perfect for cleaning up Downloads folders, organizing photo collections, or managing large document libraries.

**Key Features:**
- 🧠 **AI Pattern Learning** - Learns from your choices and adapts to your workflow
- 🔀 **Intelligent Duplicate Detection** - Date-aware collision handling with EXIF support
- 🗂️ **7 Organization Modes** - Extension, Alphabet, Patterns, IMG/DSC detection, Sequential, and more
- 🎨 **Modern Tabbed GUI** - Clean, intuitive 4-tab interface built with tkinter
- ↩️ **Full Undo Support** - Every operation is logged and reversible
- 🔍 **Pattern Search & Collect** - Find and collect files matching custom patterns
- 📁 **Quick Folder Creation** - Auto-create A-Z, 0-9 folder structures
- 🛡️ **Safe Operations** - Path traversal protection, atomic file moves, TOCTOU protection
- 📊 **Operation History** - Complete logging with statistics and pattern analytics
- 🚀 **High Performance** - Memory-efficient generator pattern handles 100,000+ files

---

## 📸 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────┐
│  File Organizer v7.0                                │
├─────────────────────────────────────────────────────┤
│  Source: [Recent Directories Dropdown        ] 📂   │
│  Target: [Recent Directories Dropdown        ] 📂   │
│                                                     │
│  [📂 Organize] [🧠 AI Scanner] [🔧 Tools] [⚙️ Adv] │
│  ├─ By Extension                                    │
│  ├─ Alphabetize                                     │
│  ├─ IMG/DSC Detection                               │
│  └─ [NEW] AI Learning with Pattern Statistics       │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

**Option 1: Run from source**
```bash
# Clone repository
git clone https://github.com/Emfiloel/File-Org.git
cd File-Org

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/file_organizer.py
```

**Option 2: Install as package**
```bash
# Install the package
pip install -e .

# Run from anywhere
file-organizer
```

**Option 3: Download executable** (Coming soon)
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

## ✨ v7.0 New Features

### 🧠 AI Pattern Learning
The intelligent pattern detector learns from your choices and automatically applies patterns with increasing confidence:
- 4-tier detection system (Learned, Camera, Sequential, Delimiter)
- Pattern library persists between sessions
- Pattern statistics dashboard
- Preview mode before organizing

### 🔀 Advanced Collision Detection
Smart duplicate handling with date/time awareness:
- EXIF date extraction for photos
- `[d]` suffix for same-size duplicates
- `{d}` suffix for different-size versions
- `!Dupes` folder for true duplicates
- `!Dupes Size` folder for same-day different versions

### 🏠 Enhanced In-Place Organization
When organizing in-place, only root files are organized - files already in subfolders are left untouched

### 📊 Pattern Statistics
View analytics about your learned patterns, confidence scores, and detection methods

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
# Run the main test suite
python tests/test_file_organizer.py

# Or run comprehensive feature tests
python tests/test_all_features.py
```

**Expected output:**
```
======================================================================
FILE ORGANIZER v7.0 - TEST SUITE
======================================================================
Ran 17 tests in 1.267s
OK
[PASS] ALL TESTS PASSED
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
│   └── file_organizer.py          # Main application (v7.0)
├── tests/
│   ├── test_file_organizer.py      # Unit tests (17 tests)
│   └── test_all_features.py        # Comprehensive test suite (27 tests)
├── tools/
│   └── file_generator.py           # Test file generator
├── docs/
│   ├── CHANGELOG.md                # Version history
│   └── CONTRIBUTING.md             # Contribution guidelines
├── archive/
│   ├── v6.4/                       # v6.4 code + docs
│   ├── v6.3/                       # v6.3 code + docs
│   ├── v6.2/                       # v6.2 code + docs
│   ├── v6.1/                       # v6.1 code + docs
│   ├── legacy/                     # Historical versions
│   └── development_history/        # Development documentation
├── .github/
│   └── workflows/                  # CI/CD pipelines (coming soon)
├── README.md                       # This file
├── LICENSE                         # MIT License
├── requirements.txt                # Dependencies
└── setup.py                        # Package installation
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

### v7.0 (Current) - Reorganization & Consolidation
- 🎯 **Repository restructure** for clean v7.0 baseline
- 🧠 **AI Pattern Learning** - 4-tier intelligent detection system
- 🔀 **Advanced Collision Detection** - Date-aware EXIF duplicate handling
- 🏠 **Enhanced In-Place** - Smart subfolder preservation
- 📊 **Pattern Analytics** - Statistics dashboard for learned patterns
- 🗂️ **Code Consolidation** - 82% reduction in code duplication
- 📦 **Proper packaging** - setup.py and requirements.txt added
- ✅ 17 tests passing (backward compatible with v6.4)

### v6.4 - Consolidation (Archived)
- ✨ Intelligent pattern scanner with machine learning
- ✨ Advanced collision detection (EXIF, date/time aware)
- ✨ Enhanced in-place organization (root-only mode)
- ✨ Code quality improvements (82% less duplication)
- 🎨 Dedicated AI Scanner tab in GUI

### v6.3 - GUI Enhancements (Archived)
- ✨ Auto-create A-Z + 0-9 folder structures
- ✨ Custom pattern search and collect
- ✨ Tabbed interface (Organize, Tools, Advanced)
- ✨ Recent directories dropdown

### v6.2 - In-Place Organization (Archived)
- ✨ In-place organization mode
- ✨ Skip folders with # prefix

### v6.1 - Enhanced Architecture (Archived)
- ✨ Undo progress bar
- ✨ Comprehensive unit tests
- ✨ Type hints throughout

**See [docs/CHANGELOG.md](docs/CHANGELOG.md) for complete history**

---

## 🤝 Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

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

- **Issues**: [GitHub Issues](https://github.com/Emfiloel/File-Org/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Emfiloel/File-Org/discussions)

---

## 🎯 Roadmap

### v7.1 - Testing & CI/CD (Next)
- 🧪 Increase test coverage to 50%+
- 🤖 GitHub Actions CI/CD pipeline
- 📦 Automated releases
- 🐳 Docker support

### v7.5 - Modular Architecture (Planned)
- 🔌 Plugin architecture
- 🔧 Configurable organization rules
- 📊 Advanced analytics
- 🌐 Web-based configuration UI

### v8.0 - Cloud & AI (Future)
- ☁️ Cloud storage integration (Google Drive, Dropbox, OneDrive)
- 🤖 Enhanced ML pattern learning
- 🔍 Content-aware organization (image recognition, OCR)
- 🌐 Web interface

---

**Made with ❤️ by the File Organizer team**

*Last updated: December 2025*
*Version: 7.0*
