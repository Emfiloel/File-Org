# ==============================
# FILE ORGANIZER - MASTER FILE 3
# ==============================
# New in this version:
# - AUTOMATIC PATTERN SCANNER: Scans files and detects common naming patterns
# - Handles millions of files efficiently
# - Shows detected patterns with statistics and samples
# - One-click organize by detected patterns
# - Multiple pattern types: prefix, delimiter, camera, date, numeric, extension
# ==============================

import os
import re
import shutil
import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog

# ==============================
# GUI WINDOW SETUP
# ==============================
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    root = TkinterDnD.Tk()
    dnd_available = True
except ImportError:
    root = tk.Tk()
    dnd_available = False

root.title("File Organizer - Master File 3")

# ── THEME ──────────────────────────────────────────────────────────────────────
style = ttk.Style()
for t in ("clam", "vista", "xpnative", "default"):
    try:
        style.theme_use(t)
        break
    except Exception:
        pass

FONT_BASE  = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI Semibold", 12)
root.option_add("*Font", FONT_BASE)
root.configure(padx=10, pady=10)
style.configure("TButton", padding=6)
style.configure("TEntry", padding=4)
style.configure("TLabel", padding=2)
style.configure("Title.TLabel", font=FONT_TITLE)
style.configure("TProgressbar", thickness=12)
style.configure("Section.TLabelframe.Label", font=FONT_TITLE)
levels_entry = None  # will be created in the "Extract Up" section

# ── HEADER ─────────────────────────────────────────────────────────────────────
header = ttk.Frame(root, padding=(8, 8))
header.grid(row=0, column=0, columnspan=3, sticky="ew")
ttk.Label(header, text="File Organizer - Master File 3", style="Title.TLabel").pack(side="left")

# ── SOURCE/TARGET ──────────────────────────────────────────────────────────────
paths_box = ttk.LabelFrame(root, text="Locations", style="Section.TLabelframe")
paths_box.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=(8, 12))
paths_box.columnconfigure(1, weight=1)

ttk.Label(paths_box, text="Source Directory(ies):").grid(row=0, column=0, sticky="e", padx=(8,6), pady=6)
source_entry = ttk.Entry(paths_box)
source_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
ttk.Button(paths_box, text="Browse", command=lambda: source_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=(6,8), pady=6)

ttk.Label(paths_box, text="Target Directory:").grid(row=1, column=0, sticky="e", padx=(8,6), pady=6)
target_entry = ttk.Entry(paths_box)
target_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
ttk.Button(paths_box, text="Browse", command=lambda: target_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2, padx=(6,8), pady=6)

# ==============================
# CORE HELPERS
# ==============================
def get_source_dirs():
    return [d.strip() for d in source_entry.get().split(',') if os.path.isdir(d.strip())]

def report_error(title, message):
    sep = "-" * 70
    try:
        preview_text.insert("end", f"\n{sep}\n{title}: {message}\n{sep}\n")
        preview_text.see("end")
    except Exception:
        print(f"[{title}] {message}")

def move_file(src, dst_folder, filename):
    # Create destination folder and auto-rename on collision: "name (2).ext"
    os.makedirs(dst_folder, exist_ok=True)
    base, ext = os.path.splitext(filename)
    dst = os.path.join(dst_folder, filename)
    counter = 2
    while os.path.exists(dst):
        dst = os.path.join(dst_folder, f"{base} ({counter}){ext}")
        counter += 1
    try:
        shutil.move(src, dst)
    except Exception as e:
        report_error("Error", f"Failed to move {filename}: {e}")

def update_progress(index, total):
    progress_bar["value"] = index
    root.update_idletasks()
    if index == total:
        messagebox.showinfo("Info", "Operation completed successfully")

def show_preview(preview_items):
    preview_text.delete("1.0", tk.END)
    for _, folder, filename in preview_items:
        preview_text.insert(tk.END, f"{filename} → {folder}/\n")

def smart_title(text):
    return '_'.join(w if w.isupper() else w.capitalize() for w in text.split('_'))

# === User mapping (Smart +) ===
MAPPING_FILE = "folder_mappings.json"
USER_MAP = {}
def load_mappings():
    global USER_MAP
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            USER_MAP = json.load(f)
    except Exception:
        USER_MAP = {}
def save_mappings():
    try:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(USER_MAP, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
def make_key(filename: str) -> str:
    base, _ = os.path.splitext(filename)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base)
    base = re.sub(r'(?<=[\-_])\d+[A-Za-z]?$', '', base)
    return base.strip().lower()
load_mappings()

# ==============================
# DETECTION HELPERS
# ==============================
def detect_folder_name(filename):
    base, _ = os.path.splitext(filename)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base).rstrip(' .')
    base = re.sub(r'(?<=[\-_])\d+[A-Za-z]?$', '', base).rstrip(' _-.')
    m = re.search(r'([\-_]?)(\d+)$', base)
    if m:
        pre = base[:m.start()]
        delim = m.group(1)
    else:
        pre, delim = base, ''
    if '_' in pre and '-' not in pre:
        folder = smart_title(pre)
        if delim == '-': folder += '[-]'
    elif '-' in pre and '_' not in pre:
        folder = '-'.join(w.capitalize() for w in pre.split('-'))
        if delim == '_': folder += '[_]'
    elif '-' in pre and '_' in pre:
        folder = '-'.join(w.capitalize() for w in pre.split('-')) if pre.rfind('-') > pre.rfind('_') else smart_title(pre)
        if   delim == '_': folder += '[_]'
        elif delim == '-': folder += '[-]'
    else:
        m_simple = re.match(r"([A-Za-z]+)\d+$", pre)
        folder = m_simple.group(1).capitalize() if m_simple else None
    return folder.rstrip(' .') if folder else None

