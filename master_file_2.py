# ==============================
# FILE ORGANIZER - CLEAN & FIXED
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

root.title("File Organizer with Pattern Detection")

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
levels_entry = None  # will be created in the “Extract Up” section

# ── HEADER ─────────────────────────────────────────────────────────────────────
header = ttk.Frame(root, padding=(8, 8))
header.grid(row=0, column=0, columnspan=3, sticky="ew")
ttk.Label(header, text="File Organizer", style="Title.TLabel").pack(side="left")

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
    target_root = (target_entry.get() or "").strip()  # micro-polish: read once
    all_files = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for file in files:
                src = os.path.join(dirpath, file)

                # logic returns RELATIVE folder name under target
                rel_folder = logic_func(file)
                if not rel_folder:
                    continue

                dst_folder = os.path.join(target_root, rel_folder)
                dst = os.path.join(dst_folder, file)

                # Skip no-ops
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

    # Build plan
    logic = lambda fname: folder_logic(fname)  # returns RELATIVE folder name under target
    plan = collect_files(source_dirs, logic)

    if preview:
        filtered = [(src, os.path.relpath(dst_folder, target_dir), fname) for src, dst_folder, fname in plan]
        show_preview(filtered)
        return

    total = len(plan)
    progress_bar["maximum"] = total
    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        move_file(src, dst_folder, fname)
        update_progress(i, total)

# ==============================
# LOGIC FUNCTIONS
# ==============================
def by_extension(filename):
    ext = os.path.splitext(filename)[1][1:]  # remove dot
    return ext.upper() if ext else "_NOEXT"

def by_alphabet(filename):
    first = filename[0].upper()
    if first.isalpha(): return first
    if first.isdigit(): return "0-9"
    return "!@#$"

def by_numeric(filename):
    name = filename.lstrip()
    if not name:
        return "!@#$"
    ch = name[0]
    # Replace Windows-invalid folder name characters with "_"
    if ch in '\\/:*?"<>|':
        return "!@#$"
    if ch.isdigit():
        return ch
    if ch.isalpha():
        return ch.upper()
    return ch

def by_img_dsc(filename):
    return extract_img_tag(filename)  # None → skipped

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
# SPECIAL FUNCTIONS (not via run_organizer)
# ==============================
# ───────── name–set–file FAMILY (strict patterns, SET can be text or number) ─────────
# Rules:
# • name-set-file        : ONLY matches ANYTHING-SET-FILENUMBER
# • name_set_file        : ONLY matches ANYTHING_SET_FILENUMBER
# • name set mixed       : ONLY matches ANYTHING <D1> SET <D2> FILENUMBER, D1/D2 ∈ {'-','_'}
#   - Folder = SET (if numeric → zero-pad to 3; if has letters → as-is)
#   - Mixed mode: if D1 != D2 → prefix D1 and suffix D2 to the folder (e.g., name-049_123 → -049_)
#   - Non-matching filenames are skipped

def _nsf_tidy_base(filename):
    base, _ = os.path.splitext(filename)
    # strip trailing " (123)" copies and trim edges
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base).strip().rstrip(' .')
    return base

def _nsf_pad_if_numeric(token, pad=3):
    return token.zfill(pad) if token.isdigit() and len(token) < pad else token

def name_set_file_dash(filename):
    """
    Match ONLY: ANYTHING-SET-FILENUMBER
      - SET: [A-Za-z0-9]+
      - FILENUMBER: digits
    Folder = SET (numeric padded to 3; text as-is)
    """
    base = _nsf_tidy_base(filename)
    m = re.match(r'^.+-(?P<set>[A-Za-z0-9]+)-(?P<file>\d+)$', base)
    if not m:
        return None
    set_token = m.group('set')
    return _nsf_pad_if_numeric(set_token, 3)

def name_set_file_underscore(filename):
    """
    Match ONLY: ANYTHING_SET_FILENUMBER
      - SET: [A-Za-z0-9]+
      - FILENUMBER: digits
    Folder = SET (numeric padded to 3; text as-is)
    """
    base = _nsf_tidy_base(filename)
    m = re.match(r'^.+_(?P<set>[A-Za-z0-9]+)_(?P<file>\d+)$', base)
    if not m:
        return None
    set_token = m.group('set')
    return _nsf_pad_if_numeric(set_token, 3)

def name_set_file_mixed(filename):
    """
    Match ONLY: ANYTHING <D1> SET <D2> FILENUMBER, where D1/D2 ∈ {'-','_'}
    Folder base = SET (numeric padded to 3; text as-is).
    If D1 != D2, decorate folder as: D1 + folder + D2. If equal, no decoration.
    """
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

# ───────── Extract Up N Levels ─────────
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
# ───────── End Extract Up N Levels ─────────

