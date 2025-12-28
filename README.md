# File Organizer

> **Professional-grade file organization tool with AI-powered pattern learning, intelligent duplicate detection, and complete undo capability.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/Emfiloel/File-Org/workflows/CI/badge.svg)](https://github.com/Emfiloel/File-Org/actions/workflows/ci.yml)
[![Code Quality](https://github.com/Emfiloel/File-Org/workflows/Code%20Quality/badge.svg)](https://github.com/Emfiloel/File-Org/actions/workflows/code-quality.yml)
[![Tests](https://img.shields.io/badge/tests-90%20passing-brightgreen.svg)](v7.1/tests/)

---

## 📁 Repository Structure

```
File-Org/
├── v7.2/                    # ✅ CURRENT VERSION (December 2025)
│   ├── src/                 # Source code
│   ├── tests/               # Test suite (90 tests)
│   ├── docs/                # Documentation
│   ├── requirements.txt     # Production dependencies
│   └── requirements-dev.txt # Development dependencies
│
├── v7.1/                    # Previous version (archived)
├── .github/                # GitHub Actions CI/CD workflows
└── README.md               # This file
```

> 📦 **Previous versions** (v7.0, v6.4, v6.3, v6.2, v6.1) are archived in the private [File-Org-Archive](https://github.com/Emfiloel/File-Org-Archive) repository.

---

## 🚀 Quick Start

```bash
# Navigate to current version
cd v7.2/

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/file_organizer.py
```

### For Developers

```bash
# Navigate to current version
cd v7.2/

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

## ✨ Features

### **v7.2 (Current Version)** - December 2025

**🆕 New in v7.2:**
- ✅ **Recursive Missing File Scanner**
  - Scan entire directory trees for missing files
  - Process each subfolder independently
  - Interactive folder selection UI with pattern counts
  - Progress tracking for large folder hierarchies
  - Choose between single-folder or recursive mode

- ✅ **Global Case Sensitivity Toggle**
  - Control case-sensitive matching for all operations
  - Affects pattern search, extensions, folders, camera tags
  - GUI checkbox near "target = source" option
  - Defaults to case-insensitive for backward compatibility
  - Windows path validation stays case-insensitive for security

- ✅ **Send to Recycle Bin**
  - Safely remove files with system recycle bin integration
  - Dedicated button in file selection window
  - Platform-independent (Windows/Mac/Linux via send2trash)
  - Confirmation dialog prevents accidental deletion
  - Operation logging for tracking

- ✅ **Enhanced Security**
  - Removed all user-specific paths from documentation
  - Cleaned up SECURITY_AUDIT_REPORT.md
  - Protected path validation for recycle bin operations

**Features from v7.1:**
- ✅ **Missing File Scanner**
  - Detects gaps in numbered file sequences
  - Creates placeholder files to maintain organization
  - Supports pure numeric (001.jpg) and prefixed files (IMG_001.jpg)
  - Centralized logging in missing_files.log

- ✅ **Enhanced Pattern Search**
  - Case-insensitive pattern matching
  - Folder name validation and error handling
  - Comprehensive debugging logs

**Features from v7.0:**
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
  - 90 tests (up from 67 in v7.0)
  - Missing file scanner tests (23 new tests)
  - Core functions, date organization, custom folders

**🔧 Infrastructure:**
- GitHub Actions CI/CD (15 configurations: 3 OS × 5 Python versions)
- Code quality automation (Black, flake8, mypy, Bandit, Safety)
- Automated releases with changelog generation
- PR checks with test status comments

---

## 📊 Key Features

- 🧠 **AI Pattern Learning** - Learns from your choices and adapts to your workflow
- 🔀 **Intelligent Duplicate Detection** - Date-aware collision handling with EXIF support
- 🗂️ **9 Organization Modes** - Extension, Alphabet, Date (Year/Month/Full), Patterns, IMG/DSC detection, Sequential
- 🎨 **Modern Tabbed GUI** - Clean, intuitive 4-tab interface built with tkinter
- ↩️ **Full Undo Support** - Every operation is logged and reversible
- 🔍 **Pattern Search & Collect** - Find and collect files matching custom patterns
- 📁 **Quick Folder Creation** - Auto-create A-Z, 0-9, or custom hierarchies
- 🔍 **Missing File Scanner** - Detect and fill gaps in numbered sequences
- 🛡️ **Safe Operations** - Path traversal protection, atomic file moves, TOCTOU protection
- 📊 **Operation History** - Complete logging with statistics and pattern analytics
- 🚀 **High Performance** - Memory-efficient generator pattern handles 100,000+ files
- 🔒 **Thread-Safe** - Concurrent operation management with proper locking

---

## 🧪 Testing

```bash
# Run all tests
cd v7.1/
python -m unittest discover -s tests -p "test_*.py" -v

# Test results (v7.1)
# Ran 90 tests in 1.2s
# OK (skipped=10)
```

**Test Coverage:**
- ✅ Core functions (18 tests)
- ✅ Date organization (8 tests)
- ✅ Custom folder hierarchy (14 tests)
- ✅ Missing file scanner (23 tests)
- ✅ File organizer features (17 tests)
- ⏭️ AI pattern enhancements (10 tests - future features)

---

## 📚 Documentation

- **[Full Documentation](v7.1/docs/)** - Complete feature guide
- **[Code Reliability Analysis](v7.1/docs/CODE_RELIABILITY_ANALYSIS.md)** - Reliability improvements
- **[CI/CD Workflows](.github/workflows/)** - Automation documentation

---

## 🤝 Contributing

1. Work in the `v7.1/` directory
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

**Version:** v7.1 | **Last Updated:** December 26, 2025