def extract_img_tag(filename):
    m = re.search(r"(IMG|DSC|DSCN|DCS|DCSN)(?=\d|_|\.|$)", filename, re.IGNORECASE)
    return m.group(1).upper() if m else None

# ==============================
# ORGANIZER ENGINE
# ==============================
def collect_files(source_dirs, logic_func):
    """
    Plan moves (walk first, move later).
    Safe even when Target == Source, because we compute the plan before moving.
    """
    target_root = (target_entry.get() or "").strip()
    all_files = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for file in files:
                src = os.path.join(dirpath, file)
                rel_folder = logic_func(file)
                if not rel_folder:
                    continue
                dst_folder = os.path.join(target_root, rel_folder)
                dst = os.path.join(dst_folder, file)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue
                all_files.append((src, dst_folder, file))
    return all_files

def run_organizer(folder_logic, preview=False):
    source_dirs = get_source_dirs()
    target_dir  = (target_entry.get() or "").strip()

    if not source_dirs:
        messagebox.showerror("Error", "Please select at least one valid source directory.")
        return
    if not target_dir or not os.path.isdir(target_dir):
        messagebox.showerror("Error", "Target directory not set or invalid.")
        return

    logic = lambda fname: folder_logic(fname)
    plan = collect_files(source_dirs, logic)

    if preview:
        filtered = [(src, os.path.relpath(dst_folder, target_dir), fname) for src, dst_folder, fname in plan]
        show_preview(filtered)
        return

    total = len(plan)
    if total == 0:
        messagebox.showinfo("Info", "No files to organize.")
        return
    progress_bar["maximum"] = total
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname)
        update_progress(i, total)

# ==============================
# LOGIC FUNCTIONS
# ==============================
def by_extension(filename):
    ext = os.path.splitext(filename)[1][1:]
    return ext.upper() if ext else "_NOEXT"

def by_alphabet(filename):
    first = filename[0].upper()
    if first.isalpha(): return first
    if first.isdigit(): return "0-9"
    return "!@#$"

def by_numeric_simple(filename):
    """Simple first-character grouping"""
    name = filename.lstrip()
    if not name:
        return "!@#$"
    ch = name[0]
    if ch in '\\/:*?"<>|':
        return "!@#$"
    if ch.isdigit():
        return ch
    if ch.isalpha():
        return ch.upper()
    return ch

def by_img_dsc(filename):
    return extract_img_tag(filename)

def by_detected(filename):
    return detect_folder_name(filename)

def by_detected_or_prompt(filename, allow_prompt=True):
    key = make_key(filename)
    if key in USER_MAP:
        return USER_MAP[key]
    folder = detect_folder_name(filename)
    if folder:
        return folder
    if allow_prompt:
        answer = simpledialog.askstring(
            "Unclassified file",
            f"Enter folder name for:\n\n{filename}\n\nThis choice will be remembered for similar files.\n(Target: {target_entry.get()})"
        )
        if answer:
            USER_MAP[key] = answer.strip()
            save_mappings()
            return USER_MAP[key]
    return None

# ==============================
# ADVANCED NUMERIC BUCKETING (from OG version)
# ==============================
def organize_numerically_advanced(preview=False):
    """
    Advanced numeric bucketing with intelligent merging from original version.
    Groups files by number ranges (0-999, 1000-1999, etc.) with smart merging.
    """
    source_dirs = get_source_dirs()
    target_dir = (target_entry.get() or "").strip()

    if not source_dirs:
        messagebox.showerror("Error", "Please select at least one valid source directory.")
        return
    if not target_dir or not os.path.isdir(target_dir):
        messagebox.showerror("Error", "Target directory not set or invalid.")
        return

    all_files = []
    camera_patterns = ["IMG", "DSC", "DSCN", "DCS", "DCSN"]
    camera_pattern_regex = re.compile(r"\b(" + "|".join(camera_patterns) + r")\b", re.IGNORECASE)
    numeric_pattern = re.compile(r"^(\d+)([_\-]?)")
    text_pattern = re.compile(r"^([A-Za-z]+)")

    buckets = {}  # { base_bucket: [fileinfo, ...] }

    def get_bucket(num: int, size: int) -> int:
        return (num // size) * size

    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)

                # Pattern: IMG, DSC, etc.
                camera_match = camera_pattern_regex.search(filename)
                if camera_match:
                    folder = camera_match.group(1).upper()
                    dst_folder = os.path.join(target_dir, folder)
                    all_files.append((src, dst_folder, filename))
                    continue

                # Numeric pattern
                num_match = numeric_pattern.match(filename)
                if num_match:
                    num_str = num_match.group(1)
                    try:
                        number = int(num_str)
                    except ValueError:
                        continue
                    base_bucket = get_bucket(number, 1000)
                    if base_bucket not in buckets:
                        buckets[base_bucket] = []
                    buckets[base_bucket].append((src, filename))
                    continue

                # Text fallback
                text_match = text_pattern.match(filename)
                if text_match:
                    folder = text_match.group(1).capitalize()
                    dst_folder = os.path.join(target_dir, folder)
                    all_files.append((src, dst_folder, filename))
                    continue

    # Merge buckets intelligently
    sorted_buckets = sorted(buckets.items())
    merged_groups = []
    current_group = []
    group_start = None

    for bucket_val, file_list in sorted_buckets:
        if not current_group:
            current_group.append((bucket_val, file_list))
            group_start = bucket_val
            continue

        current_count = sum(len(lst) for _, lst in current_group)
        is_dense = any(len(lst) >= 50 for _, lst in current_group)

        if current_count + len(file_list) <= 500 and not is_dense:
            current_group.append((bucket_val, file_list))
        else:
            # Finalize previous group
            group_end = current_group[-1][0]
            merged_groups.append((group_start, group_end, current_group))
            current_group = [(bucket_val, file_list)]
            group_start = bucket_val

    # Handle final group
    if current_group:
        group_end = current_group[-1][0]
        merged_groups.append((group_start, group_end, current_group))

    # Assign merged buckets to folders
    for start, end, group in merged_groups:
        folder_name = f"{start}-{end+999}"
        dst_folder = os.path.join(target_dir, folder_name)
        for _, file_list in group:
            for src, filename in file_list:
                all_files.append((src, dst_folder, filename))

    # Preview or execute
    if preview:
        filtered = [(src, os.path.relpath(dst_folder, target_dir), fname)
                    for src, dst_folder, fname in all_files]
        show_preview(filtered)
        return

    total_files = len(all_files)
    if total_files == 0:
        messagebox.showinfo("Numerically Advanced", "No matching files found to organize.")
        return

    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)

