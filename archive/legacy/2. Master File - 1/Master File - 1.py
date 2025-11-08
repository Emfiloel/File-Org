# ==============================
# FILE ORGANIZER - REFACTORED
# ==============================
# Author: Refactored for clarity and simplicity
# Function: Organize files by extension, name pattern, alphabet, number, and smart logic
# UI: Tkinter with DnD support (optional)
# ==============================

import os
import re
import shutil
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

root.title("File Organizer with Pattern Detection")
# (call load_mappings() later, after it's defined)

# ── START: THEME & GLOBAL STYLES ───────────────────────────────────────────────
from tkinter import font as tkfont

style = ttk.Style()
# pick a clean built-in theme
for t in ("clam", "vista", "xpnative", "default"):
    try:
        style.theme_use(t)
        break
    except Exception:
        pass

# App font palette
FONT_BASE   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_TITLE  = ("Segoe UI Semibold", 12)

root.option_add("*Font", FONT_BASE)
root.configure(padx=10, pady=10)

# Button & entry cosmetics
style.configure("TButton", padding=6)
style.map("TButton",
    relief=[("pressed", "sunken"), ("active", "raised")])
style.configure("TEntry", padding=4)
style.configure("TLabel", padding=2)
style.configure("Title.TLabel", font=FONT_TITLE)

# Progressbar a bit thicker
style.configure("TProgressbar", thickness=12)

# Frame styles
style.configure("Card.TFrame", background=style.lookup("TFrame", "background"))
style.configure("Section.TLabelframe.Label", font=FONT_TITLE)
# ── END: THEME & GLOBAL STYLES ─────────────────────────────────────────────────

# ── START: HEADER ──────────────────────────────────────────────────────────────
header = ttk.Frame(root, style="Card.TFrame", padding=(8, 8))
header.grid(row=0, column=0, columnspan=3, sticky="ew")
ttk.Label(header, text="File Organizer", style="Title.TLabel").pack(side="left")
# ── END: HEADER ────────────────────────────────────────────────────────────────

# ── START: SOURCE/TARGET SECTION ───────────────────────────────────────────────
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
# ── END: SOURCE/TARGET SECTION ─────────────────────────────────────────────────

# ==============================
# CORE HELPERS
# ==============================
def get_source_dirs():
    return [d.strip() for d in source_entry.get().split(',') if os.path.isdir(d.strip())]

def move_file(src, dst_folder, filename):
    print(f"[MOVE DEBUG] src: {src}")
    print(f"[MOVE DEBUG] dst_folder: {dst_folder}")
    print(f"[MOVE DEBUG] dst: {os.path.join(dst_folder, filename)}")

    os.makedirs(dst_folder, exist_ok=True)
    try:
        shutil.move(src, os.path.join(dst_folder, filename))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move {filename}: {e}")

def update_progress(index, total):
    progress_bar["value"] = index
    root.update_idletasks()
    if index == total:
        messagebox.showinfo("Info", "Operation completed successfully")

def show_preview(preview_items):
    preview_text.delete("1.0", tk.END)
    for src, folder, filename in preview_items:
        preview_text.insert(tk.END, f"{filename} → {folder}/\n")

def smart_title(text):
    return '_'.join(w if w.isupper() else w.capitalize() for w in text.split('_'))

# === START: User mapping persistence (global) ===
import json

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
    """Stable key for remembering a folder: lowercased base name with noisy suffixes removed."""
    base, _ = os.path.splitext(filename)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base)           # remove "(123)" suffix
    base = re.sub(r'(?<=[\-_])\d+[A-Za-z]?$', '', base)     # remove only final -123 / _123r
    base = base.strip().lower()
    return base
# === END: User mapping persistence (global) ===

# Load saved folder choices (global)
load_mappings()

# ==============================
# FILENAME PATTERN DETECTION
# ==============================

