import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

def get_source_dirs():
    dirs = [d.strip() for d in source_entry.get().split(',') if d.strip()]
    return [d for d in dirs if os.path.isdir(d)]

def select_source_directory():
    directory_paths = filedialog.askdirectory(mustexist=True)
    if directory_paths:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, directory_paths)

def select_target_directory():
    directory_path = filedialog.askdirectory()
    target_entry.delete(0, tk.END)
    target_entry.insert(0, directory_path)

def move_file(file_path, target_folder, filename):
    os.makedirs(target_folder, exist_ok=True)
    try:
        shutil.move(file_path, os.path.join(target_folder, filename))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move {filename}: {e}")

def update_progress(index, total_files):
    progress_bar["value"] = index
    root.update_idletasks()
    if index == total_files:
        messagebox.showinfo("Info", "Operation completed successfully")

# === Pattern Detection ===
def detect_pattern_folder_name(filename):
    base, _ = os.path.splitext(filename)
    m_paren = re.search(r'([_-])\((\d+)\)$', base)
    if m_paren:
        base = base[:m_paren.start()]
    else:
        base = re.sub(r'\(\d+\)$', '', base)
    m = re.search(r'([_-]?)(\d+)$', base)
    if m:
        pre = base[:m.start()]
        num_delim = m.group(1)
    else:
        pre = base
        num_delim = ''
    if '_' in pre and '-' not in pre:
        folder = '_'.join(w if w.isupper() else w.capitalize() for w in pre.split('_'))
        if num_delim == '-':
            folder += '[-]'
        return folder
    elif '-' in pre and '_' not in pre:
        folder = '-'.join(w.capitalize() if not w.isupper() else w for w in pre.split('-'))
        if num_delim == '_':
            folder += '[_]'
        return folder
    elif '_' in pre and '-' in pre:
        us = pre.rfind('_')
        ds = pre.rfind('-')
        if ds > us:
            folder = '-'.join(w.capitalize() if not w.isupper() else w for w in pre.split('-'))
            if num_delim == '_':
                folder += '[_]'
            return folder
        else:
            folder = '_'.join(w if w.isupper() else w.capitalize() for w in pre.split('_'))
            if num_delim == '-':
                folder += '[-]'
            return folder
    else:
        m_simple = re.match(r"([A-Za-z0-9]+)\d+$", base)
        if m_simple:
            return m_simple.group(1).capitalize()
        return pre.capitalize()

# === Centralized IMG/DSC Detection ===
def extract_img_dsc_tag(filename):
    patterns = ["IMG", "DSC", "DSCN", "DCS", "DCSN"]
    pattern_re = re.compile(rf"({'|'.join(patterns)})", re.IGNORECASE)
    match = pattern_re.search(filename)
    return match.group(1).upper() if match else None

def organize_by_extension():
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []
    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                file_extension = filename.split('.')[-1]
                dst_folder = os.path.join(target_dir, file_extension)
                dst = os.path.join(dst_folder, filename)
                if os.path.exists(dst):
                    continue  # skip duplicate
                if os.path.abspath(src) != os.path.abspath(dst):
                    all_files.append((src, dst_folder, filename))
    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)

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

def smart_title(s):
    return '_'.join(
        w if w.isupper() else w.capitalize() for w in s.split('_')
    )