# ==============================
# SPECIAL FUNCTIONS (not via run_organizer)
# ==============================
def _nsf_tidy_base(filename):
    base, _ = os.path.splitext(filename)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base).strip().rstrip(' .')
    return base

def _nsf_pad_if_numeric(token, pad=3):
    return token.zfill(pad) if token.isdigit() and len(token) < pad else token

def name_set_file_dash(filename):
    """Match ONLY: ANYTHING-SET-FILENUMBER"""
    base = _nsf_tidy_base(filename)
    m = re.match(r'^.+-(?P<set>[A-Za-z0-9]+)-(?P<file>\d+)$', base)
    if not m:
        return None
    set_token = m.group('set')
    return _nsf_pad_if_numeric(set_token, 3)

def name_set_file_underscore(filename):
    """Match ONLY: ANYTHING_SET_FILENUMBER"""
    base = _nsf_tidy_base(filename)
    m = re.match(r'^.+_(?P<set>[A-Za-z0-9]+)_(?P<file>\d+)$', base)
    if not m:
        return None
    set_token = m.group('set')
    return _nsf_pad_if_numeric(set_token, 3)

def name_set_file_mixed(filename):
    """Match ONLY: ANYTHING <D1> SET <D2> FILENUMBER"""
    base = _nsf_tidy_base(filename)
    m = re.match(r'^.+(?P<d1>[_-])(?P<set>[A-Za-z0-9]+)(?P<d2>[_-])(?P<file>\d+)$', base)
    if not m:
        return None
    d1, set_token, d2 = m.group('d1'), m.group('set'), m.group('d2')
    folder = _nsf_pad_if_numeric(set_token, 3)
    if d1 != d2:
        folder = f"{d1}{folder}{d2}"
    return folder

def organize_zips():
    source_dirs = get_source_dirs()
    target_dir  = (target_entry.get() or "").strip()
    pattern = re.compile(r'(.+)\.zip-\d+', re.IGNORECASE)
    plan = []
    for source_dir in source_dirs:
        for filename in os.listdir(source_dir):
            m = pattern.match(filename)
            if m:
                src = os.path.join(source_dir, filename)
                dst_folder = os.path.join(target_dir, m.group(1))
                plan.append((src, dst_folder, filename))
    total = len(plan)
    if total == 0:
        messagebox.showinfo("Organize Zips", "No multi-part zip files found.")
        return
    progress_bar["maximum"] = total
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname)
        update_progress(i, total)

def organize_top_level_only():
    source_dirs = get_source_dirs()
    target_dir  = (target_entry.get() or "").strip()
    plan = []
    for source_dir in source_dirs:
        for filename in os.listdir(source_dir):
            src = os.path.join(source_dir, filename)
            if not os.path.isfile(src):
                continue
            folder = detect_folder_name(filename) or "Unsorted"
            dst_folder = os.path.join(target_dir, folder)
            dst = os.path.join(dst_folder, filename)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue
            plan.append((src, dst_folder, filename))
    if not plan:
        messagebox.showinfo("Top-Level", "No top-level files found to organize.")
        return
    progress_bar["maximum"] = len(plan)
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname)
        update_progress(i, len(plan))