def detect_folder_name(filename):
    base, _ = os.path.splitext(filename)
    # Remove trailing " (123)" or "-(123)" or "_(123)" and any spaces before it, then trim trailing spaces/dots
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base).rstrip(' .')
    # Remove only the final -number or _number + optional letter (e.g., -01r, -02, _03a), keep earlier numeric parts
    base = re.sub(r'(?<=[\-_])\d+[A-Za-z]?$', '', base).rstrip(' _-.')

    m = re.search(r'([\-_]?)(\d+)$', base)
    if m:
        pre = base[:m.start()]
        delim = m.group(1)
    else:
        pre = base
        delim = ''

    if '_' in pre and '-' not in pre:
        folder = smart_title(pre)
        if delim == '-':
            folder += '[-]'
    elif '-' in pre and '_' not in pre:
        folder = '-'.join(w.capitalize() for w in pre.split('-'))
        if delim == '_':
            folder += '[_]'
    elif '-' in pre and '_' in pre:
        folder = '-'.join(w.capitalize() for w in pre.split('-')) if pre.rfind('-') > pre.rfind('_') else smart_title(pre)
        if delim == '_':
            folder += '[_]'
        elif delim == '-':
            folder += '[-]'
    else:
        m_simple = re.match(r"([A-Za-z]+)\d+$", pre)
        if m_simple:
            folder = m_simple.group(1).capitalize()
        else:
            folder = None  # no confident rule → trigger prompt (via by_detected_or_prompt)

    # Always strip trailing space/dot on final folder name (Windows-safe)
    if folder is not None:
        folder = folder.rstrip(' .')
    return folder

# ==============================
# IMG/DSC DETECTION
# ==============================

def extract_img_tag(filename):
    # Match tags even if stuck to numbers (e.g., "77875DSC" or "IMG1234")
    match = re.search(r"(IMG|DSC|DSCN|DCS|DCSN)(?=\d|_|\.|$)", filename, re.IGNORECASE)
    return match.group(1).upper() if match else None

# ==============================
# FILE ORGANIZATION MODES
# ==============================
def collect_files(source_dirs, logic_func):
    all_files = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for file in files:
                src = os.path.join(dirpath, file)
                dst_folder = logic_func(file, src)
                if not dst_folder:
                    continue
                dst = os.path.join(dst_folder, file)
                if os.path.exists(dst) or os.path.abspath(src) == os.path.abspath(dst):
                    continue
                all_files.append((src, dst_folder, file))
    return all_files

def run_organizer(logic_func, preview=False):
    source_dirs = get_source_dirs()
    target_dir = (target_entry.get() or "").strip()  # strip hidden spaces/newlines

    if not target_dir or not os.path.isdir(target_dir):
        messagebox.showerror("Error", "Target directory not set or invalid.")
        return

    # Disallow target living inside any source (avoids moving-while-walking issues)
    for s in source_dirs:
        try:
            if os.path.commonpath([os.path.abspath(target_dir), os.path.abspath(s)]) == os.path.abspath(s):
                messagebox.showerror(
                    "Error",
                    f"Target folder cannot be inside a source folder:\nSource: {s}\nTarget: {target_dir}"
                )
                return
        except Exception:
            pass

    logic = lambda f, s: os.path.join(target_dir, logic_func(f))
    all_files = collect_files(source_dirs, logic)

    if preview:
        # all_files already contains only matches (dst_folder truthy)
        filtered = [(src, os.path.relpath(dst, target_dir), fname)
                    for src, dst, fname in all_files]
        show_preview(filtered)
        return

    total = len(all_files)
    progress_bar["maximum"] = total
    for i, (src, dst, fname) in enumerate(all_files, 1):
        move_file(src, dst, fname)
        update_progress(i, total)
        
# ==============================
# ORGANIZE LOGIC FUNCTIONS
# ==============================
def by_extension(filename):
    return os.path.splitext(filename)[1][1:].lower()

def by_alphabet(filename):
    first = filename[0].upper()
    if first.isalpha(): return first
    if first.isdigit(): return "0-9"
    return os.path.join("!@#$", first)

def by_img_dsc(filename):
    tag = extract_img_tag(filename)
    return tag if tag else None

def by_detected(filename):
    return detect_folder_name(filename)