# ==============================
# HELP POPUP
# ==============================
def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("Help - Button Guide")
    help_win.geometry("600x500"); help_win.minsize(400, 300)
    frame = tk.Frame(help_win); frame.pack(fill=tk.BOTH, expand=True)
    text_area = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y); text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    help_text = """

🟦 Extension-Based
• By Extension – Recursively moves files into folders named by UPPERCASE extension (e.g., JPG, PDF, _NOEXT).
• Preview Extension – Show the plan without moving files.

🟨 Alphabet-Based
• Alphabetize – Groups files by first character (A–Z, 0–9, !@#$).
• Preview Alphabet – Show the plan without moving files.
• Numeric – Groups files by the very first character only. 
   Digits go into folders 0–9, letters into A–Z, symbols into their own folder.
• Preview Numeric – Show the plan without moving files.

🟪 IMG/DSC
• IMG/DSC Only – Files containing IMG/DSC/DSCN/DCS/DCSN go to matching folders.
• Preview IMG/DSC – Show the plan without moving files.

🟩 Smart Detection
• Smart Pattern – Groups files by detected naming patterns (underscores, dashes, sequences).
• Preview Smart – Show the plan without moving files.
• Smart Pattern + – As above, but prompts if unknown and remembers your choice.
• Preview Smart + – Show the plan for Smart+ (no prompts), without moving files.

🟫 Name–Set–File (separate logic family)
These modes expect NAME–SET–FILENUMBER where FILENUMBER is digits. The SET can be
letters or numbers (alphanumeric). Folder = SET. If SET is numeric, it’s zero-padded
to 3 (e.g., 7 → 007). Non-matching files are skipped.

• name-set-file — Hyphen mode: ANYTHING-SET-FILENUMBER
  Examples:
    - m153-049-123.jpg → 049
    - alpha-Teena-007.png → Teena
• Preview name-set-file — Show the plan.

• name_set_file — Underscore mode: ANYTHING_SET_FILENUMBER
  Examples:
    - Teena_Breathtaking_009.jpg → Breathtaking
    - proj_Set12_5.png → Set12
• Preview name_set_file — Show the plan.

• name set mixed — Mixed separators: ANYTHING <D1> SET <D2> FILENUMBER (D1/D2 ∈ {'-','_'})
  Folder = SET (text as-is; numeric padded). If D1 != D2, decorate: prefix D1 and suffix D2.
  Examples:
    - Teena-Breathtaking_009.jpg → -Breathtaking_
    - Teena_Breathtaking-006.jpg → _Breathtaking-
    - name-049_123.jpg → -049_
    - name_Set12_005.png → -Set12_
    - alpha-Set-123.jpg → Set        (same delimiters, no decoration)
• Preview name set mixed — Show the plan.

🟥 Special Functions
• Organize Zips – Groups multi-part .zip-XX files into folders by base name.
• Top-Level Only – Organizes only files in the top-level of the source.
• Extract – Moves all files from subfolders into the parent, cleaning empty folders.
• Extract Up… – Move files up N directory levels.
• Extract & Scan – “Extract” moves all files from subfolders to the parent (then cleans empties).
  “Scan Sources” lists all files in the selected Source folder(s) in the Preview panel.
"""
    text_area.insert(tk.END, help_text); text_area.config(state=tk.DISABLED)

# ==============================
# BUTTON DEFINITIONS (sectioned, alphabetical)
# ==============================

def add_section(parent, title: str, buttons: list):
    """Create a labeled section with its buttons on one row, then a separator."""
    sect = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
    sect.pack(fill="x", padx=0, pady=(0, 6))
    row = ttk.Frame(sect)
    row.pack(fill="x", padx=6, pady=6)
    for label, cmd in buttons:
        ttk.Button(row, text=label, command=cmd).pack(side="left", padx=(0, 6))
    ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

def show_pattern_tester():
    win = tk.Toplevel(root)
    win.title("Pattern Tester")
    win.geometry("680x460")
    win.minsize(540, 380)

    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    # --- Modes to test (no prompts in tester) ---
    MODES = {
        "By Extension": by_extension,
        "Alphabetize": by_alphabet,
        "IMG/DSC": by_img_dsc,
        "Smart Pattern": by_detected,
        "Smart Pattern + (no prompt)": lambda f: by_detected_or_prompt(f, allow_prompt=False),
        "name-set-file": name_set_file_dash,
        "name_set_file": name_set_file_underscore,
        "name set mixed": name_set_file_mixed,
    }

    # Input area
    top = ttk.Frame(frm); top.pack(fill="x")
    ttk.Label(top, text="Mode:").pack(side="left")
    mode = ttk.Combobox(top, state="readonly", values=list(MODES.keys()), width=28)
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
        "report.final.pdf"
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
                rows.append(f"{name}\n  {label:<24} → {dest or '(skip)'}\n")
        out.config(state="normal"); out.delete("1.0", "end")
        out.insert("1.0", "\n".join(rows) or "(no input)")
        out.config(state="disabled")

    def do_test():
        sel = mode.get()
        _run_on_lines({sel: MODES[sel]})

    def do_test_all():
        _run_on_lines(MODES)

    # Button bar (pinned)
    btnbar = ttk.Frame(frm)
    btnbar.pack(fill="x", pady=(8,0))
    ttk.Button(btnbar, text="Test All", command=do_test_all).pack(side="right")
    ttk.Button(btnbar, text="Test", command=do_test).pack(side="right", padx=(0,6))