def extract_all_to_parent():
    source_dirs = get_source_dirs()
    plan = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            if os.path.abspath(dirpath) == os.path.abspath(source):
                continue
            for f in files:
                src = os.path.join(dirpath, f)
                dst = os.path.join(source, f)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue
                plan.append((src, os.path.dirname(dst), f))
    if not plan:
        messagebox.showinfo("Extract", "No files found in subfolders.")
        return
    progress_bar["maximum"] = len(plan)
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname)
        update_progress(i, len(plan))
    # Clean up empties
    removed = 0
    for source in source_dirs:
        for dpath, _, _ in os.walk(source, topdown=False):
            if os.path.abspath(dpath) != os.path.abspath(source) and not os.listdir(dpath):
                try:
                    os.rmdir(dpath); removed += 1
                except Exception:
                    pass
    messagebox.showinfo("Extract Complete", f"Moved {len(plan)} file(s). Removed {removed} empty folder(s).")

def scan_sources():
    source_dirs = get_source_dirs()
    if not source_dirs:
        messagebox.showerror("Scan Sources", "Please select at least one source folder.")
        return

    preview_text.delete("1.0", tk.END)
    total = 0
    for src in source_dirs:
        for dirpath, _, files in os.walk(src):
            for f in files:
                try:
                    rel = os.path.relpath(os.path.join(dirpath, f), src)
                except Exception:
                    rel = os.path.join(dirpath, f)
                preview_text.insert("end", f"{rel}\n")
                total += 1

    if total == 0:
        preview_text.insert("end", "(No files found)\n")
    preview_text.see("end")

def extract_up_levels():
    try:
        levels = int(levels_entry.get())
        if levels < 1: raise ValueError
    except Exception:
        messagebox.showerror("Extract Up", "Please enter a valid number of levels (>=1).")
        return
    source_dirs = get_source_dirs()
    if not source_dirs:
        messagebox.showerror("Extract Up", "Please select at least one source folder.")
        return
    plan = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for fname in files:
                src = os.path.join(dirpath, fname)
                dest_dir = dirpath
                for _ in range(levels):
                    dest_dir = os.path.dirname(dest_dir)
                if len(os.path.abspath(dest_dir)) < len(os.path.abspath(source)):
                    dest_dir = source
                dst = os.path.join(dest_dir, fname)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue
                plan.append((src, dest_dir, fname))
    if not plan:
        messagebox.showinfo("Extract Up", "No files found to move for the chosen level(s).")
        return
    progress_bar["maximum"] = len(plan)
    moved = 0
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname); moved += 1
        update_progress(i, len(plan))
    # Remove empties
    removed_dirs = 0
    for source in source_dirs:
        for dpath, _, _ in os.walk(source, topdown=False):
            if os.path.abspath(dpath) == os.path.abspath(source):
                continue
            if not os.listdir(dpath):
                try: os.rmdir(dpath); removed_dirs += 1
                except: pass
    messagebox.showinfo("Extract Up Complete", f"Moved {moved} file(s). Removed {removed_dirs} empty folder(s).")

# ==============================
# AUTOMATIC PATTERN SCANNER
# ==============================
def analyze_filename_patterns(filenames, progress_callback=None):
    """
    Analyzes a list of filenames and detects common patterns.
    Returns a dictionary of detected patterns with file lists.
    Optimized for millions of files.
    """
    patterns = {}
    total = len(filenames)

    for idx, filename in enumerate(filenames):
        if progress_callback and idx % 5000 == 0:
            progress_callback(idx, total)

        base, ext = os.path.splitext(filename)

        # Pattern 1: Common prefix (letters/words before numbers/delimiters)
        # Example: "Vacation_001" → "Vacation"
        m_prefix = re.match(r'^([A-Za-z]+[A-Za-z\s]*?)[-_\s]*\d', base)
        if m_prefix:
            prefix = m_prefix.group(1).strip()
            pattern_key = f"PREFIX:{prefix}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'prefix',
                    'name': prefix,
                    'files': [],
                    'folder_name': prefix.title()
                }
            patterns[pattern_key]['files'].append(filename)
            continue

        # Pattern 2: Delimiter-based tokens (extract middle token)
        # Example: "Project-Alpha-001" → "Project-Alpha"
        tokens = re.split(r'[-_\s]+', base)
        if len(tokens) >= 2:
            # Remove trailing numeric tokens
            non_numeric_tokens = [t for t in tokens if not t.isdigit()]
            if len(non_numeric_tokens) >= 2:
                pattern_name = '-'.join(non_numeric_tokens[:2])
                pattern_key = f"DELIM:{pattern_name}"
                if pattern_key not in patterns:
                    patterns[pattern_key] = {
                        'type': 'delimiter',
                        'name': pattern_name,
                        'files': [],
                        'folder_name': pattern_name.title()
                    }
                patterns[pattern_key]['files'].append(filename)
                continue

        # Pattern 3: Camera/device tags (IMG, DSC, etc.)
        m_camera = re.search(r'\b(IMG|DSC|DSCN|DCS|DCSN|VID|MOV|PXL)\b', base, re.IGNORECASE)
        if m_camera:
            tag = m_camera.group(1).upper()
            pattern_key = f"CAMERA:{tag}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'camera',
                    'name': tag,
                    'files': [],
                    'folder_name': tag
                }
            patterns[pattern_key]['files'].append(filename)
            continue

        # Pattern 4: Date patterns (YYYY-MM-DD, YYYYMMDD, etc.)
        m_date = re.search(r'(20\d{2})[-_]?(\d{2})[-_]?(\d{2})', base)
        if m_date:
            year, month, day = m_date.groups()
            date_str = f"{year}-{month}"
            pattern_key = f"DATE:{date_str}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'date',
                    'name': date_str,
                    'files': [],
                    'folder_name': date_str
                }
            patterns[pattern_key]['files'].append(filename)
            continue

        # Pattern 5: Pure numeric start (group by first digits)
        m_numeric = re.match(r'^(\d+)', base)
        if m_numeric:
            num = int(m_numeric.group(1))
            # Group into ranges of 1000
            bucket = (num // 1000) * 1000
            pattern_key = f"NUMERIC:{bucket}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'numeric',
                    'name': f"{bucket}-{bucket+999}",
                    'files': [],
                    'folder_name': f"{bucket}-{bucket+999}"
                }
            patterns[pattern_key]['files'].append(filename)
            continue

        # Pattern 6: Extension grouping (fallback)
        if ext:
            ext_clean = ext[1:].upper()
            pattern_key = f"EXT:{ext_clean}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'extension',
                    'name': ext_clean,
                    'files': [],
                    'folder_name': ext_clean
                }
            patterns[pattern_key]['files'].append(filename)
        else:
            # No pattern detected - goes to "Uncategorized"
            pattern_key = "UNCAT:Other"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'uncategorized',
                    'name': 'Other',
                    'files': [],
                    'folder_name': 'Uncategorized'
                }
            patterns[pattern_key]['files'].append(filename)

    if progress_callback:
        progress_callback(total, total)

    return patterns

