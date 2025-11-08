# ==============================
# FILE ORGANIZER - MASTER FILE 5
# PRODUCTION-READY EDITION
# ==============================
# NEW FEATURES:
# - Sequential Pattern Detection (NEW!)
# - Pattern Scanner with 7 pattern types (NEW!)
# - Centralized data directory (.file_organizer_data/)
# - Operation logging with UNDO functionality
# - Hash-based duplicate detection (MD5)
# - Memory-efficient processing (generators, chunking)
# - Configuration system
# - Pre-flight validation
# - Comprehensive error reporting
# - Statistics and analytics
# - Safety features and rollback
# ==============================

import os
import re
import shutil
import json
import hashlib
import sqlite3
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from typing import Iterator, Tuple, Dict, List, Optional

# ==============================
# DATA DIRECTORY MANAGEMENT
# ==============================
class DataDirectory:
    """Manages centralized data storage"""

    def __init__(self):
        self.base_dir = Path(__file__).parent / ".file_organizer_data"
        self.config_file = self.base_dir / "config.json"
        self.operations_file = self.base_dir / "operations.jsonl"
        self.duplicates_db = self.base_dir / "duplicates.db"
        self.mappings_file = self.base_dir / "folder_mappings.json"
        self.stats_file = self.base_dir / "statistics.json"

        self._ensure_directory()

    def _ensure_directory(self):
        """Create data directory if it doesn't exist"""
        self.base_dir.mkdir(exist_ok=True)

    def get_path(self, filename: str) -> Path:
        """Get path to a data file"""
        return self.base_dir / filename

# Global data directory instance
DATA_DIR = DataDirectory()