# === START: Smart Pattern with prompt + memory ===
def by_detected_or_prompt(filename, allow_prompt=True):
    # 1) Try user memory first (global)
    key = make_key(filename)
    if key in USER_MAP:
        return USER_MAP[key]

    # 2) Try regex-based detection
    folder = detect_folder_name(filename)
    if folder:
        return folder

    # 3) Unknown and allowed → ask user once, then remember globally
    if allow_prompt:
        answer = simpledialog.askstring(
            "Unclassified file",
            f"Enter folder name for:\n\n{filename}\n\nThis choice will be remembered for similar files.\n(Target root: {target_entry.get()})"
        )
        if answer:
            USER_MAP[key] = answer.strip()
            save_mappings()
            return USER_MAP[key]

    return None
# === END: Smart Pattern with prompt + memory ===

def organize_zips():
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    pattern = re.compile(r'(.+)\.zip-\d+')
    all_files = []

    for source_dir in source_dirs:
        for filename in os.listdir(source_dir):
            match = pattern.match(filename)
            if match:
                src = os.path.join(source_dir, filename)
                dst_folder = os.path.join(target_dir, match.group(1))
                dst = os.path.join(dst_folder, filename)
                if os.path.exists(dst):
                    continue
                all_files.append((src, dst_folder, filename))

    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)

def organize_top_level_only():
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []

    for source_dir in source_dirs:
        for filename in os.listdir(source_dir):
            src = os.path.join(source_dir, filename)
            if not os.path.isfile(src):
                continue  # Skip folders or nested content

            folder = detect_folder_name(filename)
            if folder is None:
                folder = "Unsorted"

            dst_folder = os.path.join(target_dir, folder)
            dst = os.path.join(dst_folder, filename)

            if os.path.exists(dst):
                continue  # skip duplicates
            if os.path.abspath(src) != os.path.abspath(dst):
                all_files.append((src, dst_folder, filename))

    total_files = len(all_files)
    if total_files == 0:
        messagebox.showinfo("Top-Level", "No top-level files found to organize.")
        return

    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)
        
# ==============================
# EXTRACT FILES FROM SUBFOLDERS
# ==============================
def extract_all_to_parent():
    source_dirs = get_source_dirs()
    all_files = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            if os.path.abspath(dirpath) == os.path.abspath(source):
                continue
            for f in files:
                src = os.path.join(dirpath, f)
                dst = os.path.join(source, f)
                if not os.path.exists(dst):
                    all_files.append((src, dst))
    if not all_files:
        messagebox.showinfo("Extract", "No files found in subfolders.")
        return

    total = len(all_files)
    progress_bar["maximum"] = total
    for i, (src, dst) in enumerate(all_files, 1):
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
        except Exception:
            pass
        update_progress(i, total)

    for source in source_dirs:
        for dirpath, _, files in os.walk(source, topdown=False):
            if dirpath != source and not os.listdir(dirpath):
                try: os.rmdir(dirpath)
                except: pass

    messagebox.showinfo("Extract Complete", f"Moved {total} file(s) and cleaned empty folders.")

# ───────── START: Extract Up N Levels ─────────
def extract_up_levels():
    """
    Move files up N directory levels from their current path,
    reading N from the small 'Levels Up' entry in the UI.
    """
    try:
        levels = int(levels_entry.get())
        if levels < 1:
            raise ValueError
    except Exception:
        messagebox.showerror("Extract Up", "Please enter a valid number of levels (>=1).")
        return

    source_dirs = get_source_dirs()
    if not source_dirs:
        messagebox.showerror("Extract Up", "Please select at least one source folder.")
        return

    all_moves = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for fname in files:
                src = os.path.join(dirpath, fname)

                # Compute destination 'levels' up
                dest_dir = dirpath
                for _ in range(levels):
                    dest_dir = os.path.dirname(dest_dir)

                # Clamp to the source root if we went too far
                if len(os.path.abspath(dest_dir)) < len(os.path.abspath(source)):
                    dest_dir = source

                dst = os.path.join(dest_dir, fname)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue
                if os.path.exists(dst):
                    continue

                all_moves.append((src, dst))

    if not all_moves:
        messagebox.showinfo("Extract Up", "No files found to move for the chosen level(s).")
        return

    progress_bar["maximum"] = len(all_moves)
    moved, skipped = 0, 0
    for i, (src, dst) in enumerate(all_moves, 1):
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved += 1
        except Exception:
            skipped += 1
        update_progress(i, len(all_moves))

    removed_dirs = 0
    for source in source_dirs:
        for dpath, _, _ in os.walk(source, topdown=False):
            if os.path.abspath(dpath) == os.path.abspath(source):
                continue
            if not os.listdir(dpath):
                try:
                    os.rmdir(dpath)
                    removed_dirs += 1
                except Exception:
                    pass

    messagebox.showinfo(
        "Extract Up Complete",
        f"Moved {moved} file(s), skipped {skipped} duplicate(s).\n"
        f"Removed {removed_dirs} empty folder(s)."
    )