def folder_name_from_file(filename):
    base, ext = os.path.splitext(filename)
    base_clean = base
    m_paren = re.search(r'([_-])\((\d+)\)$', base)
    if m_paren:
        base_clean = base[:m_paren.start()]
    else:
        base_clean = re.sub(r'\(\d+\)$', '', base)
    m = re.search(r'([_-]?)(\d+)$', base_clean)
    if m:
        pre = base_clean[:m.start()]
        num_delim = m.group(1)
    else:
        pre = base_clean
        num_delim = ''
    if '_' in pre and '-' not in pre:
        folder = smart_title(pre)
        if num_delim == '-':
            folder += '[-]'
        return folder
    elif '-' in pre and '_' not in pre:
        folder = '-'.join(w.capitalize() if not w.isupper() else w for w in pre.split('-'))
        if num_delim == '_':
            folder += '[_]'
        return folder
    elif '_' in pre and '-' in pre:
        us = pre.rfind('_')
        ds = pre.rfind('-')
        if ds > us:
            folder = '-'.join(
                w.capitalize() if not w.isupper() else w for w in pre.split('-')
            )
            if num_delim == '_':
                folder += '[_]'
            return folder
        else:
            folder = smart_title(pre)
            if num_delim == '-':
                folder += '[-]'
            return folder
    else:
        m_simple = re.match(r"([A-Za-z0-9]+)\d+$", base_clean)
        if m_simple:
            folder = m_simple.group(1).capitalize()
            return folder
        return pre.capitalize()

def organize_alphabetically(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []

    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                first_char = filename[0].upper()

                if first_char.isalpha():
                    folder_name = first_char
                elif first_char.isdigit():
                    folder_name = "0-9"
                else:
                    folder_name = os.path.join("!@#$", first_char)

                dst_folder = os.path.join(target_dir, folder_name)
                dst = os.path.join(dst_folder, filename)

                if os.path.exists(dst):
                    continue  # skip duplicates
                if os.path.abspath(src) != os.path.abspath(dst):
                    all_files.append((src, dst_folder, filename))

    if preview:
        preview_popup([(src, os.path.basename(dst_folder), filename) for src, dst_folder, filename in all_files])
        return

    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)
        
# === Unified Preview Panel ===
def show_preview(previews):
    preview_text.delete("1.0", tk.END)
    for src, folder, filename in previews:
        preview_text.insert(tk.END, f"{filename} → {folder}/\n")

def preview_alphabetize():
    organize_alphabetically(preview=True)

def organize_smart(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []

    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                folder = folder_name_from_file(filename)
                dst_folder = os.path.join(target_dir, folder)
                dst = os.path.join(dst_folder, filename)

                if os.path.exists(dst):
                    continue  # skip duplicates
                if os.path.abspath(src) != os.path.abspath(dst):
                    all_files.append((src, dst_folder, filename))

    if preview:
        preview_popup([(src, os.path.basename(dst_folder), filename) for src, dst_folder, filename in all_files])
        return

    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)