def show_pattern_scanner():
    """Opens a window to scan and analyze filename patterns - optimized for millions of files"""
    scanner_win = tk.Toplevel(root)
    scanner_win.title("Pattern Scanner & Analyzer")
    scanner_win.geometry("1000x700")
    scanner_win.minsize(800, 500)

    main_frame = ttk.Frame(scanner_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Info label
    info_label = ttk.Label(main_frame, text="🔍 Automatic Pattern Detection - Scan millions of files efficiently",
                           font=("Segoe UI", 11, "bold"))
    info_label.pack(anchor="w", pady=(0, 10))

    # Progress section
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill="x", pady=(0, 10))

    progress_label = ttk.Label(progress_frame, text="Ready to scan...")
    progress_label.pack(anchor="w")

    scan_progress = ttk.Progressbar(progress_frame, mode="determinate")
    scan_progress.pack(fill="x", pady=(5, 0))

    # Results section (scrollable)
    results_frame = ttk.LabelFrame(main_frame, text="Detected Patterns", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Treeview for patterns
    columns = ("Pattern Type", "Pattern Name", "File Count", "Folder Name", "Samples")
    tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)

    tree.heading("Pattern Type", text="Type")
    tree.heading("Pattern Name", text="Pattern")
    tree.heading("File Count", text="Files")
    tree.heading("Folder Name", text="Destination Folder")
    tree.heading("Samples", text="Sample Files")

    tree.column("Pattern Type", width=100)
    tree.column("Pattern Name", width=150)
    tree.column("File Count", width=100)
    tree.column("Folder Name", width=150)
    tree.column("Samples", width=400)

    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill=tk.BOTH, expand=True)
    scrollbar.pack(side="right", fill="y")

    # Store detected patterns globally for organize function
    detected_patterns = {}

    def scan_files():
        source_dirs = get_source_dirs()
        if not source_dirs:
            messagebox.showerror("Error", "Please select source directory first")
            return

        # Clear previous results
        for item in tree.get_children():
            tree.delete(item)

        detected_patterns.clear()

        progress_label.config(text="Scanning files...")
        scanner_win.update()

        # Collect all filenames
        all_files = []
        for source in source_dirs:
            for dirpath, _, files in os.walk(source):
                for f in files:
                    all_files.append((os.path.join(dirpath, f), f))

        total_files = len(all_files)
        progress_label.config(text=f"Found {total_files:,} files. Analyzing patterns...")
        scan_progress["maximum"] = total_files
        scanner_win.update()

        # Analyze patterns
        filenames_only = [f for _, f in all_files]

        def update_progress(current, total):
            scan_progress["value"] = current
            if current % 10000 == 0 or current == total:
                progress_label.config(text=f"Analyzing... {current:,}/{total:,} files ({int(100*current/total)}%)")
                scanner_win.update()

        patterns = analyze_filename_patterns(filenames_only, update_progress)

        # Filter patterns with minimum file count (at least 2 files)
        MIN_FILES = 2
        filtered_patterns = {k: v for k, v in patterns.items() if len(v['files']) >= MIN_FILES}

        # Sort by file count (descending)
        sorted_patterns = sorted(filtered_patterns.items(), key=lambda x: len(x[1]['files']), reverse=True)

        # Display results
        for pattern_key, pattern_data in sorted_patterns:
            ptype = pattern_data['type'].title()
            pname = pattern_data['name']
            count = len(pattern_data['files'])
            folder = pattern_data['folder_name']

            # Get up to 3 sample filenames
            samples = pattern_data['files'][:3]
            sample_text = ", ".join(samples)
            if len(pattern_data['files']) > 3:
                sample_text += f" ... (+{len(pattern_data['files']) - 3} more)"

            tree.insert("", "end", values=(ptype, pname, f"{count:,}", folder, sample_text))
            detected_patterns[pattern_key] = pattern_data

        progress_label.config(text=f"✓ Scan complete! Found {len(filtered_patterns)} patterns in {total_files:,} files")
        scan_progress["value"] = total_files

    def organize_by_patterns():
        if not detected_patterns:
            messagebox.showerror("Error", "Please scan files first")
            return

        target_dir = target_entry.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Please select a valid target directory")
            return

        source_dirs = get_source_dirs()
        if not source_dirs:
            messagebox.showerror("Error", "Please select source directory")
            return

        # Build file map for quick lookup
        file_map = {}
        for source in source_dirs:
            for dirpath, _, files in os.walk(source):
                for f in files:
                    file_map[f] = os.path.join(dirpath, f)

        # Organize files based on detected patterns
        total_moved = 0
        total_files = sum(len(p['files']) for p in detected_patterns.values())
        progress_bar["maximum"] = total_files

        for pattern_data in detected_patterns.values():
            folder_name = pattern_data['folder_name']
            dst_folder = os.path.join(target_dir, folder_name)

            for filename in pattern_data['files']:
                if filename in file_map:
                    src = file_map[filename]
                    move_file(src, dst_folder, filename)
                    total_moved += 1
                    progress_bar["value"] = total_moved
                    if total_moved % 100 == 0:
                        root.update_idletasks()

        messagebox.showinfo("Complete", f"Organized {total_moved:,} files into {len(detected_patterns)} folders")
        scanner_win.destroy()

    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x")

    ttk.Button(button_frame, text="🔍 Scan Files", command=scan_files, width=15).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="📁 Organize by Patterns", command=organize_by_patterns, width=20).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="Close", command=scanner_win.destroy).pack(side="right")