# --- Sections & Buttons (define logically; we'll sort by section title) ---
sections = {
    "Alphabetize": [
    ("Alphabetize",       lambda: run_organizer(by_alphabet)),
    ("Preview Alphabet",  lambda: run_organizer(by_alphabet, preview=True)),
    ("Numeric",           lambda: run_organizer(by_numeric)),
    ("Preview Numeric",   lambda: run_organizer(by_numeric, preview=True)),
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
    # ✅ Combined section
    "Extract & Scan": [
        ("Extract",        extract_all_to_parent),
        ("Scan Sources",   scan_sources),
    ],
    "Organize Zips": [
        ("Organize Zips",            organize_zips),
    ],
}

# ── ACTIONS (scrollable) ───────────────────────────────────────────────────────
# A titled LabelFrame that contains a Canvas+Scrollbar. Inside the Canvas lives
# a normal Frame ("actions_content") where we add each section.
actions_frame = ttk.LabelFrame(root, text="Actions", style="Section.TLabelframe")
actions_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
actions_frame.columnconfigure(0, weight=1)
actions_frame.rowconfigure(0, weight=1)

# Canvas + vertical scrollbar
actions_canvas = tk.Canvas(actions_frame, highlightthickness=0)
actions_vsb    = ttk.Scrollbar(actions_frame, orient="vertical", command=actions_canvas.yview)
actions_canvas.configure(yscrollcommand=actions_vsb.set)

# Give the canvas a comfortable height so it doesn't grow the whole window
actions_canvas.configure(height=280)
actions_canvas.grid(row=0, column=0, sticky="nsew")
actions_vsb.grid(row=0, column=1, sticky="ns")

# Inner content frame inside the canvas (this is where sections are packed)
actions_content = ttk.Frame(actions_canvas)
_actions_window = actions_canvas.create_window((0, 0), window=actions_content, anchor="nw")

# Keep scrollregion and width in sync
def _actions_on_content_configure(event):
    actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))

def _actions_on_canvas_configure(event):
    # Stretch inner frame to the canvas width
    actions_canvas.itemconfig(_actions_window, width=event.width)

actions_content.bind("<Configure>", _actions_on_content_configure)
actions_canvas.bind("<Configure>", _actions_on_canvas_configure)

# Mouse wheel support (Windows/Mac/Linux) only while cursor is over the canvas
def _mw_bind_all():
    actions_canvas.bind_all("<MouseWheel>", _on_mousewheel)   # Windows/Mac
    actions_canvas.bind_all("<Button-4>", _on_mousewheel)     # Linux up
    actions_canvas.bind_all("<Button-5>", _on_mousewheel)     # Linux down

def _mw_unbind_all():
    actions_canvas.unbind_all("<MouseWheel>")
    actions_canvas.unbind_all("<Button-4>")
    actions_canvas.unbind_all("<Button-5>")

def _on_mousewheel(event):
    # Windows/Mac
    if hasattr(event, "delta") and event.delta:
        direction = -1 if event.delta > 0 else 1
        actions_canvas.yview_scroll(direction, "units")
        return
    # Linux (Button-4 up / Button-5 down)
    if getattr(event, "num", None) == 4:
        actions_canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:
        actions_canvas.yview_scroll(1, "units")

actions_canvas.bind("<Enter>", lambda e: _mw_bind_all())
actions_canvas.bind("<Leave>", lambda e: _mw_unbind_all())
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=4, pady=(0, 10), sticky="ew")

# --- Render sections alphabetically (case-insensitive) into actions_content ---
for title in sorted(sections.keys(), key=lambda s: s.lower()):
    if title != "Extract & Scan":
        add_section(actions_content, title, sections[title])
    else:
        # Custom section with buttons + the Extract Up row
        sect = ttk.LabelFrame(actions_content, text=title, style="Section.TLabelframe")
        sect.pack(fill="x", padx=0, pady=(0, 6))

        # Row 1: the normal buttons (Extract, Scan Sources)
        row_btns = ttk.Frame(sect); row_btns.pack(fill="x", padx=6, pady=6)
        for label, cmd in sections[title]:
            ttk.Button(row_btns, text=label, command=cmd).pack(side="left", padx=(0, 6))

        # Row 2: the Extract Up composite (label + entry + button)
        row_up = ttk.Frame(sect); row_up.pack(fill="x", padx=6, pady=6)
        ttk.Label(row_up, text="Levels Up:").pack(side="left", padx=(0, 6))
        levels_entry = ttk.Entry(row_up, width=6)
        levels_entry.insert(0, "1")
        levels_entry.pack(side="left", padx=(0, 6))
        ttk.Button(row_up, text="Extract Up…", command=extract_up_levels).pack(side="left")

        # Separator after the whole section
        ttk.Separator(actions_content, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

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
root.grid_rowconfigure(2, weight=1)  # Actions (scrollable)
root.grid_rowconfigure(4, weight=1)  # Preview
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# START GUI
root.mainloop()
