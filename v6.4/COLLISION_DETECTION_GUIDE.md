# ADVANCED COLLISION DETECTION - USER GUIDE

**Version:** v6.4
**Date:** November 8, 2025
**Status:** ✅ IMPLEMENTED

---

## 🎯 OVERVIEW

v6.4 introduces **intelligent duplicate detection** with date/time comparison and smart folder routing.

### Key Features:
- ✅ **[d] suffix** - Same size files (exact duplicates)
- ✅ **{d} suffix** - Different size files (different versions)
- ✅ **!Dupes folder** - True duplicates (same size + same date)
- ✅ **!Dupes Size folder** - Different versions from same date
- ✅ **EXIF date support** - Reads photo metadata
- ✅ **In-place mode** - Only organizes root files, skips subfolders

---

## 📐 COLLISION DETECTION MATRIX

| Condition | Size | Date | Action | Folder | Filename |
|-----------|------|------|--------|--------|----------|
| True Duplicate | Same | Same | Move | `!Dupes` | `filename[d].ext` |
| Same-Day Versions | Different | Same | Move | `!Dupes Size` | `filename{d}.ext` |
| Similar File | Same | Different | Move | Target Folder | `filename[d].ext` |
| Different Version | Different | Different | Move | Target Folder | `filename{d}.ext` |

---

## 🔍 DETAILED EXAMPLES

### Example 1: True Duplicate (Same Size + Same Date)

```
Moving: vacation.jpg (100KB, 2024-01-15 10:30:00)
Existing: Vacation/vacation.jpg (100KB, 2024-01-15 10:30:00)

Detection:
✅ Same filename
✅ Same size (100KB)
✅ Same date (2024-01-15 10:30:00)

Action: Move to !Dupes/vacation[d].jpg

Reason: True duplicate - likely exact copy
```

**Directory Structure:**
```
/Target/
  ├── Vacation/
  │   └── vacation.jpg (original)
  └── !Dupes/
      └── vacation[d].jpg (duplicate)
```

---

### Example 2: Different Versions Same Day (Different Size + Same Date)

```
Moving: vacation.jpg (150KB, 2024-01-15 10:30:00)
Existing: Vacation/vacation.jpg (100KB, 2024-01-15 10:30:00)

Detection:
✅ Same filename
❌ Different size (150KB vs 100KB)
✅ Same date (2024-01-15 10:30:00)

Action: Move to !Dupes Size/vacation{d}.jpg

Reason: Different versions (edited/resized) from same moment
```

**Directory Structure:**
```
/Target/
  ├── Vacation/
  │   └── vacation.jpg (100KB original)
  └── !Dupes Size/
      └── vacation{d}.jpg (150KB edited version)
```

---

### Example 3: Similar File (Same Size + Different Date)

```
Moving: vacation.jpg (100KB, 2024-06-20 14:00:00)
Existing: Vacation/vacation.jpg (100KB, 2024-01-15 10:30:00)

Detection:
✅ Same filename
✅ Same size (100KB)
❌ Different date (6 months apart)

Action: Move to Vacation/vacation[d].jpg

Reason: Same size but different dates - different photos, keep in folder
```

**Directory Structure:**
```
/Target/
  └── Vacation/
      ├── vacation.jpg (Jan 15)
      └── vacation[d].jpg (Jun 20)
```

---

### Example 4: Different Version (Different Size + Different Date)

```
Moving: vacation.jpg (150KB, 2024-06-20 14:00:00)
Existing: Vacation/vacation.jpg (100KB, 2024-01-15 10:30:00)

Detection:
✅ Same filename
❌ Different size (150KB vs 100KB)
❌ Different date (6 months apart)

Action: Move to Vacation/vacation{d}.jpg

Reason: Different size and date - keep both versions in folder
```

**Directory Structure:**
```
/Target/
  └── Vacation/
      ├── vacation.jpg (100KB, Jan 15)
      └── vacation{d}.jpg (150KB, Jun 20)
```

---

### Example 5: Multiple Collisions (Nested [d] Suffix)

```
Scenario: Multiple files with same name and size on same date

Files:
1. vacation.jpg (100KB, 2024-01-15 10:30:00)
2. vacation.jpg (100KB, 2024-01-15 10:30:00)
3. vacation.jpg (100KB, 2024-01-15 10:30:00)

Result:
```

**Directory Structure:**
```
/Target/
  ├── Vacation/
  │   └── vacation.jpg (first file)
  └── !Dupes/
      ├── vacation[d].jpg (second file)
      └── vacation[d]2.jpg (third file)
```