def organize_smart_numeric(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []

    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                numeric_match = re.match(r"^(\d+)[-_]", filename)
                if numeric_match:
                    folder = numeric_match.group(1)
                else:
                    folder = folder_name_from_file(filename)

                dst_folder = os.path.join(target_dir, folder)
                dst = os.path.join(dst_folder, filename)

                if os.path.exists(dst):
                    continue
                if os.path.abspath(src) != os.path.abspath(dst):
                    all_files.append((src, dst_folder, filename))

    if preview:
        show_preview_in_panel([(src, os.path.basename(dst_folder), filename) for src, dst_folder, filename in all_files])
        return

    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    for index, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(index, total_files)

def organize_numerically(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []
    camera_patterns = ["IMG", "DSC", "DSCN", "DCS", "DCSN"]
    camera_pattern_regex = re.compile(r"\b(" + "|".join(camera_patterns) + r")\b", re.IGNORECASE)
    numeric_pattern = re.compile(r"^(\d+)([_\-]?)([A-Za-z]*)")
    text_pattern = re.compile(r"^([A-Za-z]+)")

    buckets = {}  # { base_bucket: [fileinfo, ...] }

    def get_bucket(num: int, size: int) -> int:
        return (num // size) * size

    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                folder_path_parts = []

                # Pattern: IMG, DSC, etc.
                camera_match = camera_pattern_regex.search(filename)
                if camera_match:
                    folder_path_parts.append(camera_match.group(1).upper())
                    dst_folder = os.path.join(target_dir, *folder_path_parts)
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
                    folder_path_parts.append(text_match.group(1).capitalize())
                    dst_folder = os.path.join(target_dir, *folder_path_parts)
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

        if current_count + len(file_list) <= 200 and not is_dense:
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
        show_preview_in_panel([
            (src, os.path.relpath(dst_folder, target_dir), filename)
            for src, dst_folder, filename in all_files
        ])
        return

    total_files = len(all_files)
    if total_files == 0:
        messagebox.showinfo("Numerically", "No matching files found to organize.")
        return

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

            folder = folder_name_from_file(filename)
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

def organize_by_detected_pattern(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []
    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                src = os.path.join(dirpath, filename)
                folder = detect_pattern_folder_name(filename)
                dst_folder = os.path.join(target_dir, folder)
                dst = os.path.join(dst_folder, filename)
                all_files.append((src, dst_folder, filename))
    if preview:
        show_preview([(src, os.path.basename(dst_folder), filename) for src, dst_folder, filename in all_files])
        return
    total = len(all_files)
    progress_bar["maximum"] = total
    for i, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(i, total)

def organize_img_dsc_files(preview=False):
    source_dirs = get_source_dirs()
    target_dir = target_entry.get()
    all_files = []
    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            for filename in files:
                tag = extract_img_dsc_tag(filename)
                if tag:
                    src = os.path.join(dirpath, filename)
                    dst_folder = os.path.join(target_dir, tag)
                    dst = os.path.join(dst_folder, filename)
                    all_files.append((src, dst_folder, filename))
    if preview:
        show_preview([(src, os.path.basename(dst_folder), filename) for src, dst_folder, filename in all_files])
        return
    total = len(all_files)
    progress_bar["maximum"] = total
    for i, (src, dst_folder, filename) in enumerate(all_files, 1):
        move_file(src, dst_folder, filename)
        update_progress(i, total)

def extract_all_to_parent():
    source_dirs = get_source_dirs()
    all_files = []
    for source_dir in source_dirs:
        for dirpath, _, files in os.walk(source_dir):
            if os.path.abspath(dirpath) == os.path.abspath(source_dir):
                continue
            for filename in files:
                src = os.path.join(dirpath, filename)
                dst = os.path.join(source_dir, filename)
                if os.path.exists(dst):
                    continue  # skip duplicate
                all_files.append({'src': src, 'dst': dst})
    if not all_files:
        messagebox.showinfo("Extract", "No files found in subfolders to extract.")
        return
    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    skipped = []
    moved = []
    for index, fileinfo in enumerate(all_files, 1):
        src_path = fileinfo['src']
        dest_path = fileinfo['dst']
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(src_path, dest_path)
            moved.append({'src': src_path, 'dst': dest_path})
        except Exception:
            skipped.append(fileinfo)
        update_progress(index, total_files)
    removed_folders = []
    for source_dir in source_dirs:
        for dirpath, dirs, files in os.walk(source_dir, topdown=False):
            if os.path.abspath(dirpath) == os.path.abspath(source_dir):
                continue
            if not os.listdir(dirpath):
                try:
                    os.rmdir(dirpath)
                    removed_folders.append(dirpath)
                except Exception:
                    pass
    msg = f"Extracted {len(moved)} file(s) to source directories."
    if skipped:
        msg += f"\nSkipped {len(skipped)} duplicate(s):\n" + ", ".join([os.path.basename(f['src']) for f in skipped[:5]])
        if len(skipped) > 5:
            msg += ", ..."
    msg += f"\nDeleted {len(removed_folders)} empty folder(s)."
    messagebox.showinfo("Extract Complete", msg)
    
# ───────── START: Extract Up N Levels ─────────
def extract_up_levels(levels=None):
    """
    Move files up N directory levels from their current path.
    Example: levels=1 moves .../A/B/file.jpg -> .../A/file.jpg
    """
    # Ask for N if not provided
    if levels is None:
        try:
            levels = simpledialog.askinteger(
                "Extract Up",
                "How many levels up should files be moved?",
                minvalue=1, maxvalue=20, parent=root
            )
        except Exception:
            levels = None
        if not levels:
            return  # cancelled or invalid

    source_dirs = get_source_dirs()
    if not source_dirs:
        messagebox.showerror("Extract Up", "Please select at least one source folder.")
        return

    all_moves = []  # list of (src, dst)
    # Build planned moves
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            for fname in files:
                src = os.path.join(dirpath, fname)

                # Compute destination "levels" up from current file's directory
                dest_dir = dirpath
                for _ in range(levels):
                    dest_dir = os.path.dirname(dest_dir)

                # If we climbed above the source root, clamp to the source root
                if len(os.path.abspath(dest_dir)) < len(os.path.abspath(source)):
                    dest_dir = source

                dst = os.path.join(dest_dir, fname)
                if os.path.abspath(src) == os.path.abspath(dst):
                    continue  # already at that level
                if os.path.exists(dst):
                    continue  # skip duplicates

                all_moves.append((src, dst))

    if not all_moves:
        messagebox.showinfo("Extract Up", "No files found to move for the chosen level(s).")
        return

    # Execute moves with progress
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

    # Optionally remove now-empty folders inside sources
    removed_dirs = 0
    for source in source_dirs:
        for dpath, dnames, fnames in os.walk(source, topdown=False):
            # don't delete the source root itself
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
    
def show_help():
    messagebox.showinfo(
        "Help: Pattern Guide",
        (
            "[by extension]\n"
            "    Files go into folders named after their extension.\n"
            "    Example: foo.jpg → .../jpg/\n\n"
            "Organize Smart (using patterns of name, set, and number):\n"
            "    name_set_number   → Name_Set\n"
            "    name_set-number   → Name_Set[-]\n"
            "    name-set-number   → Name-Set\n"
            "    name-set_number   → Name-Set[_]\n"
            "    name_setnumber    → Name_Set\n"
            "    heels35           → Heels\n"
            "    name_set_number_(001) → Name_Set_Number (ignore _(001))\n"
            "    name-set-number-(002) → Name-Set-Number (ignore -(002))\n"
            "    name(001)         → Name\n"
            "    name-set(002)     → Name-Set\n\n"
            "Alphabetize:\n"
            "    Files go into folders based on their first character.\n"
            "    A-Z → folders A-Z\n"
            "    0-9 → folder '0-9'\n"
            "    Symbols (e.g. #, !) → in '!@#$/<symbol>' folders\n\n"
            "Multiple source folders:\n"
            "    Drag or select more than one folder as source.\n"
            "    All files from all roots are merged for organizing/extracting.\n\n"
            "Organize Zips:\n"
            "    myarchive.zip-01, myarchive.zip-02 → .../myarchive/\n\n"
            "Extract:\n"
            "    Moves all files in subfolders to the parent source folder,\n"
            "    deletes empty subfolders, skips duplicates.\n\n"
            "Extract Up:\n"
            "    Specify how many levels up to extract files to.\n"
            "    Example: extracting up 2 levels from nested folders.\n\n"
            "Preview:\n"
            "    See what files would be moved and where before organizing.\n\n"
            "Drag & Drop:\n"
            "    Drag one or more folders from your file manager onto the Source entry field.\n\n"
            "Duplicates:\n"
            "    Any file that would be a duplicate (same filename exists in destination) is skipped and not moved."
            "Organize Top-Level Only:\n"
            "    Moves only the files in the root of the selected folder(s),\n"
            "    ignoring any files inside subfolders.\n\n"
            "\nNumerically:\n"
            "    Moves files that begin with a number into a folder named after that number.\n"
            "    Example: 100_peeks_043.jpg → .../100/\n"
            "    Example: 31-march.txt → .../31/\n"
            "    Preview shows in a bottom panel, and disappears after each operation.\n"
            "\nSmart + Numeric:\n"
            "    If filename starts with digits followed by '-' or '_', it goes into a folder named by that number.\n"
            "    Otherwise, applies Smart logic based on name/set/number structure.\n"
            "    Example: 100-peeks.jpg → 100/\n"
            "    Example: boots-47.jpg → Boots/\n"
            "    Uses bottom panel for preview.\n"
        )
    )

def make_entry_drop_target(entry_widget):
    def drop(event):
        data = event.data
        items = []
        in_brace = False
        buf = ''
        for ch in data:
            if ch == '{':
                in_brace = True
                buf = ''
            elif ch == '}':
                in_brace = False
                items.append(buf)
            elif ch == ' ' and not in_brace:
                if buf:
                    items.append(buf)
                    buf = ''
            else:
                buf += ch
        if buf:
            items.append(buf)
        dirs = [i.strip() for i in items if os.path.isdir(i.strip())]
        if dirs:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, ', '.join(dirs))
    entry_widget.drop_target_register(DND_FILES)
    entry_widget.dnd_bind('<<Drop>>', drop)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    root = TkinterDnD.Tk()
    dnd_available = True
except ImportError:
    root = tk.Tk()
    dnd_available = False

# === GUI Setup ===
root = tk.Tk()
root.title("File Organizer with Pattern Detection")

# Row 0 – Source & Target
tk.Label(root, text="Source Directory(ies):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
source_entry = tk.Entry(root, width=60)
source_entry.grid(row=0, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: source_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=5)

tk.Label(root, text="Target Directory:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
target_entry = tk.Entry(root, width=60)
target_entry.grid(row=1, column=1, padx=5)
tk.Button(root, text="Browse", command=lambda: target_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2, padx=5)

# Row 2 – Basic Organizers
tk.Button(root, text="[by extension]", command=organize_by_extension).grid(row=2, column=0, padx=5, pady=5)
tk.Button(root, text="Organize Zips", command=organize_zips).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Extract", command=extract_all_to_parent).grid(row=2, column=2, padx=5, pady=5)

# Row 3 – Smart Organizers
tk.Button(root, text="Organize Smart", command=lambda: organize_smart(preview=False)).grid(row=3, column=0, padx=5, pady=5)
tk.Button(root, text="Preview Smart", command=lambda: organize_smart(preview=True)).grid(row=3, column=1, padx=5, pady=5)
tk.Button(root, text="Alphabetize", command=lambda: organize_alphabetically(preview=False)).grid(row=3, column=2, padx=5, pady=5)

# Row 4 – Smart + Numeric & Numeric Preview
tk.Button(root, text="Smart + Numeric", command=lambda: organize_smart_numeric(preview=True)).grid(row=4, column=0, padx=5, pady=5)
tk.Button(root, text="Preview Numerically", command=lambda: organize_numerically(preview=True)).grid(row=4, column=1, padx=5, pady=5)

# Row 5 – Top-level options
tk.Label(root, text="Levels Up:").grid(row=5, column=0, padx=5, sticky="e")
extract_level_entry = tk.Entry(root, width=5)
extract_level_entry.insert(0, "2")
extract_level_entry.grid(row=5, column=1, sticky="w")
tk.Button(root, text="Extract Up", command=extract_up_levels).grid(row=5, column=2, padx=5)

# Row 6 – Pattern Detection Organizers
tk.Button(root, text="DET file", command=lambda: organize_by_detected_pattern(preview=False)).grid(row=6, column=0, padx=5, pady=5)
tk.Button(root, text="Preview DET", command=lambda: organize_by_detected_pattern(preview=True)).grid(row=6, column=1, padx=5, pady=5)

# Row 7 – IMG/DSC Only
tk.Button(root, text="IMG/DSC Only", command=lambda: organize_img_dsc_files(preview=False)).grid(row=7, column=0, padx=5, pady=5)
tk.Button(root, text="Preview IMG/DSC", command=lambda: organize_img_dsc_files(preview=True)).grid(row=7, column=1, padx=5, pady=5)

# Row 8 – Progress bar and clear button
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=8, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="we")
tk.Button(root, text="Clear Preview", command=lambda: preview_text.delete("1.0", tk.END)).grid(row=8, column=2, padx=10, pady=(10, 5))

# Row 9 – Unified preview panel
preview_frame = tk.Frame(root)
preview_frame.grid(row=9, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="we")
preview_text = tk.Text(preview_frame, height=12, width=95, wrap="none")
preview_text.pack(fill="both", expand=True)

root.mainloop()