# ==============================
# HELP POPUP
# ==============================
def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("Help - Complete Guide")
    help_win.geometry("750x650"); help_win.minsize(500, 400)
    frame = tk.Frame(help_win); frame.pack(fill=tk.BOTH, expand=True)
    text_area = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y); text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    help_text = """
FILE ORGANIZER - MASTER FILE 3
Complete Feature Guide

🆕 NEW: AUTOMATIC PATTERN SCANNER
• Pattern Scanner – Automatically detects naming patterns in your files
  - Handles millions of files efficiently
  - Detects 6 pattern types:
    1. PREFIX: Common word/letter prefix (Vacation_001 → Vacation)
    2. DELIMITER: Token-based patterns (Project-Alpha-001 → Project-Alpha)
    3. CAMERA: Device tags (IMG, DSC, DSCN, DCS, DCSN, VID, MOV, PXL)
    4. DATE: Date patterns (2024-01-15 → 2024-01)
    5. NUMERIC: Number ranges (0-999, 1000-1999, etc.)
    6. EXTENSION: File type grouping (JPG, PDF, etc.)
  - Shows statistics and sample files for each pattern
  - One-click organize by detected patterns
  - Minimum 2 files required to form a pattern

🟦 Extension-Based
• By Extension – Moves files into folders named by UPPERCASE extension (JPG, PDF, _NOEXT)
• Preview Extension – Shows the plan without moving files

🟨 Alphabet-Based
• Alphabetize – Groups files by first character (A–Z, 0–9, !@#$)
• Preview Alphabet – Shows the plan without moving files
• Numeric (Simple) – Groups by very first character only (digits → 0-9, letters → A-Z)
• Preview Numeric – Shows the plan without moving files

🟪 IMG/DSC Detection
• IMG/DSC Only – Files with IMG/DSC/DSCN/DCS/DCSN tags → matching folders
• Preview IMG/DSC – Shows the plan without moving files

🟩 Smart Pattern Detection
• Smart Pattern – Groups files by detected naming patterns (underscores, dashes, sequences)
• Preview Smart – Shows the plan without moving files
• Smart Pattern + – Same as Smart Pattern but prompts for unknown files and remembers choices
• Preview Smart + – Shows the plan for remembered files only (no prompts)

🟫 Name–Set–File Family
• name-set-file / name_set_file / name set mixed – Strict pattern matching modes
  Folder = SET (numeric values padded to 3 digits)

🟧 Advanced Numeric
• Numerically Advanced – Intelligent bucketing by number ranges (max 500 files per folder)
  - Camera tags → separate folders
  - Groups numeric files into buckets of 1000
  - Merges small/sparse buckets intelligently

🟥 Special Functions
• Organize Zips – Groups multi-part .zip-XX files
• Top-Level Only – Organizes only root-level files
• Extract – Moves files from subfolders to parent
• Scan Sources – Lists all files in Preview panel
• Extract Up… – Moves files up N directory levels

🔧 Pattern Tester
• Pattern Tester – Interactive window to test how filenames will be organized

💾 User Mapping
• Smart Pattern + saves choices to "folder_mappings.json"

📝 General Features
• Drag & Drop – Drag folders to Source field
• Multiple Sources – Comma-separated folders
• Auto-Rename – Duplicates get " (2)" suffix
• Preview – Verify before moving
• Progress Bar – Real-time progress
"""
    text_area.insert(tk.END, help_text); text_area.config(state=tk.DISABLED)