---

## 📅 DATE/TIME EXTRACTION

### Priority Order:
1. **EXIF DateTimeOriginal** (for photos) - Most accurate
2. **EXIF DateTime** (fallback for photos)
3. **File modification time** (for non-photos)

### Supported Formats:
- **.jpg, .jpeg** - EXIF data extracted
- **.tiff, .tif** - EXIF data extracted
- **All other files** - Use file modification time

### Date Comparison Tolerance:
- **Threshold:** 1 second
- **Reason:** Account for file system precision differences

---

## 🏠 IN-PLACE MODE BEHAVIOR

### When "Organize in Place" is Checked:

**Root Files** ✅ Organized
```
/MyPhotos/
  ├── vacation-001.jpg  ← WILL BE ORGANIZED
  ├── trip-002.jpg      ← WILL BE ORGANIZED
  └── IMG_1234.jpg      ← WILL BE ORGANIZED
```

**Subfolder Files** ❌ Left Alone
```
/MyPhotos/
  └── Summer/
      ├── beach.jpg     ← LEFT UNTOUCHED
      └── sunset.jpg    ← LEFT UNTOUCHED
```

**After Organization:**
```
/MyPhotos/
  ├── Vacation/
  │   └── vacation-001.jpg  (moved from root)
  ├── Trip/
  │   └── trip-002.jpg      (moved from root)
  ├── IMG/
  │   └── IMG_1234.jpg      (moved from root)
  └── Summer/
      ├── beach.jpg         ← STILL UNTOUCHED
      └── sunset.jpg        ← STILL UNTOUCHED
```

---

## 🔑 SUFFIX MEANING

### [d] - Same Size Indicator
- **Meaning:** File has same size as existing file
- **Interpretation:** Likely exact duplicate or highly similar
- **Use Case:** True duplicates, copied files

### {d} - Different Size Indicator
- **Meaning:** File has different size than existing file
- **Interpretation:** Different version, edited, or resized
- **Use Case:** Edited photos, different quality levels

---

## 📁 SPECIAL FOLDERS

### !Dupes Folder
- **Purpose:** Store true duplicates (same size + same date)
- **Location:** Target directory root (same level as A-Z folders)
- **Naming:** Uses `!` prefix to sort at top
- **Suffix:** Files get `[d]` suffix

### !Dupes Size Folder
- **Purpose:** Store different versions from same moment
- **Location:** Target directory root (same level as A-Z folders)
- **Naming:** Uses `!` prefix to sort at top
- **Suffix:** Files get `{d}` suffix

**Example Directory:**
```
/Target/
  ├── !Dupes/           ← True duplicates
  ├── !Dupes Size/      ← Different versions same day
  ├── A/
  ├── B/
  ├── Vacation/
  └── IMG/
```

---

## ⚙️ CONFIGURATION

### Enable/Disable Features:

**Hash-Based Duplicate Detection** (Recommended)
```json
{
  "duplicate_detection": {
    "method": "hash",
    "hash_algorithm": "md5",
    "chunk_size": 8192
  }
}
```

**Size-Only Detection** (Faster but less accurate)
```json
{
  "duplicate_detection": {
    "method": "size_only"
  }
}
```

---

## 🧪 TESTING SCENARIOS

### Test 1: Basic Duplicate
```
1. Organize: vacation.jpg (100KB, Jan 15)
2. Organize again: vacation.jpg (100KB, Jan 15)
Expected: !Dupes/vacation[d].jpg
```

### Test 2: Edited Version Same Day
```
1. Organize: photo.jpg (100KB, Jan 15 10:30)
2. Organize: photo.jpg (150KB, Jan 15 10:30)
Expected: !Dupes Size/photo{d}.jpg
```

### Test 3: Same Size Different Day
```
1. Organize: sunset.jpg (200KB, Jan 15)
2. Organize: sunset.jpg (200KB, Jun 20)
Expected: Sunset/sunset[d].jpg
```

### Test 4: In-Place Mode
```
Before:
/Photos/
  ├── IMG_001.jpg
  ├── IMG_002.jpg
  └── Already Sorted/
      └── old_photo.jpg

After:
/Photos/
  ├── IMG/
  │   ├── IMG_001.jpg
  │   └── IMG_002.jpg
  └── Already Sorted/
      └── old_photo.jpg  ← UNTOUCHED
```

---

## 🎓 DECISION TREE

