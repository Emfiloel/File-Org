# File Generator - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Build the Executable
```batch
build_generator.bat
```

### Step 2: Run the Generator
```batch
dist\FileGenerator.exe
```

### Step 3: Generate Files
1. Click **Browse...** → Select output folder
2. Set file count (default: 1,000,000)
3. Click **▶ Generate Files**

---

## 📊 What You'll Get

### 1,000,000 Files Distributed As:

| Type | Count | Purpose |
|------|-------|---------|
| Extension variety | 150,000 | Test "By Extension" mode |
| Alphabet (A-Z, 0-9, !@#$) | 100,000 | Test "By Alphabet" mode |
| Numeric (1, 42, 999) | 80,000 | Test "By Numeric" mode |
| Camera tags (IMG_, DSC_) | 120,000 | Test "By IMG/DSC" mode |
| Smart patterns | 200,000 | Test "Smart Pattern" mode |
| Sequential patterns | 150,000 | Test "Sequential" mode |
| Edge cases | 50,000 | Test sanitization & handling |
| Random | 150,000 | General testing |

---

## 🎯 Example Filenames Generated

```
✓ document_42.pdf
✓ Apple.txt → A folder
✓ 42.txt → 42 folder
✓ IMG_0001.jpg → IMG folder
✓ vacation-001.jpg → vacation folder
✓ report-001-final.pdf → report folder
✓ CON.txt → Tests reserved name sanitization
✓ café.txt → Tests Unicode handling
✓ file with spaces.txt → Tests space handling
✓ multi-part-name.txt → Tests hyphen patterns
✓ snake_case_file.txt → Tests underscore patterns
✓ Xj9kL2mP.doc → Random filename
```

---

## ⏱️ Generation Time

| Disk Type | Speed | Time for 1M files |
|-----------|-------|-------------------|
| SSD (NVMe) | 50-100k files/sec | 10-20 seconds |
| SSD (SATA) | 20-50k files/sec | 20-50 seconds |
| HDD | 2-10k files/sec | 2-8 minutes |

---

## 💾 Disk Space Needed

- **Minimum:** ~250 MB
- **Typical:** ~4 GB (NTFS cluster size)
- **Recommendation:** 5-10 GB free

---

## 🎮 Testing Workflow

### 1. Generate Files
```batch
dist\FileGenerator.exe
```
- Select folder: `C:\TestFiles`
- Count: 1,000,000
- Click Generate

### 2. Organize with File Organizer v6.3

**Test By Extension:**
- Source: `C:\TestFiles`
- Target: `C:\Organized\ByExtension`
- Mode: By Extension
- Result: `.pdf`, `.jpg`, `.txt` folders

**Test By Alphabet:**
- Mode: By Alphabet
- Result: `A`, `B`, `C`... `Z`, `0-9`, `!@#$` folders

**Test Smart Pattern:**
- Mode: Smart Pattern Detection
- Result: `vacation`, `work`, `project` folders auto-detected

**Test IMG/DSC:**
- Mode: By IMG/DSC Tags
- Result: `IMG`, `DSC`, `VID`, `MOV` folders

**Test Sequential:**
- Mode: Sequential Pattern
- Result: Groups like `report`, `file`, `scan`

**Test Edge Cases:**
- Check: `CON.txt` → becomes `CON_safe.txt`
- Check: `café.txt` → handled correctly
- Check: Long filenames → handled gracefully

---

## 🔥 Pro Tips

### Faster Generation
1. Use SSD instead of HDD
2. Disable antivirus temporarily
3. Close other programs
4. Use fewer files (500,000 instead of 1M)

### Better Testing
1. Generate to empty folder
2. Take before/after screenshots
3. Test one mode at a time
4. Keep original test files for re-testing

### Disk Space Optimization
1. Start with 100,000 files
2. Delete after testing
3. Regenerate as needed

---

## 🛠️ Troubleshooting

**Slow generation?**
→ Check disk type (HDD vs SSD)
→ Disable antivirus
→ Reduce file count

**Out of space?**
→ Free up disk space
→ Reduce to 100,000-500,000 files
→ Use different drive

**Can't select folder?**
→ Try different location
→ Check permissions
→ Run as Administrator

---

## 📁 File Structure After Build

```
v6.3/
├── dist/
│   └── FileGenerator.exe        ← Run this!
├── file_generator.py            ← Source
├── build_generator.bat          ← Build script
├── build_generator_exe.spec     ← PyInstaller config
├── FILE_GENERATOR_README.md     ← Full docs
└── GENERATOR_QUICK_START.md     ← This file
```

---

## ✅ Verification Checklist

After generation:

- [ ] File count matches (check folder properties)
- [ ] Various extensions present (.pdf, .jpg, .txt, etc.)
- [ ] IMG/DSC files exist (IMG_0001.jpg, etc.)
- [ ] Pattern files exist (vacation-001.jpg, etc.)
- [ ] Edge cases exist (CON.txt, café.txt, etc.)
- [ ] All files are 0 bytes

---

## 🎯 Common File Counts

| Count | Generation Time | Disk Space | Use Case |
|-------|----------------|------------|----------|
| 10,000 | <1 second | ~40 MB | Quick test |
| 100,000 | 2-10 seconds | ~400 MB | Standard test |
| 500,000 | 10-30 seconds | ~2 GB | Thorough test |
| 1,000,000 | 10-480 seconds | ~4 GB | **Comprehensive test** |

---

## 🌟 Quick Commands

### Build
```batch
build_generator.bat
```

### Run
```batch
dist\FileGenerator.exe
```

### Run with Python (no build)
```bash
python file_generator.py
```

### Clean Build Artifacts
```batch
rmdir /s /q build
del FileGenerator.spec
```

---

## 📞 Need Help?

- **Full Documentation:** `FILE_GENERATOR_README.md`
- **Build Issues:** Check Python and PyInstaller installation
- **Runtime Issues:** Check disk space and permissions

---

**That's it! You're ready to generate 1,000,000 test files! 🚀**

Run `build_generator.bat` now to get started!

---

**Created:** 2025-11-06
**Version:** 1.0
**For:** File Organizer v6.3 Testing
