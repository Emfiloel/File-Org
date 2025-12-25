# Contributing to File Organizer

Thank you for your interest in contributing to File Organizer! We welcome contributions from the community.

---

## 🎯 How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
- Check the [existing issues](https://github.com/Emfiloel/my-monetization-project/issues) to avoid duplicates
- Gather details about your environment (OS, Python version)
- Reproduce the bug and document the steps

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 10, macOS 14, Ubuntu 22.04]
 - Python Version: [e.g. 3.9.5]
 - File Organizer Version: [e.g. v6.3]

**Additional context**
Any other context about the problem.
```

### Suggesting Features

We love feature suggestions! Please:
1. Check [existing feature requests](https://github.com/Emfiloel/my-monetization-project/issues?q=is%3Aissue+label%3Aenhancement)
2. Open a new issue with label `enhancement`
3. Clearly describe the feature and its benefits
4. Include mockups or examples if applicable

### Code Contributions

**Areas we'd love help with:**
- 🧪 **Testing**: Increase test coverage (currently 17 tests, target 50+)
- 🌍 **i18n**: Multi-language support
- 🎨 **UI/UX**: Interface improvements
- 📱 **Cross-platform**: Linux/macOS testing and fixes
- 🔌 **Plugins**: Plugin architecture implementation
- 🤖 **ML**: Pattern learning algorithms
- 📝 **Documentation**: Guides, tutorials, API docs

---

## 🚀 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/my-monetization-project.git
cd my-monetization-project
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Set Up Environment

```bash
# Install Python 3.7+ if not already installed
python --version

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies (if any)
# pip install -r requirements-dev.txt
```

### 4. Make Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 5. Test Your Changes

```bash
# Run unit tests
python tests/test_v6_3.py

# Run comprehensive tests
python tests/test_all_features.py

# Test the application
python src/file_organizer.py
```

### 6. Commit Your Changes

Follow conventional commits:

```bash
# Format: <type>(<scope>): <subject>

git commit -m "feat(gui): add dark mode toggle"
git commit -m "fix(organize): resolve collision handling bug"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(patterns): add sequential pattern tests"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 📝 Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where applicable

**Example:**
```python
def organize_files(source_dir: str, target_dir: str, mode: str) -> Tuple[int, int]:
    """
    Organize files from source to target directory.

    Args:
        source_dir: Path to source directory
        target_dir: Path to target directory
        mode: Organization mode ('extension', 'alphabet', etc.)

    Returns:
        Tuple of (files_moved, files_failed)
    """
    files_moved = 0
    files_failed = 0

    # Implementation here

    return files_moved, files_failed
```

### Documentation

- Add docstrings to all functions
- Use Google-style docstrings
- Update README.md if adding user-facing features
- Add comments for non-obvious code

### Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for meaningful test names

**Example:**
```python
def test_organize_by_extension_creates_folders():
    """Test that organize by extension creates correct folder structure"""
    # Setup
    source = create_test_directory()

    # Execute
    result = organize_by_extension(source, target)

    # Assert
    assert os.path.exists(os.path.join(target, 'JPG'))
    assert os.path.exists(os.path.join(target, 'PDF'))
```

---

## 🔍 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`python tests/test_v6_3.py`)
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manually tested the application

## Screenshots (if applicable)
Add screenshots of UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## 🏗️ Project Architecture

Understanding the codebase:

```
file-organizer/
├── src/
│   └── file_organizer.py       # Main application
│       ├── GUI components (tkinter)
│       ├── Organization logic
│       ├── Pattern detection
│       └── File operations
├── tests/
│   ├── test_v6_3.py            # Unit tests
│   └── test_all_features.py    # Integration tests
├── tools/
│   └── file_generator.py       # Test file generation
└── docs/
    └── Various documentation
```

### Key Components

**OperationLogger** (lines 175-254)
- Logs all file operations to `.file_organizer_data/operations.jsonl`
- Enables undo functionality

**Pattern Detection** (lines 1571-1899)
- `detect_folder_name()`: Main pattern detection logic
- `detect_sequential_pattern()`: Numbered file detection
- `extract_img_tag()`: Camera file detection

**File Operations** (lines 992-1052)
- `collect_files_generator()`: Memory-efficient file collection
- `move_file()`: Atomic file moving with TOCTOU protection

**Security** (lines 602-697)
- `is_safe_directory()`: Path traversal protection
- `sanitize_folder_name()`: Windows reserved name handling

---

## 🎯 Good First Issues

Looking for a place to start? Check issues labeled:
- `good first issue` - Easy tasks for newcomers
- `help wanted` - Tasks we need help with
- `documentation` - Documentation improvements

---

## 💬 Questions?

- **General questions**: [GitHub Discussions](https://github.com/Emfiloel/my-monetization-project/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/Emfiloel/my-monetization-project/issues)
- **Feature requests**: [GitHub Issues](https://github.com/Emfiloel/my-monetization-project/issues) with `enhancement` label

---

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to a positive environment:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## 🙏 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes for their contributions
- GitHub Contributors page

---

**Thank you for contributing to File Organizer!**

*Together we can build something amazing.*