```
File Collision Detected
│
├─ Get Source Size & Date
├─ Get Existing Size & Date
│
├─ Compare Sizes:
│  │
│  ├─ SAME SIZE:
│  │  │
│  │  ├─ Compare Dates:
│  │  │  │
│  │  │  ├─ SAME DATE (within 1 sec):
│  │  │  │  └─ Move to !Dupes/filename[d].ext
│  │  │  │
│  │  │  └─ DIFFERENT DATE:
│  │  │     └─ Move to TargetFolder/filename[d].ext
│  │  │
│  │
│  └─ DIFFERENT SIZE:
│     │
│     ├─ Compare Dates:
│     │  │
│     │  ├─ SAME DATE (within 1 sec):
│     │  │  └─ Move to !Dupes Size/filename{d}.ext
│     │  │
│     │  └─ DIFFERENT DATE:
│     │     └─ Move to TargetFolder/filename{d}.ext
│     │
```

---

## 💡 TIPS & BEST PRACTICES

### For Best Results:
1. ✅ **Enable hash detection** for accuracy
2. ✅ **Preview first** to understand file routing
3. ✅ **Check !Dupes folders** after organizing
4. ✅ **Use EXIF-capable photos** for accurate dates
5. ✅ **Enable in-place mode** to preserve subfolder organization

### What to Do with !Dupes:
1. **Review** - Check if files are truly duplicates
2. **Delete** - Remove true duplicates to save space
3. **Keep** - Preserve if needed for backup
4. **Archive** - Move to external storage

### What to Do with !Dupes Size:
1. **Compare** - Check quality/size differences
2. **Choose Best** - Keep highest quality version
3. **Delete Lower Quality** - Save disk space
4. **Keep Both** - If both versions needed

---

## 🐛 TROUBLESHOOTING

### Issue: Files Going to Wrong Folder

**Problem:** Files with [d] going to target folder instead of !Dupes

**Solution:** Check if dates are truly the same
- Files must have same date within 1 second
- Check EXIF data vs file modification time
- Use "View Learned Patterns" to see detected dates

### Issue: All Files Getting [d] Suffix

**Problem:** Every file collision gets [d] suffix

**Solution:** This is normal if files have same size
- [d] means same size (not necessarily duplicate)
- Check !Dupes folder for true duplicates
- Different dates will keep files in target folder

### Issue: In-Place Mode Not Working

**Problem:** Subfolder files still being organized

**Solution:** Verify checkbox is enabled
- Check "Organize in Place" checkbox
- Only root-level files should be organized
- Files in subfolders should be skipped

---

## 📊 STATISTICS

After organizing, check the operation log to see:
- Total files moved
- Files sent to !Dupes
- Files sent to !Dupes Size
- Files with [d] suffix
- Files with {d} suffix

**Example Log:**
```
Operation: Intelligent Pattern
Files Moved: 1,234
Duplicates Found: 45
  - !Dupes: 30 files
  - !Dupes Size: 15 files
Target Folder Collisions: 22
  - [d] suffix: 15 files
  - {d} suffix: 7 files
```

---

## 🔬 TECHNICAL DETAILS

### EXIF Date Extraction:
```python
def get_file_datetime(filepath: str) -> Optional[datetime]:
    """
    Extract date/time from file with priority:
    1. EXIF Date/Time Original (for photos)
    2. File modification time (fallback)
    """
```

### Collision Detection:
```python
# Check for collision
if os.path.exists(dst):
    src_size = get_file_size(src)
    dst_size = get_file_size(dst)
    src_date = get_file_datetime(src)
    dst_date = get_file_datetime(dst)

    same_size = (src_size == dst_size)
    same_date = (time_diff < 1)  # 1 second tolerance

    if same_size and same_date:
        move_to("!Dupes", "[d]")
    elif not same_size and same_date:
        move_to("!Dupes Size", "{d}")
    elif same_size and not same_date:
        move_to(target_folder, "[d]")
    else:
        move_to(target_folder, "{d}")
```

---

## ✅ TESTING CHECKLIST

Before using in production:
- [ ] Test with duplicate files (same size + date)
- [ ] Test with edited versions (different size + same date)
- [ ] Test with similar files (same size + different date)
- [ ] Test with different files (different size + date)
- [ ] Test in-place mode with subfolders
- [ ] Verify !Dupes folder creation
- [ ] Verify !Dupes Size folder creation
- [ ] Check EXIF date extraction on photos
- [ ] Verify [d] and {d} suffixes
- [ ] Test nested collisions (multiple [d] files)

---

**End of Collision Detection Guide**

**Generated:** November 8, 2025
**Version:** v6.4 Consolidation
**Status:** Production Ready
