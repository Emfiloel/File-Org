# File Organizer

> **Professional-grade file organization tool with AI-powered pattern learning, intelligent duplicate detection, and complete undo capability.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/Emfiloel/File-Org/workflows/CI/badge.svg)](https://github.com/Emfiloel/File-Org/actions/workflows/ci.yml)
[![Code Quality](https://github.com/Emfiloel/File-Org/workflows/Code%20Quality/badge.svg)](https://github.com/Emfiloel/File-Org/actions/workflows/code-quality.yml)
[![Tests](https://img.shields.io/badge/tests-67%20passing-brightgreen.svg)](v7.0/tests/)

---

## 📁 Repository Structure

```
File-Org/
├── v7.0/                    # ✅ STABLE RELEASE (December 2025)
│   ├── src/                 # Source code
│   ├── tests/               # Test suite (67 tests)
│   ├── docs/                # Documentation
│   ├── requirements.txt     # Production dependencies
│   ├── requirements-dev.txt # Development dependencies
│   ├── setup.py            # Installation script
│   └── README.md           # Full documentation
│
├── v7.1-dev/               # 🚧 ACTIVE DEVELOPMENT (Work in Progress)
│   └── [Same structure as v7.0 with ongoing improvements]
│
├── archive/                # Previous versions
│   ├── v6.4/              # Custom folder hierarchy
│   ├── v6.3/              # AI pattern learning
│   ├── v6.2/              # In-place organization
│   └── v6.1/              # Reserved name sanitization
│
├── .github/               # GitHub Actions CI/CD workflows
└── README.md              # This file
```

---

## 🚀 Quick Start

### For Users (Stable Release)
```bash
# Navigate to stable release
cd v7.0/

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/file_organizer.py
```

### For Developers (Active Development)
```bash
# Navigate to development version
cd v7.1-dev/

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run the application
python src/file_organizer.py
```

---

## 🎯 What is File Organizer?

File Organizer is a desktop application that automatically organizes your files into logical folder structures based on various criteria. Perfect for cleaning up Downloads folders, organizing photo collections, or managing large document libraries.

---

## ✨ Features by Version

### **v7.0 (Current Stable Release)** - December 2025

**🆕 New in v7.0:**
- ✅ **Code Reliability Improvements**
  - Specific exception handling (replaced 10 generic handlers)
  - Thread-safe operation management with `OperationManager`
  - Enhanced structured logging with rotation (5MB, 3 backups)
  - Concurrent operation prevention

- ✅ **Date-Based Organization**
  - Organize by Year (YYYY)
  - Organize by Month (YYYY-MM)
  - Organize by Full Date (YYYY-MM-DD)
  - EXIF date extraction for photos

- ✅ **Custom Folder Hierarchy Creator**
  - Dash-delimited parsing (e.g., TMC-Aileron-LH)
  - Numbered subfolder generation (001-999)
  - Input validation and error handling

- ✅ **Expanded Test Coverage**
  - 67 tests (up from 17 in v6.4)
  - Core functions, date organization, custom folders
  - 394% increase in test coverage

**🔧 Infrastructure:**
- GitHub Actions CI/CD (15 configurations: 3 OS × 5 Python versions)
- Code quality automation (Black, flake8, mypy, Bandit, Safety)
- Automated releases with changelog generation
- PR checks with test status comments

### **v6.4** - Custom Folder Hierarchy
- Custom nested folder creation
- Numbered subfolder generation

### **v6.3** - AI Pattern Learning
- 4-tier intelligent pattern detection
- Pattern analytics dashboard
- 82% code consolidation

### **v6.2** - In-Place Organization
- Organize within same folder
- Skip folders with # prefix

### **v6.1** - Reserved Name Sanitization
- Windows reserved name handling
- Case-insensitive security checks

---

## 📊 Key Features

- 🧠 **AI Pattern Learning** - Learns from your choices and adapts to your workflow
- 🔀 **Intelligent Duplicate Detection** - Date-aware collision handling with EXIF support
- 🗂️ **9 Organization Modes** - Extension, Alphabet, Date (Year/Month/Full), Patterns, IMG/DSC detection, Sequential
- 🎨 **Modern Tabbed GUI** - Clean, intuitive 4-tab interface built with tkinter
- ↩️ **Full Undo Support** - Every operation is logged and reversible
- 🔍 **Pattern Search & Collect** - Find and collect files matching custom patterns
- 📁 **Quick Folder Creation** - Auto-create A-Z, 0-9, or custom hierarchies
- 🛡️ **Safe Operations** - Path traversal protection, atomic file moves, TOCTOU protection
- 📊 **Operation History** - Complete logging with statistics and pattern analytics
- 🚀 **High Performance** - Memory-efficient generator pattern handles 100,000+ files
- 🔒 **Thread-Safe** - Concurrent operation management with proper locking

---

## 🧪 Testing

```bash
# Run all tests
cd v7.0/
python -m unittest discover -s tests -p "test_*.py" -v

# Test results (v7.0)
# Ran 67 tests in 0.9s
# OK (skipped=10)
```

**Test Coverage:**
- ✅ Core functions (18 tests)
- ✅ Date organization (8 tests)
- ✅ Custom folder hierarchy (14 tests)
- ✅ File organizer features (17 tests)
- ⏭️ AI pattern enhancements (10 tests - future features)

---

## 📚 Documentation

- **[v7.0 Full Documentation](v7.0/README.md)** - Complete feature guide
- **[Code Reliability Analysis](v7.0/docs/CODE_RELIABILITY_ANALYSIS.md)** - Reliability improvements
- **[CI/CD Workflows](.github/workflows/)** - Automation documentation

---

## 🤝 Contributing

1. Work in the `v7.1-dev/` directory
2. Run tests before committing
3. Follow conventional commit format
4. Ensure CI passes on all platforms

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **GitHub Repository:** https://github.com/Emfiloel/File-Org
- **Issues:** https://github.com/Emfiloel/File-Org/issues
- **CI/CD:** https://github.com/Emfiloel/File-Org/actions

---

**Version:** v7.0 Stable | **Last Updated:** December 25, 2025