# ==============================
# PATTERN TESTER
# ==============================
def show_pattern_tester():
    win = tk.Toplevel(root)
    win.title("Pattern Tester")
    win.geometry("700x500")
    win.minsize(540, 380)

    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    MODES = {
        "By Extension": by_extension,
        "Alphabetize": by_alphabet,
        "Numeric (Simple)": by_numeric_simple,
        "IMG/DSC": by_img_dsc,
        "Smart Pattern": by_detected,
        "Smart Pattern + (no prompt)": lambda f: by_detected_or_prompt(f, allow_prompt=False),
        "name-set-file": name_set_file_dash,
        "name_set_file": name_set_file_underscore,
        "name set mixed": name_set_file_mixed,
    }

    top = ttk.Frame(frm); top.pack(fill="x")
    ttk.Label(top, text="Mode:").pack(side="left")
    mode = ttk.Combobox(top, state="readonly", values=list(MODES.keys()), width=30)
    mode.current(0)
    mode.pack(side="left", padx=(6,0))

    ttk.Label(frm, text="Enter filenames (one per line):").pack(anchor="w", pady=(8,2))
    txt = tk.Text(frm, height=10, font=("Consolas", 10))
    txt.pack(fill="both", expand=True)
    txt.insert("1.0",
        "Teena-Breathtaking_009.jpg\n"
        "m153-049-123.jpg\n"
        "Teena_Breathtaking-006.jpg\n"
        "IMG0123.JPG\n"
        "alpha-Set12-007.png\n"
        "report.final.pdf\n"
        "12345-file.txt\n"
        "boots35.jpg"
    )

    out = tk.Text(frm, height=10, font=("Consolas", 10), state="disabled")
    out.pack(fill="both", expand=True, pady=(8,0))

    def _run_on_lines(funcs_by_label):
        lines = [l.strip() for l in txt.get("1.0", "end").splitlines() if l.strip()]
        rows = []
        for name in lines:
            for label, func in funcs_by_label.items():
                try:
                    dest = func(name)
                except Exception as e:
                    dest = f"(error: {e})"
                rows.append(f"{name}\n  {label:<30} → {dest or '(skip)'}\n")
        out.config(state="normal"); out.delete("1.0", "end")
        out.insert("1.0", "\n".join(rows) or "(no input)")
        out.config(state="disabled")

    def do_test():
        sel = mode.get()
        _run_on_lines({sel: MODES[sel]})

    def do_test_all():
        _run_on_lines(MODES)

    btnbar = ttk.Frame(frm)
    btnbar.pack(fill="x", pady=(8,0))
    ttk.Button(btnbar, text="Test All", command=do_test_all).pack(side="right")
    ttk.Button(btnbar, text="Test", command=do_test).pack(side="right", padx=(0,6))

# ==============================
# BUTTON DEFINITIONS
# ==============================
def add_section(parent, title: str, buttons: list):
    sect = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
    sect.pack(fill="x", padx=0, pady=(0, 6))
    row = ttk.Frame(sect)
    row.pack(fill="x", padx=6, pady=6)
    for label, cmd in buttons:
        ttk.Button(row, text=label, command=cmd).pack(side="left", padx=(0, 6))
    ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

sections = {
    "🔍 Pattern Scanner (NEW!)": [
        ("🔍 Pattern Scanner",   show_pattern_scanner),
    ],
    "Alphabetize": [
        ("Alphabetize",       lambda: run_organizer(by_alphabet)),
        ("Preview Alphabet",  lambda: run_organizer(by_alphabet, preview=True)),
        ("Numeric (Simple)",  lambda: run_organizer(by_numeric_simple)),
        ("Preview Numeric",   lambda: run_organizer(by_numeric_simple, preview=True)),
    ],
    "By Extension": [
        ("By Extension",       lambda: run_organizer(by_extension)),
        ("Preview Extension",  lambda: run_organizer(by_extension, preview=True)),
    ],
    "IMG/DSC": [
        ("IMG/DSC Only",       lambda: run_organizer(by_img_dsc)),
        ("Preview IMG/DSC",    lambda: run_organizer(by_img_dsc, preview=True)),
    ],
    "name set mixed": [
        ("name set mixed",           lambda: run_organizer(name_set_file_mixed)),
        ("Preview name set mixed",   lambda: run_organizer(name_set_file_mixed, preview=True)),
    ],
    "name-set-file": [
        ("name-set-file",            lambda: run_organizer(name_set_file_dash)),
        ("Preview name-set-file",    lambda: run_organizer(name_set_file_dash, preview=True)),
    ],
    "name_set_file": [
        ("name_set_file",            lambda: run_organizer(name_set_file_underscore)),
        ("Preview name_set_file",    lambda: run_organizer(name_set_file_underscore, preview=True)),
    ],
    "Numerically Advanced": [
        ("Numerically Advanced",       lambda: organize_numerically_advanced(preview=False)),
        ("Preview Numerically Advanced", lambda: organize_numerically_advanced(preview=True)),
    ],
    "Pattern Tester": [
        ("Pattern Tester",           show_pattern_tester),
    ],
    "Smart Pattern": [
        ("Smart Pattern",            lambda: run_organizer(by_detected)),
        ("Preview Smart",            lambda: run_organizer(by_detected, preview=True)),
    ],
    "Smart Pattern +": [
        ("Smart Pattern +",          lambda: run_organizer(lambda f: by_detected_or_prompt(f, allow_prompt=True))),
        ("Preview Smart +",          lambda: run_organizer(lambda f: by_detected_or_prompt(f, allow_prompt=False), preview=True)),
    ],
    "Top-Level Only": [
        ("Top-Level Only",           organize_top_level_only),
    ],
    "Extract & Scan": [
        ("Extract",        extract_all_to_parent),
        ("Scan Sources",   scan_sources),
    ],
    "Organize Zips": [
        ("Organize Zips",            organize_zips),
    ],
}