# ───────── END: Extract Up N Levels ─────────
# === START: Scrollable Help Popup ===
def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("Help - Button Guide")
    help_win.geometry("600x500")  # Starting size (resizable)
    help_win.minsize(400, 300)

    # Frame for text + scrollbar
    frame = tk.Frame(help_win)
    frame.pack(fill=tk.BOTH, expand=True)

    text_area = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    help_text = """
🟦 Extension-Based
• By Extension – Moves files into folders named after their file extension (e.g., JPG, PDF).
• Preview Extension – Shows what would happen without moving files.

🟨 Alphabet-Based
• Alphabetize – Groups files into folders by first character (A–Z, 0–9, or special symbols).
• Preview Alphabet – Preview of alphabetical grouping.

🟪 IMG/DSC
• IMG/DSC Only – Moves files containing IMG, DSC, DSCN, DCS, DCSN into matching folders.
• Preview IMG/DSC – Preview of IMG/DSC sorting.

🟩 Smart Detection
• Smart Pattern – Groups files by detected naming patterns (underscores, dashes, sequences).
• Preview Smart – Shows detected pattern groups without moving.
• Smart Pattern + – As above, but prompts if unknown and remembers your choice.
• Preview Smart + – Shows only known/remembered groups, no prompts.

🟥 Special Functions
• Organize Zips – Groups multi-part .zip-XX files into folders by base name.
• Top-Level Only – Organizes only files in the top-level of the source folder.
• Extract – Moves all files from subfolders into the parent, cleaning empty folders.
"""

    text_area.insert(tk.END, help_text)
    text_area.config(state=tk.DISABLED)  # Read-only

# ==============================
# BUTTON DEFINITIONS (Grouped)
# ==============================
buttons = [
    # 🟦 Extension-Based
    ("By Extension", lambda: run_organizer(by_extension)),
    ("Preview Extension", lambda: run_organizer(by_extension, preview=True)),

    # 🟨 Alphabet-Based
    ("Alphabetize", lambda: run_organizer(by_alphabet)),
    ("Preview Alphabet", lambda: run_organizer(by_alphabet, preview=True)),

    # 🟪 IMG/DSC
    ("IMG/DSC Only", lambda: run_organizer(by_img_dsc)),
    ("Preview IMG/DSC", lambda: run_organizer(by_img_dsc, preview=True)),

    # 🟩 Smart Detection
    ("Smart Pattern", lambda: run_organizer(by_detected)),
    ("Preview Smart", lambda: run_organizer(by_detected, preview=True)),

    # Smart Detection with prompt + memory (global mapping)
    ("Smart Pattern +", lambda: run_organizer(lambda f: by_detected_or_prompt(f, allow_prompt=True))),
    ("Preview Smart +", lambda: run_organizer(lambda f: by_detected_or_prompt(f, allow_prompt=False), preview=True)),

    # 🟥 Special Functions
    ("Organize Zips", organize_zips),
    ("Top-Level Only", organize_top_level_only),
    ("Extract", extract_all_to_parent),
    ("__EXTRACT_UP_WIDGET__", None),  # composite widget goes here
]