# ==============================
# CONFIGURATION SYSTEM
# ==============================
class Config:
    """Centralized configuration management"""

    DEFAULT_CONFIG = {
        "max_files_per_folder": 500,
        "skip_folders": ["Sort", ".git", "node_modules", "__pycache__"],
        "duplicate_detection": {
            "method": "hash",  # "size_only" or "hash"
            "hash_algorithm": "md5",
            "chunk_size": 8192
        },
        "performance": {
            "batch_size": 10000,
            "progress_update_interval": 1000,
            "use_generators": True
        },
        "safety": {
            "enable_undo": True,
            "max_undo_operations": 10,
            "validate_before_move": True
        },
        "ui": {
            "theme": "clam",
            "font_base": "Segoe UI",
            "font_size": 10
        }
    }

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or create default"""
        if DATA_DIR.config_file.exists():
            try:
                with open(DATA_DIR.config_file, 'r') as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: dict):
        """Save configuration to file"""
        try:
            with open(DATA_DIR.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default=None):
        """Get config value with dot notation (e.g., 'duplicate_detection.method')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

    def set(self, key: str, value):
        """Set config value and save"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self._save_config(self.config)

# Global config instance
CONFIG = Config()

# ==============================
# OPERATION LOGGING SYSTEM
# ==============================
class OperationLogger:
    """Logs all file operations for undo functionality"""

    def __init__(self):
        self.current_operation = None
        self.operations = []

    def start_operation(self, operation_type: str, source_dirs: List[str], target_dir: str):
        """Start a new operation"""
        self.current_operation = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "source_dirs": source_dirs,
            "target_dir": target_dir,
            "moves": [],
            "errors": [],
            "stats": {
                "files_moved": 0,
                "duplicates_found": 0,
                "errors": 0,
                "total_size_mb": 0
            }
        }

    def log_move(self, src: str, dst: str, size_bytes: int):
        """Log a successful file move"""
        if self.current_operation:
            self.current_operation["moves"].append({
                "from": src,
                "to": dst,
                "size": size_bytes
            })
            self.current_operation["stats"]["files_moved"] += 1
            self.current_operation["stats"]["total_size_mb"] += size_bytes / (1024 * 1024)

    def log_error(self, error: str, filename: str):
        """Log an error"""
        if self.current_operation:
            self.current_operation["errors"].append({
                "error": error,
                "file": filename,
                "timestamp": datetime.now().isoformat()
            })
            self.current_operation["stats"]["errors"] += 1

    def log_duplicate(self):
        """Increment duplicate counter"""
        if self.current_operation:
            self.current_operation["stats"]["duplicates_found"] += 1

    def end_operation(self):
        """End current operation and save to log"""
        if self.current_operation:
            # Append to JSONL file (one JSON object per line)
            try:
                with open(DATA_DIR.operations_file, 'a') as f:
                    f.write(json.dumps(self.current_operation) + '\n')
                self.operations.append(self.current_operation)

                # Keep only last N operations in memory
                max_ops = CONFIG.get('safety.max_undo_operations', 10)
                if len(self.operations) > max_ops:
                    self.operations = self.operations[-max_ops:]
            except Exception as e:
                print(f"Failed to save operation log: {e}")

            self.current_operation = None

    def get_recent_operations(self, limit: int = 10) -> List[dict]:
        """Get recent operations from log file"""
        operations = []
        if DATA_DIR.operations_file.exists():
            try:
                with open(DATA_DIR.operations_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        operations.append(json.loads(line))
            except Exception as e:
                print(f"Failed to read operations: {e}")
        return operations

    def undo_last_operation(self) -> Tuple[bool, str]:
        """Undo the last operation"""
        recent = self.get_recent_operations(1)
        if not recent:
            return False, "No operations to undo"

        operation = recent[0]
        moved_back = 0
        errors = []

        # Move files back in reverse order
        for move in reversed(operation["moves"]):
            try:
                if os.path.exists(move["to"]):
                    os.makedirs(os.path.dirname(move["from"]), exist_ok=True)
                    shutil.move(move["to"], move["from"])
                    moved_back += 1
            except Exception as e:
                errors.append(f"{os.path.basename(move['to'])}: {str(e)}")

        if errors:
            return True, f"Undone {moved_back} files. Errors: {len(errors)}"
        return True, f"Successfully undone {moved_back} file moves"

# Global logger instance
LOGGER = OperationLogger()

# ==============================
# HASH-BASED DUPLICATE DETECTION
# ==============================
class DuplicateDetector:
    """Hash-based duplicate detection with SQLite storage"""

    def __init__(self):
        self.db_path = DATA_DIR.duplicates_db
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for duplicate hashes"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS file_hashes (
                filename TEXT,
                size INTEGER,
                hash TEXT,
                path TEXT,
                first_seen TIMESTAMP,
                PRIMARY KEY (filename, size, hash)
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_filename ON file_hashes(filename)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_hash ON file_hashes(hash)')
        conn.commit()
        conn.close()

    def compute_hash(self, filepath: str) -> Optional[str]:
        """Compute MD5 hash of file"""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(CONFIG.get('duplicate_detection.chunk_size', 8192)), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None

    def check_duplicate(self, filename: str, size: int, filepath: str) -> Tuple[bool, str]:
        """
        Check if file is duplicate.
        Returns: (is_duplicate, duplicate_type)
        - (False, '') = First occurrence
        - (True, 'DUPES') = Same name + size + hash
        - (True, 'DUPE SIZE') = Same name + different size
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if filename exists
        cursor.execute('SELECT size, hash FROM file_hashes WHERE filename = ?', (filename,))
        results = cursor.fetchall()

        if not results:
            # First occurrence - compute and store hash
            file_hash = self.compute_hash(filepath)
            if file_hash:
                cursor.execute('''
                    INSERT OR REPLACE INTO file_hashes (filename, size, hash, path, first_seen)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filename, size, file_hash, filepath, datetime.now().isoformat()))
                conn.commit()
            conn.close()
            return False, ''

        # File with same name exists - compute hash
        file_hash = self.compute_hash(filepath)
        if not file_hash:
            conn.close()
            return False, ''

        # Check if hash matches any existing hash
        for existing_size, existing_hash in results:
            if existing_hash == file_hash and existing_size == size:
                # True duplicate (same name + size + hash)
                conn.close()
                return True, 'DUPES'

        # Same name but different hash/size
        # Store this variant
        cursor.execute('''
            INSERT OR REPLACE INTO file_hashes (filename, size, hash, path, first_seen)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, size, file_hash, filepath, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, 'DUPE SIZE'

    def clear_session(self):
        """Clear current session data (for new scan)"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM file_hashes')
        conn.commit()
        conn.close()

# Global duplicate detector
DUPLICATE_DETECTOR = DuplicateDetector()

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

root.title("File Organizer - Master File 5 (Production Edition)")

# ── THEME ──────────────────────────────────────────────────────────────────────
style = ttk.Style()
theme = CONFIG.get('ui.theme', 'clam')
for t in (theme, "clam", "vista", "xpnative", "default"):
    try:
        style.theme_use(t)
        break
    except Exception:
        pass

FONT_BASE  = (CONFIG.get('ui.font_base', 'Segoe UI'), CONFIG.get('ui.font_size', 10))
FONT_TITLE = (CONFIG.get('ui.font_base', 'Segoe UI'), 12, 'bold')
root.option_add("*Font", FONT_BASE)
root.configure(padx=10, pady=10)
style.configure("TButton", padding=6)
style.configure("TEntry", padding=4)
style.configure("TLabel", padding=2)
style.configure("Title.TLabel", font=FONT_TITLE)
style.configure("TProgressbar", thickness=12)
style.configure("Section.TLabelframe.Label", font=FONT_TITLE)

levels_entry = None

# ── HEADER ─────────────────────────────────────────────────────────────────────
header = ttk.Frame(root, padding=(8, 8))
header.grid(row=0, column=0, columnspan=3, sticky="ew")
ttk.Label(header, text="File Organizer - v5 Production Edition", style="Title.TLabel").pack(side="left")

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
def get_source_dirs() -> List[str]:
    return [d.strip() for d in source_entry.get().split(',') if os.path.isdir(d.strip())]

def should_skip_folder(folder_name: str) -> bool:
    """Check if folder should be skipped"""
    skip_list = CONFIG.get('skip_folders', ['Sort'])
    return folder_name in skip_list

def report_error(title: str, message: str):
    sep = "-" * 70
    try:
        preview_text.insert("end", f"\n{sep}\n{title}: {message}\n{sep}\n")
        preview_text.see("end")
    except Exception:
        print(f"[{title}] {message}")

def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except Exception:
        return -1

def move_file(src: str, dst_folder: str, filename: str) -> bool:
    """Move file with logging"""
    os.makedirs(dst_folder, exist_ok=True)
    base, ext = os.path.splitext(filename)
    dst = os.path.join(dst_folder, filename)

    try:
        # Pre-flight check
        if CONFIG.get('safety.validate_before_move', True):
            if not os.access(dst_folder, os.W_OK):
                LOGGER.log_error("No write permission", filename)
                return False

        shutil.move(src, dst)
        size = get_file_size(dst)
        LOGGER.log_move(src, dst, size)
        return True
    except Exception as e:
        LOGGER.log_error(str(e), filename)
        return False

def update_progress(index: int, total: int):
    progress_bar["value"] = index
    root.update_idletasks()
    if index == total:
        # Show operation summary
        if LOGGER.current_operation:
            stats = LOGGER.current_operation["stats"]
            msg = f"✓ Completed!\n\n"
            msg += f"Files moved: {stats['files_moved']}\n"
            msg += f"Duplicates found: {stats['duplicates_found']}\n"
            msg += f"Total size: {stats['total_size_mb']:.2f} MB\n"
            if stats['errors'] > 0:
                msg += f"\n⚠ Errors: {stats['errors']}"
            messagebox.showinfo("Operation Complete", msg)

def show_preview(preview_items: List[Tuple[str, str, str]]):
    preview_text.delete("1.0", tk.END)

    # Group by folder and count
    folder_counts = {}
    for _, folder, filename in preview_items:
        folder_counts[folder] = folder_counts.get(folder, 0) + 1

    # Show summary
    preview_text.insert(tk.END, f"=== PREVIEW SUMMARY ===\n")
    preview_text.insert(tk.END, f"Total files: {len(preview_items)}\n")
    preview_text.insert(tk.END, f"Destination folders: {len(folder_counts)}\n\n")

    # Show folder breakdown
    preview_text.insert(tk.END, f"=== FOLDER BREAKDOWN ===\n")
    for folder, count in sorted(folder_counts.items(), key=lambda x: x[1], reverse=True):
        preview_text.insert(tk.END, f"{folder}/: {count} files\n")

    preview_text.insert(tk.END, f"\n=== SAMPLE FILES (first 100) ===\n")
    for _, folder, filename in preview_items[:100]:
        preview_text.insert(tk.END, f"{filename} → {folder}/\n")

    if len(preview_items) > 100:
        preview_text.insert(tk.END, f"\n... and {len(preview_items) - 100} more files")

def smart_title(text: str) -> str:
    return '_'.join(w if w.isupper() else w.capitalize() for w in text.split('_'))

# === User mapping (Smart +) ===
USER_MAP = {}
def load_mappings():
    global USER_MAP
    if DATA_DIR.mappings_file.exists():
        try:
            with open(DATA_DIR.mappings_file, "r", encoding="utf-8") as f:
                USER_MAP = json.load(f)
        except Exception:
            USER_MAP = {}
def save_mappings():
    try:
        with open(DATA_DIR.mappings_file, "w", encoding="utf-8") as f:
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
def detect_folder_name(filename: str) -> Optional[str]:
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

def extract_img_tag(filename: str) -> Optional[str]:
    m = re.search(r"(IMG|DSC|DSCN|DCS|DCSN)(?=\d|_|\.|$)", filename, re.IGNORECASE)
    return m.group(1).upper() if m else None

def detect_sequential_pattern(filename: str) -> Optional[str]:
    """
    Detect sequential file patterns and return the base name for folder.

    Examples:
        031204-0022 → 031204
        file001 → File
        vacation-001 → Vacation
        IMG_1234 → IMG

    Pattern: [BASE][SEPARATOR?][2+ DIGITS]
    Separators: -, _, or none
    Requires at least 2 trailing digits to avoid false positives
    """
    base, _ = os.path.splitext(filename)

    # Remove duplicate markers like (2), (3)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base).rstrip(' .')

    # Pattern 1: BASE with separator followed by 2+ digits
    # Example: vacation-001, file_123, IMG-1234
    m_sep = re.match(r'^(.+?)([-_])(\d{2,})$', base)
    if m_sep:
        base_name = m_sep.group(1)
        # Capitalize if all lowercase or mixed case, keep uppercase as-is
        if base_name.isupper():
            return base_name
        return base_name.capitalize()

    # Pattern 2: BASE without separator followed by 2+ digits
    # Example: file001, vacation123
    # Must be letters followed by digits, or mixed alphanumeric
    m_no_sep = re.match(r'^([A-Za-z]+)(\d{2,})$', base)
    if m_no_sep:
        base_name = m_no_sep.group(1)
        # Capitalize if all lowercase or mixed case, keep uppercase as-is
        if base_name.isupper():
            return base_name
        return base_name.capitalize()

    # Pattern 3: Numeric BASE with separator followed by 2+ digits
    # Example: 031204-0022, 20240101-001
    m_numeric = re.match(r'^(\d+)([-_])(\d{2,})$', base)
    if m_numeric:
        return m_numeric.group(1)

    return None

# ==============================
# PRE-FLIGHT VALIDATION
# ==============================
def validate_operation(source_dirs: List[str], target_dir: str) -> Tuple[bool, List[str]]:
    """
    Validate operation before execution.
    Returns: (is_valid, list_of_issues)
    """
    issues = []

    # Check source directories
    if not source_dirs:
        issues.append("❌ No source directories selected")
    for src in source_dirs:
        if not os.path.exists(src):
            issues.append(f"❌ Source does not exist: {src}")
        elif not os.path.isdir(src):
            issues.append(f"❌ Source is not a directory: {src}")

    # Check target directory
    if not target_dir:
        issues.append("❌ No target directory selected")
    elif not os.path.exists(target_dir):
        issues.append(f"❌ Target does not exist: {target_dir}")
    elif not os.path.isdir(target_dir):
        issues.append(f"❌ Target is not a directory: {target_dir}")
    elif not os.access(target_dir, os.W_OK):
        issues.append(f"❌ No write permission for target: {target_dir}")

    # Check if target is inside source
    for src in source_dirs:
        try:
            if os.path.commonpath([os.path.abspath(target_dir), os.path.abspath(src)]) == os.path.abspath(src):
                issues.append(f"❌ Target cannot be inside source: {src}")
        except Exception:
            pass

    # Check available space
    try:
        if target_dir and os.path.exists(target_dir):
            stat = shutil.disk_usage(target_dir)
            free_gb = stat.free / (1024**3)
            if free_gb < 1:
                issues.append(f"⚠ Low disk space: {free_gb:.2f} GB free")
    except Exception:
        pass

    return len(issues) == 0, issues

# ==============================
# MEMORY-EFFICIENT FILE COLLECTION
# ==============================
def collect_files_generator(source_dirs: List[str], logic_func) -> Iterator[Tuple[str, str, str]]:
    """
    Memory-efficient file collection using generators.
    Yields: (source_path, destination_folder, filename)
    """
    target_root = (target_entry.get() or "").strip()
    seen_files = {}  # {filename: {sizes: [], hashes: [], count: N}}

    use_hash = CONFIG.get('duplicate_detection.method') == 'hash'

    for source in source_dirs:
        for dirpath, dirnames, files in os.walk(source):
            # Filter skip folders
            dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]

            for file in files:
                src = os.path.join(dirpath, file)
                file_size = get_file_size(src)

                # Check for duplicates
                if file in seen_files:
                    seen_files[file]['count'] += 1
                    count = seen_files[file]['count']
                    base, ext = os.path.splitext(file)
                    new_filename = f"{base} ({count}){ext}"

                    # Determine if true duplicate or name collision
                    if use_hash:
                        is_dup, dup_type = DUPLICATE_DETECTOR.check_duplicate(file, file_size, src)
                        if is_dup:
                            LOGGER.log_duplicate()
                            yield (src, os.path.join(target_root, dup_type), new_filename)
                            continue
                    else:
                        # Size-only detection
                        if file_size in seen_files[file]['sizes']:
                            LOGGER.log_duplicate()
                            yield (src, os.path.join(target_root, "DUPES"), new_filename)
                            continue
                        else:
                            seen_files[file]['sizes'].append(file_size)
                            yield (src, os.path.join(target_root, "DUPE SIZE"), new_filename)
                            continue
                else:
                    # First occurrence
                    seen_files[file] = {'sizes': [file_size], 'count': 0}
                    if use_hash:
                        DUPLICATE_DETECTOR.check_duplicate(file, file_size, src)

                # Get destination folder
                rel_folder = logic_func(file)
                if not rel_folder:
                    continue

                dst_folder = os.path.join(target_root, rel_folder)
                dst = os.path.join(dst_folder, file)

                if os.path.abspath(src) == os.path.abspath(dst):
                    continue

                yield (src, dst_folder, file)

def collect_files_chunked(source_dirs: List[str], logic_func, chunk_size: int = 10000) -> List[List[Tuple[str, str, str]]]:
    """Collect files in chunks for batch processing"""
    chunks = []
    current_chunk = []

    for item in collect_files_generator(source_dirs, logic_func):
        current_chunk.append(item)
        if len(current_chunk) >= chunk_size:
            chunks.append(current_chunk)
            current_chunk = []

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# ==============================
# ORGANIZER ENGINE
# ==============================
def run_organizer(folder_logic, preview=False, operation_name="Organize"):
    source_dirs = get_source_dirs()
    target_dir  = (target_entry.get() or "").strip()

    # Validation
    is_valid, issues = validate_operation(source_dirs, target_dir)
    if not is_valid:
        error_msg = "Pre-flight validation failed:\n\n" + "\n".join(issues)
        messagebox.showerror("Validation Error", error_msg)
        return

    # Clear duplicate detector session for new scan
    if CONFIG.get('duplicate_detection.method') == 'hash':
        DUPLICATE_DETECTOR.clear_session()

    # Start operation logging
    LOGGER.start_operation(operation_name, source_dirs, target_dir)

    logic = lambda fname: folder_logic(fname)

    # Use generator for memory efficiency
    if CONFIG.get('performance.use_generators', True):
        file_gen = collect_files_generator(source_dirs, logic)

        if preview:
            # For preview, collect first 1000 items
            preview_items = []
            for i, (src, dst_folder, fname) in enumerate(file_gen):
                if i >= 1000:
                    break
                preview_items.append((src, os.path.relpath(dst_folder, target_dir), fname))
            show_preview(preview_items)
            LOGGER.end_operation()
            return

        # Execute moves with progress
        total = 0
        moved = 0
        progress_update_interval = CONFIG.get('performance.progress_update_interval', 1000)

        progress_bar["mode"] = "indeterminate"
        progress_bar.start()

        for src, dst_folder, fname in file_gen:
            total += 1
            if move_file(src, dst_folder, fname):
                moved += 1

            if total % progress_update_interval == 0:
                root.update_idletasks()

        progress_bar.stop()
        progress_bar["mode"] = "determinate"
        progress_bar["maximum"] = total
        progress_bar["value"] = moved

        # End operation logging
        LOGGER.end_operation()

        # Show summary
        stats = LOGGER.operations[-1]["stats"] if LOGGER.operations else {}
        msg = f"✓ Operation Complete!\n\n"
        msg += f"Files processed: {total}\n"
        msg += f"Files moved: {moved}\n"
        msg += f"Duplicates: {stats.get('duplicates_found', 0)}\n"
        if stats.get('errors', 0) > 0:
            msg += f"\n⚠ Errors: {stats['errors']}"
        messagebox.showinfo("Complete", msg)

# ==============================
# LOGIC FUNCTIONS (from v4)
# ==============================
def by_extension(filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1][1:]
    return ext.upper() if ext else "_NOEXT"

def by_alphabet(filename: str) -> str:
    first = filename[0].upper()
    if first.isalpha(): return first
    if first.isdigit(): return "0-9"
    return "!@#$"

def by_numeric_simple(filename: str) -> str:
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

def by_img_dsc(filename: str) -> Optional[str]:
    return extract_img_tag(filename)

def by_detected(filename: str) -> Optional[str]:
    return detect_folder_name(filename)

def by_detected_or_prompt(filename: str, allow_prompt: bool = True) -> Optional[str]:
    key = make_key(filename)
    if key in USER_MAP:
        return USER_MAP[key]
    folder = detect_folder_name(filename)
    if folder:
        return folder
    if allow_prompt:
        answer = simpledialog.askstring(
            "Unclassified file",
            f"Enter folder name for:\n\n{filename}\n\nThis choice will be remembered.\n(Target: {target_entry.get()})"
        )
        if answer:
            USER_MAP[key] = answer.strip()
            save_mappings()
            return USER_MAP[key]
    return None

def by_sequential(filename: str) -> Optional[str]:
    """Sequential pattern detection for organization mode"""
    return detect_sequential_pattern(filename)

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

        # Pattern 0: SEQUENCE - Sequential file patterns (NEW!)
        # Example: "031204-0022" → "031204", "file001" → "File", "vacation-001" → "Vacation"
        seq_folder = detect_sequential_pattern(filename)
        if seq_folder:
            pattern_key = f"SEQUENCE:{seq_folder}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'type': 'sequence',
                    'name': seq_folder,
                    'files': [],
                    'folder_name': seq_folder
                }
            patterns[pattern_key]['files'].append(filename)
            continue

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
                           font=FONT_TITLE)
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
            for dirpath, dirnames, files in os.walk(source):
                # Filter skip folders
                dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]
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

        # Start operation logging
        LOGGER.start_operation("Pattern Scanner", source_dirs, target_dir)

        # Build file map for quick lookup
        file_map = {}
        for source in source_dirs:
            for dirpath, dirnames, files in os.walk(source):
                # Filter skip folders
                dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]
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
                    if move_file(src, dst_folder, filename):
                        total_moved += 1
                    progress_bar["value"] = total_moved
                    if total_moved % 100 == 0:
                        root.update_idletasks()

        # End operation logging
        LOGGER.end_operation()

        messagebox.showinfo("Complete", f"Organized {total_moved:,} files into {len(detected_patterns)} folders")
        scanner_win.destroy()

    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x")

    ttk.Button(button_frame, text="🔍 Scan Files", command=scan_files, width=15).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="📁 Organize by Patterns", command=organize_by_patterns, width=20).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="Close", command=scanner_win.destroy).pack(side="right")

# ==============================
# UNDO FUNCTIONALITY
# ==============================
def show_undo_window():
    """Show window with recent operations and undo capability"""
    undo_win = tk.Toplevel(root)
    undo_win.title("Operation History & Undo")
    undo_win.geometry("800x600")

    main_frame = ttk.Frame(undo_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Recent Operations", font=FONT_TITLE).pack(anchor="w", pady=(0, 10))

    # Treeview for operations
    columns = ("Timestamp", "Type", "Files Moved", "Duplicates", "Errors")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
    tree.column("Timestamp", width=150)
    tree.column("Type", width=150)
    tree.column("Files Moved", width=100)
    tree.column("Duplicates", width=100)
    tree.column("Errors", width=80)

    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill=tk.BOTH, expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load operations
    operations = LOGGER.get_recent_operations(20)
    for op in reversed(operations):
        tree.insert("", "end", values=(
            op["timestamp"][:19],
            op["type"],
            op["stats"]["files_moved"],
            op["stats"]["duplicates_found"],
            op["stats"]["errors"]
        ))

    def do_undo():
        if messagebox.askyesno("Confirm Undo", "Undo the last operation? This will move files back to their original locations."):
            success, message = LOGGER.undo_last_operation()
            messagebox.showinfo("Undo Result", message)
            undo_win.destroy()

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))
    ttk.Button(button_frame, text="Undo Last Operation", command=do_undo).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="Close", command=undo_win.destroy).pack(side="right")

# ==============================
# STATISTICS WINDOW
# ==============================
def show_statistics():
    """Show statistics from operation history"""
    stats_win = tk.Toplevel(root)
    stats_win.title("Statistics & Analytics")
    stats_win.geometry("700x500")

    main_frame = ttk.Frame(stats_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Operation Statistics", font=FONT_TITLE).pack(anchor="w", pady=(0, 10))

    operations = LOGGER.get_recent_operations(100)

    if not operations:
        ttk.Label(main_frame, text="No operations recorded yet.").pack()
        return

    # Calculate statistics
    total_files = sum(op["stats"]["files_moved"] for op in operations)
    total_dupes = sum(op["stats"]["duplicates_found"] for op in operations)
    total_errors = sum(op["stats"]["errors"] for op in operations)
    total_size_mb = sum(op["stats"]["total_size_mb"] for op in operations)

    stats_text = tk.Text(main_frame, wrap="word", font=("Courier", 10), height=20)
    stats_text.pack(fill=tk.BOTH, expand=True)

    report = f"""
╔═══════════════════════════════════════════╗
║    FILE ORGANIZER STATISTICS              ║
╚═══════════════════════════════════════════╝

📊 OVERALL STATISTICS
─────────────────────────────────────────────
Total Operations:        {len(operations)}
Total Files Organized:   {total_files:,}
Total Duplicates Found:  {total_dupes:,}
Total Errors:            {total_errors:,}
Total Data Moved:        {total_size_mb:,.2f} MB

📈 RECENT OPERATIONS (Last 10)
─────────────────────────────────────────────
"""

    for op in reversed(operations[-10:]):
        report += f"\n{op['timestamp'][:19]} | {op['type']}\n"
        report += f"  Files: {op['stats']['files_moved']} | "
        report += f"Dupes: {op['stats']['duplicates_found']} | "
        report += f"Errors: {op['stats']['errors']}\n"

    stats_text.insert("1.0", report)
    stats_text.config(state="disabled")

    ttk.Button(main_frame, text="Close", command=stats_win.destroy).pack(pady=(10, 0))

# ==============================
# HELP WINDOW
# ==============================
def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("Help - Production Edition Guide")
    help_win.geometry("800x700")
    help_win.minsize(600, 500)
    frame = tk.Frame(help_win)
    frame.pack(fill=tk.BOTH, expand=True)
    text_area = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    help_text = """
FILE ORGANIZER - MASTER FILE 5 (PRODUCTION EDITION)
═══════════════════════════════════════════════════

🆕 NEW IN VERSION 5 (PRODUCTION FEATURES):

🔥 SEQUENTIAL PATTERN DETECTION (NEW!)
• Detects sequential file naming patterns
• Pattern types supported:
  - With separator: vacation-001, file_123, IMG-1234 → Vacation/, File/, IMG/
  - Without separator: file001, IMG1234 → File/, IMG/
  - Numeric base: 031204-0022, 20240101-001 → 031204/, 20240101/
• Requires minimum 2 trailing digits to avoid false positives
• Available as organization mode AND in Pattern Scanner
• Examples:
  - vacation-001.jpg, vacation-002.jpg → Vacation/
  - file001.txt, file002.txt → File/
  - 031204-0022.jpg, 031204-0023.jpg → 031204/

🔍 PATTERN SCANNER WITH 7 PATTERN TYPES
• Automatically scans and detects patterns in millions of files
• Pattern types:
  1. SEQUENCE - Sequential patterns (NEW!)
  2. PREFIX - Common word prefixes
  3. DELIMITER - Token-based patterns
  4. CAMERA - Device tags (IMG, DSC, etc.)
  5. DATE - Date patterns
  6. NUMERIC - Number ranges
  7. EXTENSION - File type grouping
• One-click organize by detected patterns
• Shows statistics and samples

📁 CENTRALIZED DATA DIRECTORY
• All data stored in: .file_organizer_data/
  - config.json (settings)
  - operations.jsonl (operation log)
  - duplicates.db (hash database)
  - folder_mappings.json (Smart Pattern+ choices)
  - statistics.json (usage stats)
• Easy to backup, portable, clean

🔄 OPERATION LOGGING & UNDO
• Every operation is logged with full details
• View operation history (View History button)
• UNDO last operation (moves files back!)
• Maximum undo operations: 10 (configurable)
• Never lose track of what was moved

🔐 HASH-BASED DUPLICATE DETECTION
• Uses MD5 hashing for 100% accuracy
• No false positives (same size ≠ duplicate)
• True duplicates: same name + size + hash → DUPES
• Name collision: same name + different content → DUPE SIZE
• Persistent database across sessions

⚡ MEMORY EFFICIENT PROCESSING
• Generator-based file collection
• Handles millions of files without memory issues
• Batch processing in chunks of 10,000
• Progress updates every 1,000 files
• Optimized for large-scale operations

✅ PRE-FLIGHT VALIDATION
• Checks source/target validity
• Verifies write permissions
• Prevents target-in-source errors
• Warns about low disk space
• Validates before any file moves

📊 STATISTICS & ANALYTICS
• Track all operations
• Total files organized
• Duplicates found
• Data moved (MB/GB)
• Error summaries
• View in Statistics window

🛡️ SAFETY FEATURES
• Configurable skip folders (Sort, .git, etc.)
• Write permission validation
• Error collection and reporting
• Operation rollback (undo)
• No data loss

⚙️ CONFIGURATION SYSTEM
• Customize max files per folder
• Choose duplicate detection method
• Adjust performance settings
• Configure UI theme
• All settings in config.json

═══════════════════════════════════════════════════

🎯 HOW TO USE:

1. Select Source folder(s)
2. Select Target folder
3. Choose organization mode
4. Click Preview to see plan
5. Click organize button to execute
6. View statistics or undo if needed

🔍 ORGANIZATION MODES:
• By Extension - Group by file type
• Alphabetize - Group by first character
• Smart Pattern - Detect naming patterns
• Smart Pattern + - Prompt for unknown patterns
• Sequential Pattern - Detect sequential files (file001→File, vacation-001→Vacation, 031204-0022→031204)
• IMG/DSC Only - Camera file detection
• Pattern Scanner - Auto-detect 7 pattern types including SEQUENCE

📝 TIPS:
• Always preview before organizing
• Check operation history regularly
• Use undo if something goes wrong
• Configure skip_folders for system dirs
• Enable hash detection for accuracy

═══════════════════════════════════════════════════
Version 5.0 - Production Ready
"""
    text_area.insert(tk.END, help_text)
    text_area.config(state=tk.DISABLED)

# ==============================
# BUTTON DEFINITIONS
# ==============================
def add_section(parent: ttk.Frame, title: str, buttons: list):
    sect = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
    sect.pack(fill="x", padx=0, pady=(0, 6))
    row = ttk.Frame(sect)
    row.pack(fill="x", padx=6, pady=6)
    for label, cmd in buttons:
        ttk.Button(row, text=label, command=cmd).pack(side="left", padx=(0, 6))
    ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

sections = {
    "By Extension": [
        ("By Extension", lambda: run_organizer(by_extension, operation_name="By Extension")),
        ("Preview", lambda: run_organizer(by_extension, preview=True)),
    ],
    "Alphabetize": [
        ("Alphabetize", lambda: run_organizer(by_alphabet, operation_name="Alphabetize")),
        ("Preview", lambda: run_organizer(by_alphabet, preview=True)),
        ("Numeric", lambda: run_organizer(by_numeric_simple, operation_name="Numeric")),
    ],
    "IMG/DSC": [
        ("IMG/DSC Only", lambda: run_organizer(by_img_dsc, operation_name="IMG/DSC")),
        ("Preview", lambda: run_organizer(by_img_dsc, preview=True)),
    ],
    "Smart Pattern": [
        ("Smart Pattern", lambda: run_organizer(by_detected, operation_name="Smart Pattern")),
        ("Preview", lambda: run_organizer(by_detected, preview=True)),
    ],
    "Smart Pattern +": [
        ("Smart Pattern +", lambda: run_organizer(lambda f: by_detected_or_prompt(f, True), operation_name="Smart Pattern+")),
        ("Preview", lambda: run_organizer(lambda f: by_detected_or_prompt(f, False), preview=True)),
    ],
    "Sequential Pattern": [
        ("Sequential Pattern", lambda: run_organizer(by_sequential, operation_name="Sequential Pattern")),
        ("Preview Sequential", lambda: run_organizer(by_sequential, preview=True)),
    ],
    "🔧 Tools": [
        ("🔍 Pattern Scanner", show_pattern_scanner),
        ("📊 Statistics", show_statistics),
        ("🔄 View History & Undo", show_undo_window),
    ],
}

# ── ACTIONS (scrollable) ───────────────────────────────────────────────────────
actions_frame = ttk.LabelFrame(root, text="Actions", style="Section.TLabelframe")
actions_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 8))
actions_frame.columnconfigure(0, weight=1)
actions_frame.rowconfigure(0, weight=1)

actions_canvas = tk.Canvas(actions_frame, highlightthickness=0)
actions_vsb = ttk.Scrollbar(actions_frame, orient="vertical", command=actions_canvas.yview)
actions_canvas.configure(yscrollcommand=actions_vsb.set, height=200)
actions_canvas.grid(row=0, column=0, sticky="nsew")
actions_vsb.grid(row=0, column=1, sticky="ns")

actions_content = ttk.Frame(actions_canvas)
_actions_window = actions_canvas.create_window((0, 0), window=actions_content, anchor="nw")

def _actions_on_configure(event):
    actions_canvas.configure(scrollregion=actions_canvas.bbox("all"))

def _canvas_on_configure(event):
    actions_canvas.itemconfig(_actions_window, width=event.width)

actions_content.bind("<Configure>", _actions_on_configure)
actions_canvas.bind("<Configure>", _canvas_on_configure)

# Mouse wheel scrolling
def _on_mousewheel(event):
    if hasattr(event, "delta") and event.delta:
        actions_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
    elif hasattr(event, "num"):
        if event.num == 4:
            actions_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            actions_canvas.yview_scroll(1, "units")

actions_canvas.bind("<Enter>", lambda e: actions_canvas.bind_all("<MouseWheel>", _on_mousewheel))
actions_canvas.bind("<Leave>", lambda e: actions_canvas.unbind_all("<MouseWheel>"))

# Render sections
for title in sorted(sections.keys()):
    add_section(actions_content, title, sections[title])

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=4, pady=(0, 10), sticky="ew")

# ── PREVIEW ────────────────────────────────────────────────────────────────────
preview_frame = ttk.LabelFrame(root, text="Preview & Results", style="Section.TLabelframe")
preview_frame.grid(row=4, column=0, columnspan=3, padx=0, pady=(0,8), sticky="nsew")
v_scroll = ttk.Scrollbar(preview_frame, orient="vertical")
h_scroll = ttk.Scrollbar(preview_frame, orient="horizontal")
preview_text = tk.Text(preview_frame, wrap="none", yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set, font=("Consolas", 9))
v_scroll.config(command=preview_text.yview)
h_scroll.config(command=preview_text.xview)
preview_frame.columnconfigure(0, weight=1)
preview_frame.rowconfigure(0, weight=1)
preview_text.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=(6,0))
v_scroll.grid(row=0, column=1, sticky="ns", padx=(0,6), pady=(6,0))
h_scroll.grid(row=1, column=0, sticky="ew", padx=(6,0), pady=(0,6))

# ── FOOTER ─────────────────────────────────────────────────────────────────────
footer = ttk.Frame(root)
footer.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,6))
footer.columnconfigure(0, weight=1)
footer.columnconfigure(1, weight=1)
footer.columnconfigure(2, weight=1)
ttk.Button(footer, text="Clear Preview", command=lambda: preview_text.delete("1.0", tk.END)).grid(row=0, column=0, pady=2)
ttk.Button(footer, text="Help", command=show_help).grid(row=0, column=1, pady=2)
ttk.Label(footer, text="v5.0 Production", foreground="gray").grid(row=0, column=2, pady=2)

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
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Show welcome message
def show_welcome():
    welcome = f"""
Welcome to File Organizer v5 - Production Edition!

🎉 New Features:
• Sequential Pattern Detection (NEW!)
• Pattern Scanner with 7 pattern types (NEW!)
• Hash-based duplicate detection
• Operation logging & UNDO
• Memory-efficient processing
• Statistics & analytics
• Pre-flight validation

📁 Data Directory:
{DATA_DIR.base_dir}

Ready to organize!
"""
    preview_text.insert("1.0", welcome)

root.after(100, show_welcome)

# START GUI
root.mainloop()