# ── ACTIONS (scrollable) ───────────────────────────────────────────────────────
actions_frame = ttk.LabelFrame(root, text="Actions", style="Section.TLabelframe")
actions_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
actions_frame.columnconfigure(0, weight=1)
actions_frame.rowconfigure(0, weight=1)

actions_canvas = tk.Canvas(actions_frame, highlightthickness=0)
actions_vsb    = ttk.Scrollbar(actions_frame, orient="vertical", command=actions_canvas.yview)
actions_canvas.configure(yscrollcommand=actions_vsb.set)
actions_canvas.configure(height=280)
actions_canvas.grid(row=0, column=0, sticky="nsew")
actions_vsb.grid(row=0, column=1, sticky="ns")

actions_content = ttk.Frame(actions_canvas)
_actions_window = actions_canvas.create_window((0, 0), window=actions_content, anchor="nw")

def _actions_on_content_configure(event):
    actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))

def _actions_on_canvas_configure(event):
    actions_canvas.itemconfig(_actions_window, width=event.width)

actions_content.bind("<Configure>", _actions_on_content_configure)
actions_canvas.bind("<Configure>", _actions_on_canvas_configure)

def _mw_bind_all():
    actions_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    actions_canvas.bind_all("<Button-4>", _on_mousewheel)
    actions_canvas.bind_all("<Button-5>", _on_mousewheel)

def _mw_unbind_all():
    actions_canvas.unbind_all("<MouseWheel>")
    actions_canvas.unbind_all("<Button-4>")
    actions_canvas.unbind_all("<Button-5>")

def _on_mousewheel(event):
    if hasattr(event, "delta") and event.delta:
        direction = -1 if event.delta > 0 else 1
        actions_canvas.yview_scroll(direction, "units")
        return
    if getattr(event, "num", None) == 4:
        actions_canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:
        actions_canvas.yview_scroll(1, "units")

actions_canvas.bind("<Enter>", lambda e: _mw_bind_all())
actions_canvas.bind("<Leave>", lambda e: _mw_unbind_all())

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=4, pady=(0, 10), sticky="ew")

# Render sections alphabetically (Pattern Scanner first)
for title in sorted(sections.keys(), key=lambda s: (not s.startswith("🔍"), s.lower())):
    if title != "Extract & Scan":
        add_section(actions_content, title, sections[title])
    else:
        sect = ttk.LabelFrame(actions_content, text=title, style="Section.TLabelframe")
        sect.pack(fill="x", padx=0, pady=(0, 6))
        row_btns = ttk.Frame(sect); row_btns.pack(fill="x", padx=6, pady=6)
        for label, cmd in sections[title]:
            ttk.Button(row_btns, text=label, command=cmd).pack(side="left", padx=(0, 6))
        row_up = ttk.Frame(sect); row_up.pack(fill="x", padx=6, pady=6)
        ttk.Label(row_up, text="Levels Up:").pack(side="left", padx=(0, 6))
        levels_entry = ttk.Entry(row_up, width=6)
        levels_entry.insert(0, "1")
        levels_entry.pack(side="left", padx=(0, 6))
        ttk.Button(row_up, text="Extract Up…", command=extract_up_levels).pack(side="left")
        ttk.Separator(actions_content, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

# ── PREVIEW ─────────────────────────────────────────────────────────────────────
preview_frame = ttk.LabelFrame(root, text="Preview", style="Section.TLabelframe")
preview_frame.grid(row=4, column=0, columnspan=3, padx=0, pady=(0,8), sticky="nsew")
v_scroll = ttk.Scrollbar(preview_frame, orient="vertical")
h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal")
preview_text = tk.Text(preview_frame, wrap="none", yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set, font=("Consolas", 10))
v_scroll.config(command=preview_text.yview); h_scroll.config(command=preview_text.xview)
preview_frame.columnconfigure(0, weight=1); preview_frame.rowconfigure(0, weight=1)
preview_text.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=(6,0))
v_scroll.grid(row=0, column=1, sticky="ns", padx=(0,6), pady=(6,0))
h_scroll.grid(row=1, column=0, sticky="ew", padx=(6,0), pady=(0,6))

# ── FOOTER ─────────────────────────────────────────────────────────────────────
footer = ttk.Frame(root); footer.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,6))
footer.columnconfigure(0, weight=1); footer.columnconfigure(1, weight=1); footer.columnconfigure(2, weight=1)
ttk.Button(footer, text="Clear Preview", command=lambda: preview_text.delete("1.0", tk.END)).grid(row=0, column=0, pady=2)
ttk.Button(footer, text="Help", command=show_help).grid(row=0, column=1, pady=2)

# DnD Support
if dnd_available:
    def drop(event):
        paths = [p.strip('{}') for p in event.data.split() if os.path.isdir(p.strip('{}'))]
        if paths:
            source_entry.delete(0, tk.END)
            source_entry.insert(0, ', '.join(paths))
    source_entry.drop_target_register(DND_FILES)
    source_entry.dnd_bind('<<Drop>>', drop)

# Resize behavior
root.grid_rowconfigure(2, weight=1)  # Actions
root.grid_rowconfigure(4, weight=1)  # Preview
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# START GUI
root.mainloop()