# ==============================
# BUTTONS + LAYOUT (no overlap)
# ==============================
# ── START: ACTIONS SECTION ─────────────────────────────────────────────────────
actions_box = ttk.LabelFrame(root, text="Actions", style="Section.TLabelframe")
actions_box.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0,8))
actions_box.columnconfigure(0, weight=1)
actions_box.columnconfigure(1, weight=1)
actions_box.columnconfigure(2, weight=1)
start_row = 0  # now relative to actions_box
cols = 3
# ── END: ACTIONS SECTION ───────────────────────────────────────────────────────

for i, (label, cmd) in enumerate(buttons):
    r = start_row + i // cols
    c = i % cols

    if label == "__EXTRACT_UP_WIDGET__":
        levels_frame = ttk.Frame(actions_box)
        ttk.Label(levels_frame, text="Levels Up:").pack(side=tk.LEFT, padx=(0, 5))
        levels_entry = ttk.Entry(levels_frame, width=6)
        levels_entry.insert(0, "1")
        levels_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(levels_frame, text="Extract Up…", command=extract_up_levels).pack(side=tk.LEFT)
        levels_frame.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
    else:
        ttk.Button(actions_box, text=label, command=cmd).grid(row=r, column=c, padx=5, pady=5, sticky="ew")

# Compute rows below the last button row
last_button_row = start_row + (len(buttons) - 1) // cols
progress_row = 3  # on root, placed after actions_box row (which is row=2)
preview_row  = 4
clear_row    = 5
help_row     = 6

# ── START: PROGRESS ────────────────────────────────────────────────────────────
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.grid(row=progress_row, column=0, columnspan=3, padx=4, pady=(0,10), sticky="ew")
# ── END: PROGRESS ──────────────────────────────────────────────────────────────

# ── START: PREVIEW ─────────────────────────────────────────────────────────────
preview_frame = ttk.LabelFrame(root, text="Preview", style="Section.TLabelframe")
preview_frame.grid(row=preview_row, column=0, columnspan=3, padx=0, pady=(0,8), sticky="nsew")

v_scroll = ttk.Scrollbar(preview_frame, orient="vertical")
h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal")

preview_text = tk.Text(
    preview_frame,
    wrap="none",
    yscrollcommand=v_scroll.set,
    xscrollcommand=h_scroll.set,
    font=("Consolas", 10)
)

v_scroll.config(command=preview_text.yview)
h_scroll.config(command=preview_text.xview)

preview_frame.columnconfigure(0, weight=1)
preview_frame.rowconfigure(0, weight=1)

preview_text.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=(6,0))
v_scroll.grid(row=0, column=1, sticky="ns", padx=(0,6), pady=(6,0))
h_scroll.grid(row=1, column=0, sticky="ew", padx=(6,0), pady=(0,6))
# ── END: PREVIEW ───────────────────────────────────────────────────────────────

# ── START: FOOTER BUTTONS ──────────────────────────────────────────────────────
footer = ttk.Frame(root)
footer.grid(row=clear_row, column=0, columnspan=3, sticky="ew", pady=(0,6))
footer.columnconfigure(0, weight=1)
footer.columnconfigure(1, weight=1)
footer.columnconfigure(2, weight=1)

ttk.Button(footer, text="Clear Preview", command=lambda: preview_text.delete("1.0", tk.END)).grid(row=0, column=0, pady=2)
ttk.Button(footer, text="Help", command=show_help).grid(row=0, column=1, pady=2)
# you could add a "Settings" or "About" on column=2 later

# Make the whole window grow nicely
root.grid_rowconfigure(preview_row, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
# ── END: FOOTER BUTTONS ────────────────────────────────────────────────────────

# DnD Support
if dnd_available:
    def drop(event):
        paths = [p.strip('{}') for p in event.data.split() if os.path.isdir(p.strip('{}'))]
        if paths:
            source_entry.delete(0, tk.END)
            source_entry.insert(0, ', '.join(paths))
    source_entry.drop_target_register(DND_FILES)
    source_entry.dnd_bind('<<Drop>>', drop)

# ==============================
# START GUI
# ==============================
root.mainloop()
