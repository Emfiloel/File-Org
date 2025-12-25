# ==============================
# FILE ORGANIZER v7.0
# Professional File Organization Tool
# ==============================
# VERSION 7.0 FEATURES:
# 🧠 AI Pattern Learning (intelligent 4-tier detection system)
# 🔀 Advanced Collision Detection (date-aware EXIF duplicate handling)
# 🏠 Enhanced In-Place Organization (smart subfolder preservation)
# 📊 Pattern Analytics Dashboard
# 🗂️ Code Consolidation (82% reduction in duplication)
#
# VERSION 6.2 FEATURES (PRESERVED):
# ✅ In-Place Organization Mode (organize within same folder)
# ✅ Skip folders with # prefix (e.g., #Sort)
#
# VERSION 6.1 FEATURES (PRESERVED):
# ✅ VERSION constant for consistent labeling
# ✅ Case-insensitive Windows path security check
# ✅ Windows reserved folder name sanitization (Critical #36 fix)
# ✅ Improved duplicate cache documentation
#
# VERSION 6 FEATURES (PRESERVED):
# ✅ Threading for responsive GUI
# ✅ Path traversal security protection
# ✅ TOCTOU-safe atomic operations
# ✅ Extract functionality restored
# ✅ Enhanced help menu
# ✅ Sequential Pattern Detection
# ✅ Pattern Scanner with 7 pattern types
# ✅ Centralized data directory (.file_organizer_data/)
# ✅ Operation logging with UNDO functionality
# ✅ Hash-based duplicate detection (MD5)
# ✅ Memory-efficient processing (generators, chunking)
# ✅ Configuration system
# ✅ Pre-flight validation
# ✅ Comprehensive error reporting
# ✅ Statistics and analytics
# ✅ Safety features and rollback
# ==============================

import os
import re
import shutil
import json
import hashlib
import sqlite3
import time
import threading
import queue
import platform
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from typing import Iterator, Tuple, Dict, List, Optional, Callable, Any, Union

# ==============================
# VERSION & CONSTANTS
# ==============================
VERSION: str = "v7.1-dev"

# Note on duplicate cache semantics:
# DUPLICATE_DETECTOR.clear_session() is called per operation run,
# so the duplicate hash DB is effectively used as a fast, per-run cache.
# If you want cross-session de-duplication persistence, remove/guard the clear
# and add explicit reconciliation logic + tests. For v6.1 baseline we keep per-run.

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
            except (json.JSONDecodeError, ValueError) as e:
                APP_LOGGER.warning(f"Config file corrupted, using defaults: {e}")
                return self.DEFAULT_CONFIG.copy()
            except (IOError, OSError) as e:
                APP_LOGGER.error(f"Cannot read config file, using defaults: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: dict):
        """Save configuration to file"""
        try:
            with open(DATA_DIR.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            APP_LOGGER.error(f"Failed to save config: {e}")

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

    def undo_last_operation_with_progress(self, progress_callback: Callable[[int, int, str], None]) -> Tuple[bool, str, int, int]:
        """
        Undo the last operation with progress updates.

        Args:
            progress_callback: Function called with (current, total, filename) for progress updates

        Returns:
            Tuple of (success, message, moved_count, total_count)
        """
        recent = self.get_recent_operations(1)
        if not recent:
            return False, "No operations to undo", 0, 0

        operation = recent[0]
        moves = operation["moves"]
        total = len(moves)
        moved_back = 0
        errors = []

        # Move files back in reverse order
        for i, move in enumerate(reversed(moves), 1):
            filename = os.path.basename(move["to"])

            # Send progress update
            if progress_callback:
                progress_callback(i, total, filename)

            try:
                if os.path.exists(move["to"]):
                    os.makedirs(os.path.dirname(move["from"]), exist_ok=True)
                    shutil.move(move["to"], move["from"])
                    moved_back += 1
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")

        if errors:
            message = f"Undone {moved_back}/{total} files. {len(errors)} errors occurred."
        else:
            message = f"Successfully undone all {moved_back} file moves"

        return True, message, moved_back, total

# Global logger instance
LOGGER = OperationLogger()

# ==============================
# ENHANCED STRUCTURED LOGGING
# ==============================
class FileOrganizerLogger:
    """
    Enhanced logging with rotation and structured output.

    Features:
    - Rotating log files (5MB max, 3 backups)
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Formatted output with timestamp, level, function name, line number
    - Thread-safe logging
    """

    def __init__(self, log_dir: Path):
        self.log_file = log_dir / "file_organizer.log"
        self.logger = logging.getLogger("FileOrganizer")
        self.logger.setLevel(logging.DEBUG)

        # Remove any existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Rotating file handler (5MB max, 3 backups)
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )

        # Format with timestamp, level, function name, line number, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)-8s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg: str, **kwargs):
        """Debug level logging"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.debug(f"{msg}{extra_info}")

    def info(self, msg: str, **kwargs):
        """Info level logging"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.info(f"{msg}{extra_info}")

    def warning(self, msg: str, **kwargs):
        """Warning level logging"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.warning(f"{msg}{extra_info}")

    def error(self, msg: str, **kwargs):
        """Error level logging"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.error(f"{msg}{extra_info}")

    def critical(self, msg: str, **kwargs):
        """Critical level logging"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.critical(f"{msg}{extra_info}")

    def exception(self, msg: str):
        """Log exception with stack trace"""
        self.logger.exception(msg)

# Global enhanced logger instance
APP_LOGGER = FileOrganizerLogger(DATA_DIR.base_dir)

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
        except FileNotFoundError:
            return None
        except PermissionError:
            return None
        except (IOError, OSError):
            return None

    def check_duplicate(self, filename: str, size: int, filepath: str) -> Tuple[bool, str]:
        """
        Check if file is duplicate.
        Returns: (is_duplicate, duplicate_type)
        - (False, '') = First occurrence
        - (True, 'DUPES') = Same name + size + hash (converted to !Dupes by caller)
        - (True, 'DUPE SIZE') = Same name + different size (converted to !Dupes Size by caller)
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
# CONSOLIDATION: MESSAGES & VALIDATION HELPERS
# ==============================
class Messages:
    """Centralized user messaging - consolidates 34+ messagebox calls"""

    # Error messages
    NO_SOURCE = "Please select at least one source directory."
    NO_TARGET = "Please select a target directory first."
    INVALID_SOURCE = "Source directory does not exist or is not accessible."
    INVALID_TARGET = "Target directory does not exist or is not accessible."
    SAME_SOURCE_TARGET = "Source and target directories cannot be the same."
    PROTECTED_DIRECTORY = "Cannot organize protected system directories."
    NO_FILES = "No files found to organize in the selected directory."

    # Success messages
    OPERATION_SUCCESS = "Operation completed successfully!"
    UNDO_SUCCESS = "Undo operation completed successfully!"

    # Info messages
    OPERATION_CANCELLED = "Operation cancelled by user."
    PREVIEW_MODE = "Preview mode - no files will be moved."

    @staticmethod
    def error(msg: str, title: str = "Error"):
        """Show error message"""
        messagebox.showerror(title, msg)

    @staticmethod
    def info(msg: str, title: str = "Information"):
        """Show info message"""
        messagebox.showinfo(title, msg)

    @staticmethod
    def warning(msg: str, title: str = "Warning"):
        """Show warning message"""
        messagebox.showwarning(title, msg)

    @staticmethod
    def confirm(msg: str, title: str = "Confirm") -> bool:
        """Show confirmation dialog"""
        return messagebox.askyesno(title, msg)


def validate_sources(show_errors: bool = True) -> Tuple[bool, List[str]]:
    """
    Validate source directories - consolidates 6 duplicate validation blocks.

    Args:
        show_errors: Whether to show error dialogs

    Returns:
        (is_valid, list_of_source_paths)
    """
    sources_text = source_entry.get().strip()

    if not sources_text:
        if show_errors:
            Messages.error(Messages.NO_SOURCE)
        return False, []

    # Split by newlines or semicolons
    sources = [s.strip() for s in re.split(r'[\n;]', sources_text) if s.strip()]

    if not sources:
        if show_errors:
            Messages.error(Messages.NO_SOURCE)
        return False, []

    # Validate each source
    for src in sources:
        if not os.path.isdir(src):
            if show_errors:
                Messages.error(f"Source directory does not exist:\n{src}")
            return False, []

    return True, sources


def validate_target(show_errors: bool = True) -> Tuple[bool, str]:
    """
    Validate target directory - consolidates 6 duplicate validation blocks.

    Args:
        show_errors: Whether to show error dialogs

    Returns:
        (is_valid, target_path)
    """
    target = target_entry.get().strip()

    if not target:
        if show_errors:
            Messages.error(Messages.NO_TARGET)
        return False, ""

    if not os.path.isdir(target):
        if show_errors:
            Messages.error(Messages.INVALID_TARGET)
        return False, ""

    return True, target


class OperationResult:
    """Build and display operation results - consolidates 5 duplicate result displays"""

    def __init__(self, title: str = "Operation Results"):
        self.title = title
        self.lines = []

    def add(self, label: str, value: int, condition: bool = True) -> 'OperationResult':
        """Add a result line (chainable)"""
        if condition:
            self.lines.append(f"{label}: {value}")
        return self

    def add_text(self, text: str, condition: bool = True) -> 'OperationResult':
        """Add custom text line (chainable)"""
        if condition:
            self.lines.append(text)
        return self

    def show(self):
        """Display the results"""
        if self.lines:
            Messages.info("\n".join(self.lines), self.title)

    def __str__(self) -> str:
        """Get results as string"""
        return "\n".join(self.lines)

# ==============================
# THREADING SUPPORT
# ==============================
class OperationManager:
    """
    Thread-safe operation management for concurrent file operations.

    Provides centralized management of:
    - Current operation thread
    - Cancellation signals
    - Thread-safe state access
    """

    def __init__(self):
        self._current_thread: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()
        self._lock = threading.Lock()
        self._user_map_lock = threading.Lock()

    def start_operation(self, target, *args, **kwargs) -> Tuple[bool, str]:
        """
        Start operation with proper locking.

        Args:
            target: Function to run in thread
            *args, **kwargs: Arguments for target function

        Returns:
            (success, message): Tuple indicating if operation started successfully
        """
        with self._lock:
            if self._current_thread and self._current_thread.is_alive():
                return False, "Operation already in progress"

            self._cancel_event.clear()
            self._current_thread = threading.Thread(
                target=target,
                args=args,
                kwargs=kwargs,
                daemon=True
            )
            self._current_thread.start()
            return True, "Operation started"

    def cancel_operation(self):
        """Thread-safe cancellation"""
        with self._lock:
            self._cancel_event.set()

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self._cancel_event.is_set()

    def is_operation_running(self) -> bool:
        """Check if an operation is currently running"""
        with self._lock:
            return self._current_thread is not None and self._current_thread.is_alive()

    def update_user_map(self, key: str, value: str):
        """Thread-safe USER_MAP update"""
        with self._user_map_lock:
            USER_MAP[key] = value
            save_mappings()

    def get_user_map_value(self, key: str) -> Optional[str]:
        """Thread-safe USER_MAP read"""
        with self._user_map_lock:
            return USER_MAP.get(key)

# Global instance
OPERATION_MANAGER = OperationManager()

# Legacy global variables for backward compatibility
# These are now deprecated in favor of OPERATION_MANAGER
current_operation_thread = None
cancel_event = threading.Event()
operation_queue = queue.Queue()

def cancel_operation():
    """
    Cancel the currently running operation.

    DEPRECATED: Use OPERATION_MANAGER.cancel_operation() instead.
    This function is maintained for backward compatibility.
    """
    OPERATION_MANAGER.cancel_operation()

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

root.title(f"File Organizer — {VERSION}")

# ── THEME ──────────────────────────────────────────────────────────────────────
style = ttk.Style()
theme = CONFIG.get('ui.theme', 'clam')
for t in (theme, "clam", "vista", "xpnative", "default"):
    try:
        style.theme_use(t)
        break
    except tk.TclError:
        # Theme not available, try next option
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
ttk.Label(header, text=f"File Organizer — {VERSION}", style="Title.TLabel").pack(side="left")

# ── SOURCE/TARGET ──────────────────────────────────────────────────────────────
paths_box = ttk.LabelFrame(root, text="Locations", style="Section.TLabelframe")
paths_box.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=(8, 12))
paths_box.columnconfigure(1, weight=1)

ttk.Label(paths_box, text="Source Directory(ies):").grid(row=0, column=0, sticky="e", padx=(8,6), pady=6)
source_entry = ttk.Combobox(paths_box, values=[])  # v6.3: Recent directories dropdown
source_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

def browse_source():
    """Browse for source directory and add to history"""
    path = filedialog.askdirectory()
    if path:
        source_entry.set(path)
        add_to_recent('source', path)

ttk.Button(paths_box, text="Browse", command=browse_source).grid(row=0, column=2, padx=(6,8), pady=6)

ttk.Label(paths_box, text="Target Directory:").grid(row=1, column=0, sticky="e", padx=(8,6), pady=6)
target_entry = ttk.Combobox(paths_box, values=[])  # v6.3: Recent directories dropdown
target_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=6)

def browse_target():
    """Browse for target directory and add to history"""
    path = filedialog.askdirectory()
    if path:
        target_entry.set(path)
        add_to_recent('target', path)

ttk.Button(paths_box, text="Browse", command=browse_target).grid(row=1, column=2, padx=(6,8), pady=6)

# In-Place Organization checkbox
inplace_organize_var = tk.BooleanVar(value=False)
ttk.Checkbutton(
    paths_box,
    text="✓ Organize within same folder (source = target)",
    variable=inplace_organize_var
).grid(row=2, column=0, columnspan=3, sticky="w", padx=(8,6), pady=(6,8))

# Folder creation tool variables (v6.3)
var_create_az = tk.BooleanVar(value=True)
var_create_09 = tk.BooleanVar(value=True)
var_create_special = tk.BooleanVar(value=True)
var_folder_case = tk.StringVar(value="upper")

# Pattern search variables (v6.3)
var_search_pattern = tk.StringVar(value="")
var_search_folder = tk.StringVar(value="")

# ==============================
# RECENT DIRECTORIES (v6.3)
# ==============================
def load_recent_directories():
    """Load recent directories from config and populate dropdowns"""
    recent = CONFIG.get("recent_directories", {"source": [], "target": []})
    source_recent = recent.get("source", [])
    target_recent = recent.get("target", [])

    source_entry['values'] = source_recent[:10]  # Keep last 10
    target_entry['values'] = target_recent[:10]

    # Set first item as default if available
    if source_recent:
        source_entry.set(source_recent[0])
    if target_recent:
        target_entry.set(target_recent[0])

def add_to_recent(entry_type, path):
    """Add a directory to recent history"""
    if not path or not os.path.isdir(path):
        return

    recent = CONFIG.get("recent_directories", {"source": [], "target": []})
    if entry_type not in recent:
        recent[entry_type] = []

    # Remove if already exists (will be re-added to front)
    if path in recent[entry_type]:
        recent[entry_type].remove(path)

    # Add to front
    recent[entry_type].insert(0, path)

    # Keep only last 10
    recent[entry_type] = recent[entry_type][:10]

    # Save to config
    CONFIG.set("recent_directories", recent)

    # Update dropdown
    if entry_type == "source":
        source_entry['values'] = recent[entry_type]
    else:
        target_entry['values'] = recent[entry_type]

# ==============================
# CORE HELPERS
# ==============================
def get_source_dirs() -> List[str]:
    return [d.strip() for d in source_entry.get().split(',') if os.path.isdir(d.strip())]

def should_skip_folder(folder_name: str) -> bool:
    """
    Check if folder should be skipped.

    Skips:
    - Folders in config skip_folders list
    - Folders starting with # immediately followed by non-space (e.g., #Sort, #Archive)
    - Does NOT skip folders with space after # (e.g., "# Sorting")
    """
    # Skip folders starting with # followed immediately by non-space character
    # #Sort → skip (# followed by S)
    # # Sorting → do NOT skip (# followed by space)
    if folder_name.startswith('#') and (len(folder_name) == 1 or folder_name[1] != ' '):
        return True

    # Skip folders in config list
    skip_list = CONFIG.get('skip_folders', ['Sort'])
    return folder_name in skip_list

def is_safe_directory(path: str) -> Tuple[bool, str]:
    """
    Validate that a directory is safe to organize.

    Prevents organizing system directories that could damage the OS.

    Args:
        path: Directory path to validate

    Returns:
        (is_safe, reason) - True if safe, False with reason if not
    """
    try:
        # Get the absolute, canonical path (resolves symlinks, .., etc.)
        real_path = os.path.abspath(os.path.realpath(path))

        # Define forbidden directories by operating system
        system = platform.system()

        if system == "Windows":
            forbidden_starts = [
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\ProgramData",
                os.environ.get("SystemRoot", ""),
            ]
        elif system == "Darwin":  # macOS
            forbidden_starts = [
                "/System",
                "/Library",
                "/Applications",
                "/usr",
                "/bin",
                "/sbin",
                "/etc",
            ]
        else:  # Linux and others
            forbidden_starts = [
                "/bin",
                "/boot",
                "/dev",
                "/etc",
                "/lib",
                "/proc",
                "/root",
                "/sbin",
                "/sys",
                "/usr",
                "/var",
            ]

        # Remove empty strings and normalize paths (case-insensitive safety on Windows)
        forbidden_starts = [os.path.abspath(p) for p in forbidden_starts if p]

        # Prepare for case-insensitive comparison on Windows
        if system == "Windows":
            real_cmp = real_path.casefold()
            forb_cmp = [f.casefold() for f in forbidden_starts]
        else:
            real_cmp = real_path
            forb_cmp = forbidden_starts

        # Check if path starts with any forbidden directory
        for forbidden, forbidden_cmp in zip(forbidden_starts, forb_cmp):
            if real_cmp.startswith(forbidden_cmp):
                return False, f"Cannot organize system directory: {forbidden}"

        # Check if path is writable
        if not os.access(real_path, os.W_OK):
            return False, f"Directory is not writable: {path}"

        return True, ""

    except (OSError, ValueError, PermissionError, TypeError) as e:
        return False, f"Invalid path: {str(e)}"

def report_error(title: str, message: str):
    sep = "-" * 70
    try:
        preview_text.insert("end", f"\n{sep}\n{title}: {message}\n{sep}\n")
        preview_text.see("end")
    except (AttributeError, tk.TclError):
        # Widget doesn't exist or isn't ready, fall back to console
        print(f"[{title}] {message}")

def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes.

    Returns:
        File size in bytes, or -1 if error occurs
    """
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        # File doesn't exist
        return -1
    except PermissionError:
        # No permission to access file
        return -1
    except OSError as e:
        # Other OS errors (network issues, invalid path, etc.)
        return -1

def get_file_datetime(filepath: str) -> Optional[datetime]:
    """
    Extract date/time from file with priority:
    1. EXIF Date/Time Original (for photos)
    2. File modification time (fallback)

    Returns datetime object or None
    """
    try:
        # Try to get EXIF data for images
        if filepath.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
            try:
                # Try to import PIL for EXIF data
                from PIL import Image
                from PIL.ExifTags import TAGS

                img = Image.open(filepath)
                exif_data = img._getexif()

                if exif_data:
                    # Look for DateTimeOriginal tag (36867) or DateTime tag (306)
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name in ('DateTimeOriginal', 'DateTime'):
                            # Parse EXIF datetime format: "2024:01:15 10:30:00"
                            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            except (ImportError, AttributeError):
                pass  # PIL not available or no EXIF data
            except (OSError, ValueError):
                pass  # Cannot read EXIF or parse datetime

        # Fallback: use file modification time
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime)

    except FileNotFoundError:
        return None  # File doesn't exist
    except PermissionError:
        return None  # No permission to access file
    except (OSError, ValueError) as e:
        return None  # Cannot get file time or convert to datetime

def move_file(src: str, dst_folder: str, filename: str) -> bool:
    """
    Move file with advanced collision detection and duplicate handling.

    Collision Logic:
    - [d] suffix: Same size (exact duplicate indicator)
    - {d} suffix: Different size (different version indicator)
    - !Dupes folder: Same name + same size + same date
    - !Dupes Size folder: Same name + different size + same date
    """
    # Pre-flight check: verify source still exists
    if not os.path.exists(src):
        LOGGER.log_error("Source file no longer exists", filename)
        return False

    try:
        os.makedirs(dst_folder, exist_ok=True)
    except (OSError, PermissionError) as e:
        LOGGER.log_error(f"Cannot create destination folder: {e}", filename)
        return False

    # Pre-flight check
    if CONFIG.get('safety.validate_before_move', True):
        if not os.access(dst_folder, os.W_OK):
            LOGGER.log_error("No write permission", filename)
            return False

    base, ext = os.path.splitext(filename)
    dst = os.path.join(dst_folder, filename)

    # Check for collision
    if os.path.exists(dst):
        # Collision detected - apply advanced duplicate detection
        src_size = get_file_size(src)
        dst_size = get_file_size(dst)
        src_date = get_file_datetime(src)
        dst_date = get_file_datetime(dst)

        # Determine if same size
        same_size = (src_size == dst_size)

        # Determine if same date (within 1 second tolerance)
        same_date = False
        if src_date and dst_date:
            time_diff = abs((src_date - dst_date).total_seconds())
            same_date = (time_diff < 1)  # Same if within 1 second

        # Decision matrix
        target_root = os.path.dirname(dst_folder)

        if same_size and same_date:
            # Case: Same size + same date → !Dupes folder with [d] suffix
            dup_folder = os.path.join(target_root, "!Dupes")
            os.makedirs(dup_folder, exist_ok=True)
            new_filename = f"{base}[d]{ext}"
            dst = os.path.join(dup_folder, new_filename)

        elif not same_size and same_date:
            # Case: Different size + same date → !Dupes Size folder with {d} suffix
            dup_folder = os.path.join(target_root, "!Dupes Size")
            os.makedirs(dup_folder, exist_ok=True)
            new_filename = f"{base}{{d}}{ext}"
            dst = os.path.join(dup_folder, new_filename)

        elif same_size and not same_date:
            # Case: Same size + different date → Keep in target folder with [d] suffix
            new_filename = f"{base}[d]{ext}"
            dst = os.path.join(dst_folder, new_filename)

        else:
            # Case: Different size + different date → Keep in target folder with {d} suffix
            new_filename = f"{base}{{d}}{ext}"
            dst = os.path.join(dst_folder, new_filename)

        # Handle nested collisions (if [d] or {d} already exists)
        counter = 2
        while os.path.exists(dst):
            # Add counter to suffix: file[d]2.jpg, file{d}2.jpg, etc.
            if same_size:
                new_filename = f"{base}[d]{counter}{ext}"
            else:
                new_filename = f"{base}{{d}}{counter}{ext}"

            # Update dst path
            if same_size and same_date:
                dst = os.path.join(os.path.join(target_root, "!Dupes"), new_filename)
            elif not same_size and same_date:
                dst = os.path.join(os.path.join(target_root, "!Dupes Size"), new_filename)
            else:
                dst = os.path.join(dst_folder, new_filename)

            counter += 1
            if counter > 100:
                LOGGER.log_error(f"Too many collisions (>{counter})", filename)
                return False

    # Attempt move
    try:
        # Final check before move
        if not os.path.exists(src):
            LOGGER.log_error("Source file disappeared just before move", filename)
            return False

        shutil.move(src, dst)

        # Success! Log the move
        size = get_file_size(dst)
        LOGGER.log_move(src, dst, size)
        return True

    except (IOError, OSError, PermissionError) as e:
        LOGGER.log_error(f"Failed to move: {e}", filename)
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
        except (json.JSONDecodeError, ValueError) as e:
            APP_LOGGER.warning(f"Mappings file corrupted, resetting: {e}")
            USER_MAP = {}
        except (IOError, OSError) as e:
            APP_LOGGER.error(f"Cannot read mappings file, resetting: {e}")
            USER_MAP = {}
def save_mappings():
    try:
        with open(DATA_DIR.mappings_file, "w", encoding="utf-8") as f:
            json.dump(USER_MAP, f, ensure_ascii=False, indent=2)
    except (IOError, OSError, PermissionError) as e:
        APP_LOGGER.error(f"Failed to save mappings: {e}")
def make_key(filename: str) -> str:
    base, _ = os.path.splitext(filename)
    base = re.sub(r'\s*[\-_]?\(\d+\)$', '', base)
    base = re.sub(r'(?<=[\-_])\d+[A-Za-z]?$', '', base)
    return base.strip().lower()
load_mappings()

# ==============================
# DETECTION HELPERS
# ==============================
def sanitize_folder_name(folder_name: str) -> str:
    """
    Sanitize folder name to avoid Windows reserved names.

    Windows reserved names: CON, PRN, AUX, NUL, COM1-9, LPT1-9

    Args:
        folder_name: The proposed folder name

    Returns:
        Safe folder name (appends '_' if reserved)
    """
    if not folder_name:
        return folder_name

    # Windows reserved names (case-insensitive)
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    # Check if the folder name (without any extension-like suffix) is reserved
    base_name = folder_name.split('.')[0].upper()

    if base_name in reserved_names:
        # Append underscore to make it safe
        return folder_name + '_'

    return folder_name

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
    return sanitize_folder_name(folder.rstrip(' .')) if folder else None

def extract_img_tag(filename: str) -> Optional[str]:
    m = re.search(r"(IMG|DSC|DSCN|DCS|DCSN)(?=\d|_|\.|$)", filename, re.IGNORECASE)
    return sanitize_folder_name(m.group(1).upper()) if m else None

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
            return sanitize_folder_name(base_name)
        return sanitize_folder_name(base_name.capitalize())

    # Pattern 2: BASE without separator followed by 2+ digits
    # Example: file001, vacation123
    # Must be letters followed by digits, or mixed alphanumeric
    m_no_sep = re.match(r'^([A-Za-z]+)(\d{2,})$', base)
    if m_no_sep:
        base_name = m_no_sep.group(1)
        # Capitalize if all lowercase or mixed case, keep uppercase as-is
        if base_name.isupper():
            return sanitize_folder_name(base_name)
        return sanitize_folder_name(base_name.capitalize())

    # Pattern 3: Numeric BASE with separator followed by 2+ digits
    # Example: 031204-0022, 20240101-001
    m_numeric = re.match(r'^(\d+)([-_])(\d{2,})$', base)
    if m_numeric:
        return sanitize_folder_name(m_numeric.group(1))

    return None

# ==============================
# INTELLIGENT PATTERN SCANNER (CONSOLIDATION)
# ==============================
class PatternLearner:
    """Machine learning for file patterns - learns from user choices"""

    def __init__(self):
        self.patterns_file = DATA_DIR.get_path("learned_patterns.json")
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load learned patterns from file"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError) as e:
                APP_LOGGER.warning(f"Patterns file corrupted, resetting: {e}")
                return {}
            except (IOError, OSError) as e:
                APP_LOGGER.error(f"Cannot read patterns file, resetting: {e}")
                return {}
        return {}

    def _save_patterns(self):
        """Save learned patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Failed to save learned patterns: {e}")

    def extract_signature(self, filename: str) -> str:
        """
        Extract pattern signature from filename.

        Examples:
            vacation-001.jpg → "TEXT-NNN"
            IMG_1234.jpg → "IMG_NNNN"
            file001.pdf → "TEXTNNN"
            031204-0022.jpg → "NNNNNN-NNNN"
        """
        base, _ = os.path.splitext(filename)

        # Build signature: TEXT, N (number), special chars preserved
        signature = []
        i = 0
        while i < len(base):
            char = base[i]
            if char.isdigit():
                # Count consecutive digits
                count = 0
                while i < len(base) and base[i].isdigit():
                    count += 1
                    i += 1
                signature.append('N' * count)
            elif char.isalpha():
                # Count consecutive letters
                text_part = []
                while i < len(base) and base[i].isalpha():
                    text_part.append(base[i])
                    i += 1
                # If uppercase camera tag (IMG, DSC), keep as-is
                text_str = ''.join(text_part)
                if text_str.isupper() and len(text_str) <= 5:
                    signature.append(text_str)
                else:
                    signature.append('TEXT')
            else:
                # Preserve special characters
                signature.append(char)
                i += 1

        return ''.join(signature)

    def learn(self, filename: str, folder: str):
        """Learn from user's folder choice"""
        signature = self.extract_signature(filename)

        if signature not in self.patterns:
            self.patterns[signature] = {
                "folder": folder,
                "count": 1,
                "examples": [filename]
            }
        else:
            # Update existing pattern
            pattern = self.patterns[signature]
            if pattern["folder"] == folder:
                pattern["count"] += 1
            else:
                # User chose different folder - reset or update based on frequency
                if pattern["count"] > 3:
                    # Strong pattern, create alternate
                    alt_sig = f"{signature}_ALT"
                    self.patterns[alt_sig] = {"folder": folder, "count": 1, "examples": [filename]}
                else:
                    # Weak pattern, replace
                    pattern["folder"] = folder
                    pattern["count"] = 1

            # Keep only last 5 examples
            if "examples" not in pattern:
                pattern["examples"] = []
            pattern["examples"].append(filename)
            pattern["examples"] = pattern["examples"][-5:]

        self._save_patterns()

    def predict(self, filename: str) -> Optional[Tuple[str, float]]:
        """
        Predict folder based on learned patterns.

        Returns:
            (folder_name, confidence) or None
        """
        signature = self.extract_signature(filename)

        if signature in self.patterns:
            pattern = self.patterns[signature]
            confidence = min(0.99, 0.80 + (pattern["count"] * 0.03))  # 0.80 to 0.99
            return pattern["folder"], confidence

        return None


class IntelligentPatternDetector:
    """Unified pattern detection with learning - consolidates 3 pattern detection methods"""

    def __init__(self):
        self.learner = PatternLearner()

    def detect(self, filename: str) -> Tuple[Optional[str], float, str]:
        """
        Detect folder for filename with confidence scoring.

        Returns:
            (folder_name, confidence, method)

        Detection priority:
            1. Learned patterns (0.80-0.99 confidence)
            2. Camera tags (0.95 confidence)
            3. Sequential patterns (0.90 confidence)
            4. Smart delimiter patterns (0.80 confidence)
        """
        # Priority 1: Check learned patterns
        learned = self.learner.predict(filename)
        if learned:
            folder, confidence = learned
            return folder, confidence, "Learned Pattern"

        # Priority 2: Camera tags (IMG, DSC, etc.)
        camera_tag = extract_img_tag(filename)
        if camera_tag:
            return camera_tag, 0.95, "Camera Tag"

        # Priority 3: Sequential patterns
        sequential = detect_sequential_pattern(filename)
        if sequential:
            return sequential, 0.90, "Sequential Pattern"

        # Priority 4: Smart delimiter patterns
        smart = detect_folder_name(filename)
        if smart:
            return smart, 0.80, "Smart Pattern"

        # No pattern detected
        return None, 0.0, "No Pattern"

    def learn_from_user_choice(self, filename: str, chosen_folder: str):
        """Learn from user's manual folder choice"""
        self.learner.learn(filename, chosen_folder)

# Global intelligent pattern detector
INTELLIGENT_DETECTOR = IntelligentPatternDetector()

# ==============================
# DATABASE SCANNER (LEARNING MODE)
# ==============================
class DatabaseScanner:
    """
    Scans directory structure to learn organization patterns.

    - Reads existing folder structures
    - Identifies organized vs unorganized areas
    - Learns from your current organization
    - Does NOT move files (read-only analysis)
    """

    def __init__(self):
        self.scan_results = {
            "total_files": 0,
            "total_folders": 0,
            "organized_files": 0,
            "unorganized_files": 0,
            "patterns_found": {},
            "folder_structure": {},
            "unorganized_areas": [],
            "learned_mappings": {}
        }
        self.unorganized_keywords = ["sorting", "sort", "unsorted", "to organize", "to sort", "temp", "temporary"]

    def is_unorganized_folder(self, folder_name: str) -> bool:
        """Check if folder name indicates unorganized area"""
        folder_lower = folder_name.lower()
        return any(keyword in folder_lower for keyword in self.unorganized_keywords)

    def scan_directory(self, root_path: str, progress_callback: Optional[Callable] = None) -> dict:
        """
        Scan directory and learn organization patterns.

        Returns scan results with:
        - Total files/folders count
        - Organized vs unorganized areas
        - Detected patterns
        - Learned folder mappings
        """
        self.scan_results = {
            "total_files": 0,
            "total_folders": 0,
            "organized_files": 0,
            "unorganized_files": 0,
            "patterns_found": {},
            "folder_structure": {},
            "unorganized_areas": [],
            "learned_mappings": {},
            "scan_date": datetime.now().isoformat(),
            "root_path": root_path
        }

        file_count = 0

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Skip system folders
            dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]

            self.scan_results["total_folders"] += len(dirnames)

            # Check if current folder is unorganized area
            folder_name = os.path.basename(dirpath)
            is_unorganized = self.is_unorganized_folder(folder_name)

            if is_unorganized:
                self.scan_results["unorganized_areas"].append({
                    "path": dirpath,
                    "folder": folder_name,
                    "file_count": len(filenames)
                })

            # Analyze files in this directory
            for filename in filenames:
                file_count += 1
                self.scan_results["total_files"] += 1

                if progress_callback and file_count % 100 == 0:
                    progress_callback(file_count, filename)

                # Classify as organized or unorganized
                if is_unorganized:
                    self.scan_results["unorganized_files"] += 1
                else:
                    self.scan_results["organized_files"] += 1
                    # Learn from organized files
                    self._learn_from_organized_file(filename, folder_name, dirpath, root_path)

        return self.scan_results

    def _learn_from_organized_file(self, filename: str, folder_name: str, full_path: str, root_path: str):
        """Learn pattern from file in organized folder"""
        # Extract pattern signature
        signature = INTELLIGENT_DETECTOR.learner.extract_signature(filename)

        # Record the mapping: pattern → folder
        if signature not in self.scan_results["learned_mappings"]:
            self.scan_results["learned_mappings"][signature] = {
                "folder": folder_name,
                "count": 0,
                "examples": []
            }

        mapping = self.scan_results["learned_mappings"][signature]
        mapping["count"] += 1

        if len(mapping["examples"]) < 5:
            mapping["examples"].append(filename)

        # Track folder structure
        rel_path = os.path.relpath(full_path, root_path)
        if folder_name not in self.scan_results["folder_structure"]:
            self.scan_results["folder_structure"][folder_name] = {
                "path": rel_path,
                "file_count": 0,
                "patterns": set()
            }

        self.scan_results["folder_structure"][folder_name]["file_count"] += 1
        self.scan_results["folder_structure"][folder_name]["patterns"].add(signature)

    def apply_learned_patterns_to_ai(self) -> int:
        """
        Apply learned patterns to the Intelligent Pattern Detector.

        Returns: Number of patterns applied
        """
        patterns_applied = 0

        for signature, data in self.scan_results["learned_mappings"].items():
            if data["count"] >= 2:  # Only learn patterns with 2+ occurrences
                folder = data["folder"]

                # Add to AI pattern learner
                for example in data["examples"]:
                    INTELLIGENT_DETECTOR.learner.learn(example, folder)

                patterns_applied += 1

        return patterns_applied

    def get_organization_insights(self) -> List[str]:
        """Get insights about organization patterns"""
        insights = []

        # Overall organization status
        if self.scan_results["total_files"] > 0:
            organized_pct = (self.scan_results["organized_files"] / self.scan_results["total_files"]) * 100
            insights.append(f"📊 {organized_pct:.1f}% of files are organized ({self.scan_results['organized_files']:,} / {self.scan_results['total_files']:,})")

        # Unorganized areas
        unorg_count = len(self.scan_results["unorganized_areas"])
        if unorg_count > 0:
            total_unorg_files = sum(area["file_count"] for area in self.scan_results["unorganized_areas"])
            insights.append(f"📁 Found {unorg_count} unorganized folder(s) with {total_unorg_files:,} files waiting to be sorted")

        # Most common folder
        if self.scan_results["folder_structure"]:
            most_used = max(self.scan_results["folder_structure"].items(),
                          key=lambda x: x[1]["file_count"])
            insights.append(f"🏆 Most used folder: '{most_used[0]}' with {most_used[1]['file_count']:,} files")

        # Pattern diversity
        pattern_count = len(self.scan_results["learned_mappings"])
        if pattern_count > 0:
            insights.append(f"🎯 Detected {pattern_count} unique file naming patterns")

        # Learnable patterns
        learnable = sum(1 for data in self.scan_results["learned_mappings"].values() if data["count"] >= 2)
        if learnable > 0:
            insights.append(f"🧠 {learnable} patterns are ready to be learned by AI Scanner")

        return insights

    def save_scan_results(self):
        """Save scan results to JSON file"""
        scan_file = DATA_DIR.get_path("scan_results.json")
        try:
            # Convert sets to lists for JSON serialization
            results_copy = dict(self.scan_results)
            for folder_data in results_copy.get("folder_structure", {}).values():
                if "patterns" in folder_data:
                    folder_data["patterns"] = list(folder_data["patterns"])

            with open(scan_file, 'w') as f:
                json.dump(results_copy, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            APP_LOGGER.error(f"Failed to save scan results: {e}")

    def load_scan_results(self) -> bool:
        """Load previous scan results"""
        scan_file = DATA_DIR.get_path("scan_results.json")
        if scan_file.exists():
            try:
                with open(scan_file, 'r') as f:
                    self.scan_results = json.load(f)

                # Convert lists back to sets
                for folder_data in self.scan_results.get("folder_structure", {}).values():
                    if "patterns" in folder_data and isinstance(folder_data["patterns"], list):
                        folder_data["patterns"] = set(folder_data["patterns"])

                return True
            except (json.JSONDecodeError, ValueError) as e:
                APP_LOGGER.warning(f"Scan results file corrupted: {e}")
                return False
            except (IOError, OSError) as e:
                APP_LOGGER.error(f"Cannot read scan results file: {e}")
                return False
        return False

# Global database scanner
DATABASE_SCANNER = DatabaseScanner()

# ==============================
# PRE-FLIGHT VALIDATION
# ==============================
def validate_operation(source_dirs: List[str], target_dir: str) -> Tuple[bool, List[str]]:
    """
    Validate operation before execution with security checks.
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
        else:
            # Security check: validate source is safe
            is_safe, reason = is_safe_directory(src)
            if not is_safe:
                issues.append(f"🔒 {reason}")

    # Check target directory
    if not target_dir:
        issues.append("❌ No target directory selected")
    elif not os.path.exists(target_dir):
        issues.append(f"❌ Target does not exist: {target_dir}")
    elif not os.path.isdir(target_dir):
        issues.append(f"❌ Target is not a directory: {target_dir}")
    elif not os.access(target_dir, os.W_OK):
        issues.append(f"❌ No write permission for target: {target_dir}")
    else:
        # Security check: validate target is safe
        is_safe, reason = is_safe_directory(target_dir)
        if not is_safe:
            issues.append(f"🔒 {reason}")

    # Check if target is inside source (skip check if in-place organization mode enabled)
    # In-place mode allows organizing within the same folder (source == target)
    if not inplace_organize_var.get():  # Only validate if NOT in in-place mode
        for src in source_dirs:
            try:
                if os.path.commonpath([os.path.abspath(target_dir), os.path.abspath(src)]) == os.path.abspath(src):
                    issues.append(f"❌ Target cannot be inside source: {src}")
            except ValueError:
                # Paths are on different drives (Windows) or incompatible, which is fine
                pass

    # Check available space
    try:
        if target_dir and os.path.exists(target_dir):
            stat = shutil.disk_usage(target_dir)
            free_gb = stat.free / (1024**3)
            if free_gb < 1:
                issues.append(f"⚠ Low disk space: {free_gb:.2f} GB free")
    except (OSError, FileNotFoundError):
        # Can't check disk space, but don't block the operation
        pass

    return len(issues) == 0, issues

# ==============================
# MEMORY-EFFICIENT FILE COLLECTION
# ==============================
def collect_files_generator(source_dirs: List[str], logic_func) -> Iterator[Tuple[str, str, str]]:
    """
    Memory-efficient file collection using generators.
    Yields: (source_path, destination_folder, filename)

    In-place mode: Only organizes files in root directory, skips files already in subfolders.
    """
    target_root = (target_entry.get() or "").strip()
    seen_files = {}  # {filename: {sizes: [], hashes: [], count: N}}

    use_hash = CONFIG.get('duplicate_detection.method') == 'hash'
    inplace_mode = inplace_organize_var.get()

    for source in source_dirs:
        for dirpath, dirnames, files in os.walk(source):
            # In-place mode: Skip files already in subfolders (only organize root files)
            if inplace_mode and os.path.abspath(dirpath) != os.path.abspath(source):
                continue

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
                            # Update folder names to use ! prefix
                            if dup_type == "DUPES":
                                dup_type = "!Dupes"
                            elif dup_type == "DUPE SIZE":
                                dup_type = "!Dupes Size"
                            yield (src, os.path.join(target_root, dup_type), new_filename)
                            continue
                    else:
                        # Size-only detection
                        if file_size in seen_files[file]['sizes']:
                            LOGGER.log_duplicate()
                            yield (src, os.path.join(target_root, "!Dupes"), new_filename)
                            continue
                        else:
                            seen_files[file]['sizes'].append(file_size)
                            yield (src, os.path.join(target_root, "!Dupes Size"), new_filename)
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
# ORGANIZER ENGINE (THREADED)
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

    # Check if operation already running
    if OPERATION_MANAGER.is_operation_running():
        messagebox.showwarning("Busy", "⚠ An operation is already in progress. Please wait or cancel it first.")
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
            # For preview, collect first 1000 items (no threading needed)
            preview_items = []
            for i, (src, dst_folder, fname) in enumerate(file_gen):
                if i >= 1000:
                    break
                preview_items.append((src, os.path.relpath(dst_folder, target_dir), fname))
            show_preview(preview_items)
            LOGGER.end_operation()
            return

        # Execute moves in background thread for GUI responsiveness
        def worker_thread():
            """Background thread for file operations"""
            total = 0
            moved = 0
            progress_update_interval = CONFIG.get('performance.progress_update_interval', 1000)

            try:
                for src, dst_folder, fname in file_gen:
                    # Check if user cancelled
                    if OPERATION_MANAGER.is_cancelled():
                        operation_queue.put({'type': 'cancelled', 'total': total, 'moved': moved})
                        return

                    total += 1
                    if move_file(src, dst_folder, fname):
                        moved += 1

                    # Send progress update via queue
                    if total % progress_update_interval == 0:
                        operation_queue.put({'type': 'progress', 'total': total, 'moved': moved})

                # Operation complete
                operation_queue.put({'type': 'complete', 'total': total, 'moved': moved})
            except (IOError, OSError, PermissionError) as e:
                operation_queue.put({'type': 'error', 'message': f"File operation error: {str(e)}"})
            except Exception as e:
                operation_queue.put({'type': 'error', 'message': f"Unexpected error: {str(e)}"})

        # Start worker thread using OperationManager
        success, msg = OPERATION_MANAGER.start_operation(worker_thread)
        if not success:
            messagebox.showwarning("Busy", f"⚠ {msg}")
            LOGGER.end_operation()
            return

        # Start progress monitoring
        progress_bar["mode"] = "indeterminate"
        progress_bar.start()
        monitor_operation_progress()

def monitor_operation_progress():
    """Monitor the operation queue and update GUI (called from main thread)"""
    try:
        # Check queue for updates
        while not operation_queue.empty():
            message = operation_queue.get_nowait()

            if message['type'] == 'progress':
                # Update progress display
                total = message['total']
                moved = message['moved']
                preview_text.delete("1.0", tk.END)
                preview_text.insert("1.0", f"Processing... {moved}/{total} files moved")

            elif message['type'] == 'complete':
                # Operation finished successfully
                progress_bar.stop()
                progress_bar["mode"] = "determinate"
                progress_bar["maximum"] = message['total']
                progress_bar["value"] = message['moved']

                # End operation logging
                LOGGER.end_operation()

                # Show summary
                stats = LOGGER.operations[-1]["stats"] if LOGGER.operations else {}
                msg = f"✓ Operation Complete!\n\n"
                msg += f"Files processed: {message['total']}\n"
                msg += f"Files moved: {message['moved']}\n"
                msg += f"Duplicates: {stats.get('duplicates_found', 0)}\n"
                if stats.get('errors', 0) > 0:
                    msg += f"\n⚠ Errors: {stats['errors']}"
                messagebox.showinfo("Complete", msg)
                return  # Stop monitoring

            elif message['type'] == 'cancelled':
                # User cancelled operation
                progress_bar.stop()
                progress_bar["mode"] = "determinate"
                LOGGER.end_operation()
                messagebox.showinfo("Cancelled", f"Operation cancelled.\n\n{message['moved']}/{message['total']} files moved before cancellation.")
                return  # Stop monitoring

            elif message['type'] == 'error':
                # Error occurred
                progress_bar.stop()
                LOGGER.end_operation()
                messagebox.showerror("Error", f"Operation failed:\n\n{message['message']}")
                return  # Stop monitoring

        # Continue monitoring (check again in 100ms)
        root.after(100, monitor_operation_progress)

    except queue.Empty:
        # Queue is empty, keep monitoring
        root.after(100, monitor_operation_progress)

# ==============================
# EXTRACT FUNCTIONS (RESTORED FROM V2)
# ==============================
def extract_files(levels: Optional[int] = None):
    """
    Unified file extraction function - consolidates extract_all_to_parent() and extract_up_levels().

    Args:
        levels: None = extract all to parent (all levels)
                int = extract N levels up (1-10)
    """
    # Validate source directories
    is_valid, source_dirs = validate_sources()
    if not is_valid:
        return

    # Safety validation
    for src in source_dirs:
        is_safe, reason = is_safe_directory(src)
        if not is_safe:
            Messages.error(reason, "Unsafe Directory")
            return

    # Determine operation name and title
    if levels is None:
        operation_name = "Extract All to Parent"
        title = "Extract"
        success_title = "Extract Complete"
    else:
        operation_name = f"Extract Up {levels} Levels"
        title = "Extract Up"
        success_title = "Extract Up Complete"

    # Start operation logging
    LOGGER.start_operation(operation_name, source_dirs, source_dirs[0])

    # Build plan
    plan = []
    for source in source_dirs:
        for dirpath, _, files in os.walk(source):
            # For extract to parent: skip files already in parent
            if levels is None and os.path.abspath(dirpath) == os.path.abspath(source):
                continue

            for fname in files:
                src = os.path.join(dirpath, fname)

                # Calculate destination
                if levels is None:
                    # Extract to parent (source directory)
                    dest_dir = source
                else:
                    # Extract N levels up
                    dest_dir = dirpath
                    for _ in range(levels):
                        dest_dir = os.path.dirname(dest_dir)
                    # Don't go above source directory
                    if len(os.path.abspath(dest_dir)) < len(os.path.abspath(source)):
                        dest_dir = source

                # Only add if file would actually move
                if os.path.abspath(src) != os.path.join(dest_dir, fname):
                    plan.append((src, dest_dir, fname))

    if not plan:
        msg = "No files found in subfolders." if levels is None else f"No files found to move for the chosen level(s)."
        Messages.info(msg, title)
        LOGGER.end_operation()
        return

    # Execute plan with progress
    progress_bar["maximum"] = len(plan)
    succeeded = 0
    failed = 0

    for i, (src, dst_folder, fname) in enumerate(plan, 1):
        if move_file(src, dst_folder, fname):
            succeeded += 1
        else:
            failed += 1
        update_progress(i, len(plan))

    # Clean up empty folders
    removed_dirs = 0
    for source in source_dirs:
        for dpath, _, _ in os.walk(source, topdown=False):
            if os.path.abspath(dpath) == os.path.abspath(source):
                continue
            if not os.listdir(dpath):
                try:
                    os.rmdir(dpath)
                    removed_dirs += 1
                except (OSError, PermissionError):
                    pass

    LOGGER.end_operation()

    # Show results using OperationResult
    result = OperationResult(success_title)
    result.add("Files moved", succeeded)
    result.add("Files failed", failed, condition=failed > 0)
    result.add("Empty folders removed", removed_dirs)
    result.show()


def extract_all_to_parent():
    """Extract all files from subfolders to parent directory (wrapper for extract_files)"""
    extract_files(levels=None)

def extract_up_levels():
    """Extract files up N levels from their current location (wrapper for extract_files)"""
    # Get number of levels from user
    try:
        levels_str = simpledialog.askstring("Extract Up", "How many levels up? (1-10):", initialvalue="1")
        if not levels_str:
            return
        levels = int(levels_str)
        if levels < 1 or levels > 10:
            raise ValueError("Levels must be between 1 and 10")
    except ValueError as e:
        Messages.error(str(e), "Invalid Input")
        return

    # Call consolidated extract function
    extract_files(levels=levels)

# ==============================
# FOLDER CREATION TOOLS (NEW IN V6.3)
# ==============================
def create_alphanumeric_folders():
    """
    Auto-create A-Z, 0-9, and special character folders.

    User Feature Request #1: One-click folder structure creation
    """
    target_dir = (target_entry.get() or "").strip()

    if not target_dir:
        messagebox.showerror("Error", "Please select a target directory first.")
        return

    if not os.path.exists(target_dir):
        messagebox.showerror("Error", f"Target directory does not exist:\n{target_dir}")
        return

    # Get user preferences from checkboxes
    include_az = var_create_az.get()
    include_09 = var_create_09.get()
    include_special = var_create_special.get()
    use_uppercase = var_folder_case.get() == "upper"

    if not (include_az or include_09 or include_special):
        messagebox.showwarning("No Selection", "Please select at least one category to create.")
        return

    folders = []

    # Add A-Z folders
    if include_az:
        if use_uppercase:
            folders.extend([chr(i) for i in range(ord('A'), ord('Z')+1)])
        else:
            folders.extend([chr(i) for i in range(ord('a'), ord('z')+1)])

    # Add 0-9 folders
    if include_09:
        folders.extend([str(i) for i in range(10)])

    # Add special character folder
    if include_special:
        folders.append("!@#$")

    created = 0
    existing = 0
    failed = []

    # Create folders
    for folder in folders:
        path = os.path.join(target_dir, folder)
        try:
            if os.path.exists(path):
                existing += 1
            else:
                os.makedirs(path)
                created += 1
        except Exception as e:
            failed.append((folder, str(e)))

    # Show results
    msg = "✓ Folder Creation Complete!\n\n"
    msg += f"Created: {created} folders\n"
    if existing > 0:
        msg += f"Already existed: {existing} folders\n"
    if failed:
        msg += f"\n❌ Failed: {len(failed)} folders\n"
        for folder, error in failed[:5]:  # Show first 5 failures
            msg += f"  • {folder}: {error}\n"
        if len(failed) > 5:
            msg += f"  ... and {len(failed)-5} more\n"

    messagebox.showinfo("Folder Creation Complete", msg)


# ==============================
# CUSTOM FOLDER HIERARCHY (v7.0)
# ==============================
def parse_folder_hierarchy(hierarchy_string: str) -> List[str]:
    """
    Parse folder hierarchy string into list of folder names.

    Args:
        hierarchy_string: Hierarchy string with dash delimiter (e.g., "TMC-Aileron-LH")

    Returns:
        List of folder names in order

    Example:
        >>> parse_folder_hierarchy("TMC-Aileron-LH")
        ["TMC", "Aileron", "LH"]
    """
    if not hierarchy_string:
        return []

    # Split by dash delimiter and strip whitespace
    folders = [folder.strip() for folder in hierarchy_string.split('-')]

    # Filter out empty strings
    folders = [f for f in folders if f]

    return folders


def validate_folder_hierarchy(hierarchy: str) -> Tuple[bool, str]:
    """
    Validate folder hierarchy input for safety and compatibility.

    Args:
        hierarchy: Hierarchy string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for empty input
    if not hierarchy or not hierarchy.strip():
        return False, "Hierarchy cannot be empty"

    # Parse hierarchy
    parts = parse_folder_hierarchy(hierarchy)

    if not parts:
        return False, "No valid folder names found"

    # Check for excessive nesting (Windows has 260 char path limit)
    if len(parts) > 15:
        return False, f"Too many nesting levels ({len(parts)}). Maximum: 15"

    # Check individual folder name lengths
    for part in parts:
        if len(part) > 255:  # Max filename length on most systems
            return False, f"Folder name too long: '{part[:50]}...'"

        if len(part) < 1:
            return False, "Empty folder name in hierarchy"

        # Check for invalid characters (Windows + Unix)
        invalid_chars = '<>:"|?*\x00/\\'
        invalid_found = [c for c in invalid_chars if c in part]
        if invalid_found:
            return False, f"Invalid characters in '{part}': {', '.join(repr(c) for c in invalid_found)}"

    # Check estimated total path length
    # Account for separators and some base path
    estimated_length = len(os.path.sep.join(parts)) + 50  # +50 for base path
    if estimated_length > 240:  # Conservative limit below Windows 260
        return False, f"Total path too long (estimated {estimated_length} chars). Maximum: 240"

    return True, "Valid hierarchy"


def generate_numbered_folder_names(count: int) -> List[str]:
    """
    Generate numbered folder names with zero-padding.

    Args:
        count: Number of folders to generate

    Returns:
        List of numbered folder names (e.g., ["001", "002", "003"])

    Example:
        >>> generate_numbered_folder_names(5)
        ["001", "002", "003", "004", "005"]
    """
    if count <= 0:
        return []

    # Determine padding width based on count
    width = len(str(count))
    if width < 3:
        width = 3  # Minimum 3 digits

    return [str(i).zfill(width) for i in range(1, count + 1)]


def create_custom_hierarchy(base_path: str, hierarchy: str, num_folders: int = 0) -> Tuple[bool, str]:
    """
    Create custom folder hierarchy with optional numbered subfolders.

    Args:
        base_path: Base directory where hierarchy will be created
        hierarchy: Hierarchy string (e.g., "TMC-Aileron-LH")
        num_folders: Number of numbered folders to create in final level

    Returns:
        Tuple of (success, message)

    Example:
        Create "TMC/Aileron/LH/" with folders 001-050:
        >>> create_custom_hierarchy("/path", "TMC-Aileron-LH", 50)
    """
    try:
        # Parse hierarchy
        folders = parse_folder_hierarchy(hierarchy)

        if not folders:
            return False, "No folders specified in hierarchy"

        # Build nested path
        current_path = base_path
        for folder in folders:
            # Sanitize folder name
            safe_folder = sanitize_folder_name(folder)
            current_path = os.path.join(current_path, safe_folder)

            # Create folder if it doesn't exist
            if not os.path.exists(current_path):
                os.makedirs(current_path)

        # Create numbered folders if requested
        if num_folders > 0:
            numbered_folders = generate_numbered_folder_names(num_folders)

            for numbered in numbered_folders:
                numbered_path = os.path.join(current_path, numbered)
                if not os.path.exists(numbered_path):
                    os.makedirs(numbered_path)

        # Build success message
        hierarchy_display = " → ".join(folders)
        if num_folders > 0:
            hierarchy_display += f" (with {num_folders} numbered folders)"

        return True, f"Successfully created hierarchy:\n{hierarchy_display}"

    except Exception as e:
        return False, f"Error creating hierarchy: {str(e)}"


def create_custom_hierarchy_gui():
    """
    GUI wrapper for custom folder hierarchy creation.

    Prompts user for:
    1. Hierarchy string (e.g., "TMC-Aileron-LH")
    2. Number of folders in final level (optional)
    """
    target_dir = (target_entry.get() or "").strip()

    if not target_dir:
        messagebox.showerror("Error", "Please select a target directory first.")
        return

    if not os.path.exists(target_dir):
        messagebox.showerror("Error", f"Target directory does not exist:\n{target_dir}")
        return

    # Prompt for hierarchy
    hierarchy = simpledialog.askstring(
        "Custom Folder Hierarchy",
        "Enter folder hierarchy separated by dashes (-):\n\n"
        "Example: TMC-Aileron-LH\n"
        "Creates: TMC/Aileron/LH/\n\n"
        "Hierarchy:",
        parent=root
    )

    if not hierarchy:
        return  # User cancelled

    # Validate hierarchy input
    is_valid, error_msg = validate_folder_hierarchy(hierarchy)
    if not is_valid:
        messagebox.showerror("Invalid Hierarchy", f"❌ {error_msg}", parent=root)
        return

    # Prompt for number of folders in final level
    num_folders_str = simpledialog.askstring(
        "Numbered Folders",
        f"How many numbered folders to create in '{hierarchy.split('-')[-1]}'?\n\n"
        "Enter a number (e.g., 50 creates folders 001-050)\n"
        "Or press Cancel to skip numbered folders:\n\n"
        "Number of folders:",
        parent=root
    )

    # Parse number of folders
    num_folders = 0
    if num_folders_str:
        try:
            num_folders = int(num_folders_str)
            if num_folders < 0:
                messagebox.showerror("Error", "Number of folders must be positive")
                return
            if num_folders > 1000:
                if not messagebox.askyesno(
                    "Large Number",
                    f"You're creating {num_folders} folders. Continue?",
                    parent=root
                ):
                    return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return

    # Create hierarchy
    success, message = create_custom_hierarchy(target_dir, hierarchy, num_folders)

    if success:
        messagebox.showinfo("Success", f"✓ {message}", parent=root)
    else:
        messagebox.showerror("Error", f"❌ {message}", parent=root)


# ═══════════════════════════════════════════════════════════════════════════════
# ── MISSING FILE SCANNER (v7.1) ───────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def detect_file_patterns(directory: str) -> Dict[str, Dict]:
    """
    Detect numeric patterns in filenames and group files by pattern.

    Returns:
        Dict mapping pattern_key to {
            'files': list of (filename, number) tuples,
            'prefix': str,
            'suffix': str,
            'padding': int,
            'extension': str,
            'is_pure_numeric': bool
        }
    """
    import re
    from collections import defaultdict

    if not os.path.isdir(directory):
        return {}

    patterns = defaultdict(lambda: {
        'files': [],
        'prefix': '',
        'suffix': '',
        'padding': 0,
        'extension': '',
        'is_pure_numeric': False
    })

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    for filename in files:
        name, ext = os.path.splitext(filename)

        # Try to match numeric patterns
        # Pattern 1: Pure numeric (001, 1, 0042, etc.)
        match = re.match(r'^(\d+)$', name)
        if match:
            number = int(match.group(1))
            padding = len(match.group(1))
            pattern_key = f"PURE_NUMERIC_{ext}"
            patterns[pattern_key]['files'].append((filename, number))
            patterns[pattern_key]['prefix'] = ''
            patterns[pattern_key]['suffix'] = ''
            patterns[pattern_key]['padding'] = max(patterns[pattern_key]['padding'], padding)
            patterns[pattern_key]['extension'] = ext
            patterns[pattern_key]['is_pure_numeric'] = True
            continue

        # Pattern 2: Prefix + number (IMG_001, photo_42, etc.)
        match = re.match(r'^(.+?)(\d+)$', name)
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            padding = len(match.group(2))
            pattern_key = f"{prefix}_{ext}"
            patterns[pattern_key]['files'].append((filename, number))
            patterns[pattern_key]['prefix'] = prefix
            patterns[pattern_key]['suffix'] = ''
            patterns[pattern_key]['padding'] = max(patterns[pattern_key]['padding'], padding)
            patterns[pattern_key]['extension'] = ext
            patterns[pattern_key]['is_pure_numeric'] = False
            continue

        # Pattern 3: Prefix + number + suffix (IMG_001_final, etc.)
        match = re.match(r'^(.+?)(\d+)(.+)$', name)
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            suffix = match.group(3)
            padding = len(match.group(2))
            pattern_key = f"{prefix}_NUM_{suffix}_{ext}"
            patterns[pattern_key]['files'].append((filename, number))
            patterns[pattern_key]['prefix'] = prefix
            patterns[pattern_key]['suffix'] = suffix
            patterns[pattern_key]['padding'] = max(patterns[pattern_key]['padding'], padding)
            patterns[pattern_key]['extension'] = ext
            patterns[pattern_key]['is_pure_numeric'] = False

    # Filter out patterns with less than 2 files
    return {k: v for k, v in patterns.items() if len(v['files']) >= 2}


def find_missing_files(pattern_data: Dict) -> List[int]:
    """
    Find missing file numbers in a sequence.

    For pure numeric files: assumes sequence starts at 1
    For prefixed files: fills gaps between first and last existing file
    """
    if not pattern_data['files']:
        return []

    numbers = sorted([num for _, num in pattern_data['files']])
    first_num = numbers[0]
    last_num = numbers[-1]

    # For pure numeric files, start from 1
    if pattern_data['is_pure_numeric']:
        start = 1
    else:
        start = first_num

    # Find all missing numbers in range
    existing_set = set(numbers)
    missing = [n for n in range(start, last_num + 1) if n not in existing_set]

    return missing


def create_placeholder_files(directory: str, pattern_data: Dict, missing_numbers: List[int]) -> Tuple[bool, str, List[str]]:
    """
    Create empty placeholder files for missing numbers.

    Returns:
        (success, message, list of created filenames)
    """
    created_files = []

    try:
        for num in missing_numbers:
            # Build filename
            num_str = str(num).zfill(pattern_data['padding'])
            filename = f"{pattern_data['prefix']}{num_str}{pattern_data['suffix']}{pattern_data['extension']}"
            filepath = os.path.join(directory, filename)

            # Create empty file
            with open(filepath, 'w') as f:
                pass  # Empty file

            created_files.append(filename)

        return True, f"Created {len(created_files)} placeholder files", created_files

    except Exception as e:
        return False, f"Error creating placeholders: {str(e)}", created_files


def log_missing_files_operation(directory: str, pattern_key: str, pattern_data: Dict,
                                 missing_numbers: List[int], created_files: List[str]):
    """
    Log missing file operation to missing_files.log
    """
    log_dir = os.path.join(directory, ".file_organizer_data")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "missing_files.log")

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Directory: {directory}\n")
            f.write(f"Pattern: {pattern_key}\n")

            if pattern_data['is_pure_numeric']:
                f.write(f"Type: Pure numeric (starts from 1)\n")
            else:
                f.write(f"Type: Prefixed pattern\n")
                f.write(f"Prefix: '{pattern_data['prefix']}'\n")
                if pattern_data['suffix']:
                    f.write(f"Suffix: '{pattern_data['suffix']}'\n")

            f.write(f"Padding: {pattern_data['padding']} digits\n")
            f.write(f"Extension: {pattern_data['extension']}\n")

            numbers = sorted([num for _, num in pattern_data['files']])
            f.write(f"Range: {numbers[0]:0{pattern_data['padding']}d} - {numbers[-1]:0{pattern_data['padding']}d}\n")
            f.write(f"Existing files: {len(pattern_data['files'])}\n")
            f.write(f"Missing files: {len(missing_numbers)}\n")
            f.write(f"\nCreated placeholders ({len(created_files)} files):\n")

            # Group consecutive numbers for cleaner log
            if created_files:
                f.write(f"  {', '.join(created_files[:10])}")
                if len(created_files) > 10:
                    f.write(f" ... (and {len(created_files) - 10} more)")
                f.write("\n")

            f.write(f"{'='*80}\n")

    except Exception as e:
        logging.error(f"Failed to write to missing_files.log: {e}")


def scan_missing_files_gui():
    """
    GUI wrapper for missing file scanner with preview and confirmation.
    """
    target_dir = (target_entry.get() or "").strip()

    if not target_dir:
        messagebox.showerror("Error", "Please select a target directory first.")
        return

    if not os.path.isdir(target_dir):
        messagebox.showerror("Error", "Target directory does not exist.")
        return

    # Detect patterns
    patterns = detect_file_patterns(target_dir)

    if not patterns:
        messagebox.showinfo(
            "No Patterns Found",
            "No numeric file patterns detected in this directory.\n\n"
            "The scanner looks for:\n"
            "• Pure numeric files (001.jpg, 042.pdf)\n"
            "• Prefixed files (IMG_001.jpg, photo_42.png)\n\n"
            "Need at least 2 files to establish a pattern.",
            parent=root
        )
        return

    # Show pattern selection dialog
    dialog = tk.Toplevel(root)
    dialog.title("Missing File Scanner - Select Pattern")
    dialog.geometry("700x500")
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(
        dialog,
        text="📊 Detected File Patterns",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Label(
        dialog,
        text=f"Directory: {target_dir}",
        font=("Arial", 9),
        fg="gray"
    ).pack()

    # Create listbox with pattern details
    frame = ttk.Frame(dialog)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    listbox = tk.Listbox(frame, font=("Courier", 10), height=15)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)

    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    pattern_list = []
    for pattern_key, pattern_data in patterns.items():
        missing = find_missing_files(pattern_data)
        numbers = sorted([num for _, num in pattern_data['files']])

        if pattern_data['is_pure_numeric']:
            desc = f"Pure Numeric{pattern_data['extension']}"
        else:
            desc = f"{pattern_data['prefix']}###"
            if pattern_data['suffix']:
                desc += pattern_data['suffix']
            desc += pattern_data['extension']

        line = f"{desc:30} | Files: {len(pattern_data['files']):4} | Missing: {len(missing):4} | Range: {numbers[0]}-{numbers[-1]}"
        listbox.insert(tk.END, line)
        pattern_list.append((pattern_key, pattern_data, missing))

    selected_pattern = [None]

    def on_process():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a pattern to process.", parent=dialog)
            return

        idx = selection[0]
        pattern_key, pattern_data, missing = pattern_list[idx]

        if not missing:
            messagebox.showinfo("No Missing Files", "This pattern has no missing files!", parent=dialog)
            return

        # Show confirmation with details
        numbers = sorted([num for _, num in pattern_data['files']])

        if pattern_data['is_pure_numeric']:
            pattern_desc = f"Pure numeric, {pattern_data['padding']}-digit padding, {pattern_data['extension']}"
        else:
            pattern_desc = f"Prefix: '{pattern_data['prefix']}', {pattern_data['padding']}-digit padding, {pattern_data['extension']}"

        # Build gap summary
        gap_summary = []
        if pattern_data['is_pure_numeric'] and numbers[0] > 1:
            gap_summary.append(f"  • 1 - {numbers[0]-1} ({numbers[0]-1} files)")

        # Find consecutive gaps
        i = 0
        while i < len(missing):
            start = missing[i]
            end = start
            while i + 1 < len(missing) and missing[i + 1] == end + 1:
                i += 1
                end = missing[i]

            if start == end:
                gap_summary.append(f"  • {start} (1 file)")
            else:
                gap_summary.append(f"  • {start} - {end} ({end - start + 1} files)")
            i += 1

        gaps_text = "\n".join(gap_summary[:15])
        if len(gap_summary) > 15:
            gaps_text += f"\n  ... (and {len(gap_summary) - 15} more gaps)"

        message = f"""📊 Missing File Detection Summary

Pattern: {pattern_desc}
First file: {numbers[0]:0{pattern_data['padding']}d}{pattern_data['extension']}
Last file: {numbers[-1]:0{pattern_data['padding']}d}{pattern_data['extension']}

Existing files: {len(pattern_data['files'])}
Missing files: {len(missing)}

Gaps to fill:
{gaps_text}

Create {len(missing)} placeholder files?"""

        if messagebox.askyesno("Confirm Creation", message, parent=dialog):
            success, msg, created = create_placeholder_files(target_dir, pattern_data, missing)

            if success:
                # Log operation
                log_missing_files_operation(target_dir, pattern_key, pattern_data, missing, created)

                messagebox.showinfo(
                    "Success",
                    f"✓ {msg}\n\nLogged to .file_organizer_data/missing_files.log",
                    parent=dialog
                )
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"❌ {msg}", parent=dialog)

    def on_cancel():
        dialog.destroy()

    # Buttons
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Process Selected Pattern", command=on_process).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)

    tk.Label(
        dialog,
        text="💡 Tip: Select a pattern and click 'Process' to create missing placeholders",
        font=("Arial", 9),
        fg="gray"
    ).pack(pady=5)


def search_and_collect():
    """
    Search for files matching a custom pattern and collect them into a folder.
    User Feature Request #2: Custom pattern search with user-specified pattern
    """
    source_dirs = get_source_dirs()
    if not source_dirs:
        messagebox.showerror("Error", "Please select at least one source directory.")
        return

    pattern = var_search_pattern.get().strip()
    if not pattern:
        messagebox.showwarning("No Pattern", "Please enter a search pattern (e.g., IMG*, *-001-*, *.jpg)")
        return

    folder_name = var_search_folder.get().strip()
    if not folder_name:
        messagebox.showwarning("No Folder Name", "Please specify a folder name for collected files.")
        return

    # Sanitize folder name
    folder_name = sanitize_folder_name(folder_name)

    # Get target directory
    target_dir = (target_entry.get() or "").strip()
    if not target_dir:
        messagebox.showerror("Error", "Please select a target directory.")
        return

    if not os.path.exists(target_dir):
        messagebox.showerror("Error", f"Target directory does not exist:\n{target_dir}")
        return

    # Search for matching files
    status_label.config(text="🔍 Searching for matching files...")
    root.update()

    matching_files = []
    total_scanned = 0

    try:
        import fnmatch

        for source_dir in source_dirs:
            for dirpath, dirnames, filenames in os.walk(source_dir):
                # Skip certain folders
                dirnames[:] = [d for d in dirnames if not should_skip_folder(d)]

                for filename in filenames:
                    total_scanned += 1

                    # Update progress every 1000 files
                    if total_scanned % 1000 == 0:
                        status_label.config(text=f"🔍 Scanned {total_scanned} files, found {len(matching_files)} matches...")
                        root.update()

                    # Check if filename matches pattern
                    if fnmatch.fnmatch(filename, pattern):
                        src_path = os.path.join(dirpath, filename)
                        matching_files.append((src_path, filename))

        status_label.config(text=f"✓ Search complete: {len(matching_files)} matches found")

    except Exception as e:
        status_label.config(text="❌ Search failed")
        messagebox.showerror("Search Error", f"Error during search:\n{str(e)}")
        return

    # Show preview
    if not matching_files:
        messagebox.showinfo("No Matches", f"No files found matching pattern: {pattern}\n\nTotal scanned: {total_scanned}")
        return

    # Preview dialog
    preview_msg = f"✓ Found {len(matching_files)} files matching '{pattern}'\n\n"
    preview_msg += f"They will be moved to: {target_dir}\\{folder_name}\\\n\n"
    preview_msg += "Sample files (showing first 10):\n"
    for src_path, filename in matching_files[:10]:
        preview_msg += f"  • {filename}\n"
    if len(matching_files) > 10:
        preview_msg += f"  ... and {len(matching_files)-10} more\n"
    preview_msg += f"\n\nTotal scanned: {total_scanned} files"
    preview_msg += f"\nProceed with moving {len(matching_files)} files?"

    if not messagebox.askyesno("Confirm Pattern Collection", preview_msg):
        status_label.config(text="Pattern collection cancelled")
        return

    # Create target folder
    dest_folder = os.path.join(target_dir, folder_name)
    try:
        os.makedirs(dest_folder, exist_ok=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not create folder:\n{str(e)}")
        return

    # Move files
    status_label.config(text=f"📦 Moving {len(matching_files)} files...")
    root.update()

    moved = 0
    failed = []

    for i, (src_path, filename) in enumerate(matching_files, 1):
        # Update progress every 100 files
        if i % 100 == 0:
            status_label.config(text=f"📦 Moving files... {i}/{len(matching_files)}")
            root.update()

        dest_path = os.path.join(dest_folder, filename)

        # Handle filename collisions
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            counter = 2
            while os.path.exists(os.path.join(dest_folder, f"{base}({counter}){ext}")):
                counter += 1
            dest_path = os.path.join(dest_folder, f"{base}({counter}){ext}")

        try:
            shutil.move(src_path, dest_path)
            moved += 1
        except Exception as e:
            failed.append((filename, str(e)))

    # Show results
    result_msg = f"✓ Pattern Collection Complete!\n\n"
    result_msg += f"Pattern: {pattern}\n"
    result_msg += f"Folder: {folder_name}\n"
    result_msg += f"Moved: {moved} files\n"
    if failed:
        result_msg += f"\n❌ Failed: {len(failed)} files\n"
        for filename, error in failed[:5]:
            result_msg += f"  • {filename}: {error}\n"
        if len(failed) > 5:
            result_msg += f"  ... and {len(failed)-5} more\n"

    status_label.config(text=f"✓ Moved {moved} files to {folder_name}/")
    messagebox.showinfo("Pattern Collection Complete", result_msg)

# ==============================
# LOGIC FUNCTIONS (from v4)
# ==============================
def by_extension(filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1][1:]
    folder = ext.upper() if ext else "_NOEXT"
    return sanitize_folder_name(folder)

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


# ==============================
# DATE-BASED ORGANIZATION (v7.0)
# ==============================
def format_date_year(dt: datetime) -> str:
    """Format datetime as YYYY"""
    return dt.strftime("%Y")


def format_date_month(dt: datetime) -> str:
    """Format datetime as YYYY-MM"""
    return dt.strftime("%Y-%m")


def format_date_full(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD"""
    return dt.strftime("%Y-%m-%d")


def by_date_year(filename: str) -> Optional[str]:
    """Organize by year (YYYY)"""
    filepath = os.path.join(source_entry.get() if hasattr(source_entry, 'get') else '', filename)
    dt = get_file_datetime(filepath)
    if dt:
        return format_date_year(dt)
    return None


def by_date_month(filename: str) -> Optional[str]:
    """Organize by year-month (YYYY-MM)"""
    filepath = os.path.join(source_entry.get() if hasattr(source_entry, 'get') else '', filename)
    dt = get_file_datetime(filepath)
    if dt:
        return format_date_month(dt)
    return None


def by_date_full(filename: str) -> Optional[str]:
    """Organize by full date (YYYY-MM-DD)"""
    filepath = os.path.join(source_entry.get() if hasattr(source_entry, 'get') else '', filename)
    dt = get_file_datetime(filepath)
    if dt:
        return format_date_full(dt)
    return None

def by_sequential(filename: str) -> Optional[str]:
    """Sequential pattern detection for organization mode"""
    return detect_sequential_pattern(filename)

def by_intelligent(filename: str) -> Optional[str]:
    """
    Intelligent pattern detection with learning - consolidates Smart Pattern, Smart Pattern+, and Sequential Pattern.

    Uses IntelligentPatternDetector which:
    - Checks learned patterns first (highest confidence)
    - Falls back to camera tags, sequential patterns, smart patterns
    - Returns folder name or None
    """
    folder, confidence, method = INTELLIGENT_DETECTOR.detect(filename)
    return folder

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
# LEARNED PATTERNS VIEWER
# ==============================
def show_learned_patterns():
    """Display learned patterns from the intelligent pattern detector"""
    patterns_win = tk.Toplevel(root)
    patterns_win.title("🧠 Learned Patterns - Intelligent Pattern Scanner")
    patterns_win.geometry("900x600")

    main_frame = ttk.Frame(patterns_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="🧠 Learned Patterns", font=FONT_TITLE).pack(anchor="w", pady=(0, 10))

    info_text = ("The intelligent pattern scanner learns from your file organization patterns.\n"
                 "Each time you organize files, it remembers the pattern and improves its predictions.\n\n"
                 "Confidence increases with each successful use of the same pattern.")
    ttk.Label(main_frame, text=info_text, wraplength=850, justify="left").pack(anchor="w", pady=(0, 10))

    # Treeview for patterns
    columns = ("Signature", "Folder", "Count", "Confidence", "Examples")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

    tree.heading("Signature", text="Pattern Signature")
    tree.heading("Folder", text="Target Folder")
    tree.heading("Count", text="Uses")
    tree.heading("Confidence", text="Confidence")
    tree.heading("Examples", text="Example Files")

    tree.column("Signature", width=150)
    tree.column("Folder", width=150)
    tree.column("Count", width=80)
    tree.column("Confidence", width=100)
    tree.column("Examples", width=400)

    tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Load and display learned patterns
    patterns = INTELLIGENT_DETECTOR.learner.patterns

    if not patterns:
        tree.insert("", "end", values=("No patterns learned yet", "", "", "", "Start using Intelligent Pattern to learn!"))
    else:
        for signature, data in sorted(patterns.items(), key=lambda x: x[1].get("count", 0), reverse=True):
            folder = data.get("folder", "")
            count = data.get("count", 0)
            confidence = min(0.99, 0.80 + (count * 0.03))
            examples = data.get("examples", [])
            examples_str = ", ".join(examples[:3])  # Show first 3 examples

            tree.insert("", "end", values=(
                signature,
                folder,
                count,
                f"{confidence:.0%}",
                examples_str
            ))

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))

    def clear_patterns():
        """Clear all learned patterns"""
        if Messages.confirm("Are you sure you want to clear all learned patterns?\n\nThis cannot be undone.", "Clear Patterns"):
            INTELLIGENT_DETECTOR.learner.patterns = {}
            INTELLIGENT_DETECTOR.learner._save_patterns()
            patterns_win.destroy()
            Messages.info("All learned patterns have been cleared.", "Patterns Cleared")

    ttk.Button(button_frame, text="🗑️ Clear All Patterns", command=clear_patterns).pack(side="left", padx=(0, 10))
    ttk.Label(button_frame, text=f"Total Patterns: {len(patterns)}", font=FONT_BASE).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Close", command=patterns_win.destroy).pack(side="right")


def show_pattern_statistics():
    """Display statistics about the intelligent pattern scanner"""
    stats_win = tk.Toplevel(root)
    stats_win.title("🔬 Pattern Scanner Statistics")
    stats_win.geometry("700x500")

    main_frame = ttk.Frame(stats_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="🔬 Pattern Scanner Statistics", font=FONT_TITLE).pack(anchor="w", pady=(0, 10))

    # Get statistics
    patterns = INTELLIGENT_DETECTOR.learner.patterns
    total_patterns = len(patterns)
    total_uses = sum(p.get("count", 0) for p in patterns.values())

    # Count patterns by confidence level
    high_confidence = sum(1 for p in patterns.values() if p.get("count", 0) >= 5)
    medium_confidence = sum(1 for p in patterns.values() if 2 <= p.get("count", 0) < 5)
    low_confidence = sum(1 for p in patterns.values() if p.get("count", 0) < 2)

    # Most used pattern
    most_used = None
    if patterns:
        most_used = max(patterns.items(), key=lambda x: x[1].get("count", 0))

    # Create statistics display
    stats_text = tk.Text(main_frame, wrap=tk.WORD, height=20, width=80, font=FONT_BASE)
    stats_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # Build statistics content
    content = f"""
📊 OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Learned Patterns: {total_patterns}
Total Pattern Uses: {total_uses}
Average Uses per Pattern: {total_uses / total_patterns if total_patterns > 0 else 0:.1f}


🎯 CONFIDENCE DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

High Confidence (5+ uses, 95-99%): {high_confidence} patterns
Medium Confidence (2-4 uses, 86-92%): {medium_confidence} patterns
Low Confidence (1 use, 80-83%): {low_confidence} patterns


🏆 TOP PATTERN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    if most_used:
        signature, data = most_used
        count = data.get("count", 0)
        folder = data.get("folder", "")
        confidence = min(0.99, 0.80 + (count * 0.03))
        examples = data.get("examples", [])

        content += f"""
Pattern Signature: {signature}
Target Folder: {folder}
Times Used: {count}
Confidence: {confidence:.0%}
Examples: {", ".join(examples[:3])}


"""

    content += f"""
💡 DETECTION METHODS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Intelligent Scanner uses a 4-tier detection system:

1. 🧠 Learned Patterns (80-99% confidence)
   • Patterns you've used before
   • Confidence increases with each use
   • Currently: {total_patterns} learned pattern{"s" if total_patterns != 1 else ""}

2. 📷 Camera Tags (95% confidence)
   • IMG, DSC, DSCN, DCS tags
   • Professional camera file detection

3. 🔢 Sequential Patterns (90% confidence)
   • file001, vacation-123, 031204-0022
   • Number-based sequences

4. 🎯 Smart Delimiter Patterns (80% confidence)
   • Underscore and hyphen detection
   • Context-aware capitalization


📈 LEARNING PROCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Each time you organize files:
1. Pattern signature extracted (e.g., "TEXT-NNN")
2. Your folder choice is remembered
3. Confidence increases with repeated use
4. Pattern saved to learned_patterns.json

The more you use it, the smarter it gets! 🚀


💾 DATA STORAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Learned patterns are stored in:
{DATA_DIR.get_path("learned_patterns.json")}

All data is stored locally on your computer.
No cloud sync, no tracking, complete privacy.
"""

    stats_text.insert("1.0", content)
    stats_text.config(state="disabled")

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(button_frame, text="📚 View Patterns", command=lambda: [stats_win.destroy(), show_learned_patterns()]).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="Close", command=stats_win.destroy).pack(side="right")


# ==============================
# DATABASE SCANNER UI
# ==============================
def show_database_scanner():
    """Show database scanner window for learning from existing organization"""
    scanner_win = tk.Toplevel(root)
    scanner_win.title("📊 Database Scanner - Learn from Your Organization")
    scanner_win.geometry("1000x700")

    main_frame = ttk.Frame(scanner_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="📊 Database Scanner", font=FONT_TITLE).pack(anchor="w", pady=(0, 10))

    info_text = ("Scan your directories to learn organization patterns.\n"
                 "The AI will analyze your existing folder structure and learn from it.\n"
                 "Files in 'Sorting', 'Sort', or 'Unsorted' folders are treated as unorganized (not touched).")
    ttk.Label(main_frame, text=info_text, wraplength=950, justify="left").pack(anchor="w", pady=(0, 10))

    # Directory selection
    dir_frame = ttk.LabelFrame(main_frame, text="Scan Directory", padding=10)
    dir_frame.pack(fill="x", pady=(0, 10))

    scan_dir_var = tk.StringVar()
    ttk.Entry(dir_frame, textvariable=scan_dir_var, width=80).pack(side="left", padx=(0, 10))

    def browse_scan_dir():
        path = filedialog.askdirectory()
        if path:
            scan_dir_var.set(path)

    ttk.Button(dir_frame, text="Browse", command=browse_scan_dir).pack(side="left")

    # Progress frame
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill="x", pady=(0, 10))

    scan_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
    scan_progress.pack(fill="x", pady=5)

    status_label = ttk.Label(progress_frame, text="Ready to scan")
    status_label.pack(anchor="w")

    # Results display
    results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    results_text = tk.Text(results_frame, wrap=tk.WORD, height=25, font=FONT_BASE)
    results_text.pack(fill=tk.BOTH, expand=True, side="left")

    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_text.yview)
    results_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def update_progress(count, filename):
        """Update progress display"""
        status_label.config(text=f"Scanning... {count:,} files processed (current: {filename})")
        scanner_win.update_idletasks()

    def perform_scan():
        """Perform the directory scan"""
        scan_path = scan_dir_var.get().strip()

        if not scan_path:
            Messages.error("Please select a directory to scan", "No Directory")
            return

        if not os.path.isdir(scan_path):
            Messages.error(f"Directory does not exist:\n{scan_path}", "Invalid Directory")
            return

        # Clear previous results
        results_text.config(state="normal")
        results_text.delete("1.0", tk.END)
        results_text.config(state="disabled")

        # Start progress
        scan_progress.start()
        status_label.config(text="Starting scan...")
        scanner_win.update_idletasks()

        try:
            # Perform scan
            scan_results = DATABASE_SCANNER.scan_directory(scan_path, update_progress)

            # Save results
            DATABASE_SCANNER.save_scan_results()

            # Display results
            display_scan_results(scan_results)

            status_label.config(text=f"Scan complete! {scan_results['total_files']:,} files analyzed")

        except Exception as e:
            Messages.error(f"Scan failed:\n{str(e)}", "Scan Error")
            status_label.config(text="Scan failed")

        finally:
            scan_progress.stop()

    def display_scan_results(results):
        """Display scan results in text widget"""
        results_text.config(state="normal")
        results_text.delete("1.0", tk.END)

        # Build results display
        output = f"""
{'='*80}
📊 SCAN RESULTS
{'='*80}

📁 OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scanned Directory: {results['root_path']}
Scan Date: {results['scan_date']}

Total Files: {results['total_files']:,}
Total Folders: {results['total_folders']:,}

Organized Files: {results['organized_files']:,} ({results['organized_files']/results['total_files']*100:.1f}% if results['total_files'] > 0 else 0)
Unorganized Files: {results['unorganized_files']:,} ({results['unorganized_files']/results['total_files']*100:.1f}% if results['total_files'] > 0 else 0)


📂 UNORGANIZED AREAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if results['unorganized_areas']:
            output += f"Found {len(results['unorganized_areas'])} unorganized folder(s):\n\n"
            for area in results['unorganized_areas']:
                output += f"  📁 {area['folder']}\n"
                output += f"     Path: {area['path']}\n"
                output += f"     Files: {area['file_count']:,}\n\n"
        else:
            output += "No unorganized areas found (all files are in organized folders).\n\n"

        output += f"""

🎯 LEARNED PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unique Patterns Detected: {len(results['learned_mappings'])}

"""

        # Show top patterns
        if results['learned_mappings']:
            sorted_patterns = sorted(results['learned_mappings'].items(),
                                   key=lambda x: x[1]['count'], reverse=True)

            output += "Top Patterns (by frequency):\n\n"
            for i, (signature, data) in enumerate(sorted_patterns[:10], 1):
                output += f"{i}. Pattern: {signature}\n"
                output += f"   Folder: {data['folder']}\n"
                output += f"   Count: {data['count']} files\n"
                output += f"   Examples: {', '.join(data['examples'][:3])}\n\n"

        output += f"""

🗂️ FOLDER STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Organized Folders: {len(results['folder_structure'])}

"""

        # Show folder structure
        if results['folder_structure']:
            sorted_folders = sorted(results['folder_structure'].items(),
                                  key=lambda x: x[1]['file_count'], reverse=True)

            output += "Folders (sorted by file count):\n\n"
            for folder_name, folder_data in sorted_folders[:20]:
                output += f"📁 {folder_name}\n"
                output += f"   Files: {folder_data['file_count']:,}\n"
                output += f"   Patterns: {len(folder_data['patterns'])}\n\n"

        # Insights
        output += f"""

💡 INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        insights = DATABASE_SCANNER.get_organization_insights()
        for insight in insights:
            output += f"{insight}\n"

        output += f"""


🧠 READY TO LEARN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{len([d for d in results['learned_mappings'].values() if d['count'] >= 2])} patterns are ready to be applied to the AI Scanner.

Click "Apply to AI Scanner" to teach the AI your organization preferences!

{'='*80}
"""

        results_text.insert("1.0", output)
        results_text.config(state="disabled")

    def apply_to_ai():
        """Apply learned patterns to AI Scanner"""
        if DATABASE_SCANNER.scan_results.get("total_files", 0) == 0:
            Messages.error("No scan results available.\n\nPlease run a scan first.", "No Results")
            return

        try:
            patterns_applied = DATABASE_SCANNER.apply_learned_patterns_to_ai()

            if patterns_applied > 0:
                Messages.info(
                    f"Successfully applied {patterns_applied} pattern(s) to the AI Scanner!\n\n"
                    f"The AI will now use these patterns when organizing files.\n\n"
                    f"You can view learned patterns in: 🧠 AI Scanner → 📚 View Learned Patterns",
                    "Patterns Applied"
                )
            else:
                Messages.warning(
                    "No patterns were applied.\n\n"
                    "Patterns need at least 2 occurrences to be learned.\n"
                    "Try scanning a folder with more organized files.",
                    "No Patterns Applied"
                )

        except Exception as e:
            Messages.error(f"Failed to apply patterns:\n{str(e)}", "Error")

    def load_previous_scan():
        """Load and display previous scan results"""
        if DATABASE_SCANNER.load_scan_results():
            display_scan_results(DATABASE_SCANNER.scan_results)
            status_label.config(text="Loaded previous scan results")
        else:
            Messages.info("No previous scan results found.\n\nRun a scan to get started!", "No Previous Scan")

    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(button_frame, text="🔍 Start Scan", command=perform_scan, width=15).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="🧠 Apply to AI Scanner", command=apply_to_ai, width=20).pack(side="left", padx=(0, 10))
    ttk.Button(button_frame, text="📂 Load Previous Scan", command=load_previous_scan, width=20).pack(side="left", padx=(0, 10))
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
        """Undo last operation with progress bar"""
        if not messagebox.askyesno("Confirm Undo", "Undo the last operation? This will move files back to their original locations."):
            return

        # Create progress window
        progress_win = tk.Toplevel(undo_win)
        progress_win.title("Undoing Operation...")
        progress_win.geometry("400x150")
        progress_win.transient(undo_win)
        progress_win.grab_set()

        ttk.Label(progress_win, text="Undoing operation...", font=("Segoe UI", 10, "bold")).pack(pady=(20, 10))

        progress_bar = ttk.Progressbar(progress_win, orient="horizontal", mode="determinate", length=350)
        progress_bar.pack(pady=10)

        status_label = ttk.Label(progress_win, text="Preparing...")
        status_label.pack(pady=5)

        # Perform undo in thread with progress updates
        result_queue: queue.Queue = queue.Queue()

        def undo_worker():
            """Worker thread for undo operation"""
            try:
                success, message, moved_count, total_count = LOGGER.undo_last_operation_with_progress(
                    lambda current, total, filename: result_queue.put(('progress', current, total, filename))
                )
                result_queue.put(('complete', success, message, moved_count))
            except Exception as e:
                result_queue.put(('error', str(e)))

        def monitor_undo():
            """Monitor undo progress from main thread"""
            try:
                while not result_queue.empty():
                    msg = result_queue.get_nowait()

                    if msg[0] == 'progress':
                        _, current, total, filename = msg
                        progress_bar["maximum"] = total
                        progress_bar["value"] = current
                        status_label.config(text=f"Restoring {current}/{total}: {filename[:50]}...")

                    elif msg[0] == 'complete':
                        _, success, message, moved_count = msg
                        progress_win.destroy()
                        messagebox.showinfo("Undo Result", f"{message}\n\n{moved_count} files restored.")
                        undo_win.destroy()
                        return

                    elif msg[0] == 'error':
                        _, error_msg = msg
                        progress_win.destroy()
                        messagebox.showerror("Undo Error", f"Failed to undo operation:\n\n{error_msg}")
                        return

                # Continue monitoring
                progress_win.after(100, monitor_undo)

            except queue.Empty:
                progress_win.after(100, monitor_undo)

        # Start undo thread
        undo_thread = threading.Thread(target=undo_worker, daemon=True)
        undo_thread.start()

        # Start monitoring
        monitor_undo()

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
    help_win.title(f"Help — {VERSION} Guide")
    help_win.geometry("800x700")
    help_win.minsize(600, 500)
    frame = tk.Frame(help_win)
    frame.pack(fill=tk.BOTH, expand=True)
    text_area = tk.Text(frame, wrap="word", font=("Segoe UI", 10))
    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    help_text = f"""
FILE ORGANIZER — {VERSION}
═══════════════════════════════════════════════════

✨ NEW IN VERSION 6.3 (GUI ENHANCEMENTS):
• Auto-Create A-Z + 0-9 Folders - One-click folder structure creation
  - Create alphabetic folders (A-Z or a-z)
  - Create numeric folders (0-9)
  - Create special character folder (!@#$)
  - Choose uppercase or lowercase
  - Perfect for pre-organizing before file operations

• Custom Pattern Search & Collect - Search and gather files by pattern
  - Enter custom patterns: IMG*, *-001-*, *.jpg, etc.
  - Scans all source directories
  - Shows preview of matches before moving
  - Collects all matching files into one folder
  - Real-time progress updates

• Tabbed Interface - Organized UI with logical grouping
  - 📂 Organize tab: All organization modes
  - 🔧 Tools tab: Folder tools, pattern search, extract
  - ⚙️ Advanced tab: Pattern scanner, statistics, history
  - Cleaner, more intuitive navigation

• Recent Directories Dropdown - Quick access to previous paths
  - Source and target directories remember last 10 used
  - Dropdown shows history for quick selection
  - Persists across sessions
  - Auto-updated when browsing or running operations

🆕 VERSION 6.2 (IN-PLACE ORGANIZATION):
• In-Place Organization Mode - organize files within the same folder
• Skip folders with # prefix (e.g., #Sort, #Archive)
• Checkbox control to enable/disable in-place mode
• All v6.1 features preserved:
  - Case-insensitive Windows path security check
  - Windows reserved folder name sanitization (Critical #36 fix)
  - Progress UI for UNDO
  - Comprehensive type hints

🔥 SEQUENTIAL PATTERN DETECTION
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

🔐 HASH-BASED DUPLICATE DETECTION (per-run cache in v6.1)
• Uses MD5 hashing for 100% accuracy
• No false positives (same size ≠ duplicate)
• True duplicates: same name + size + hash → DUPES
• Name collision: same name + different content → DUPE SIZE
• Per-run cache (cleared each operation)

⚡ MEMORY EFFICIENT PROCESSING
• Generator-based file collection
• Handles millions of files without memory issues
• Batch processing in chunks of 10,000
• Progress updates every 1,000 files
• Optimized for large-scale operations

✅ PRE-FLIGHT VALIDATION
• Checks source/target validity
• Verifies write permissions
• Prevents target-in-source errors (unless in-place mode enabled)
• Warns about low disk space
• Validates before any file moves

🎯 IN-PLACE ORGANIZATION MODE (NEW IN v6.2)
• Enable checkbox: "✓ Organize within same folder (source = target)"
• Allows organizing files within the same directory
• Perfect for multi-level organization:
  - First pass: Move files into top-level folders (A/, B/, C/)
  - Second pass: Organize within each folder (Alpha/, Amb/ subfolders)
  - Third pass: Further organize subfolders (001/, 002/ sub-subfolders)
• Example workflow:
  1. Organize 5000 files → A/ folder (Alpha-001.jpg, Amb-001.jpg, etc.)
  2. Enable in-place mode, set source=target=A/
  3. Organize again → creates Alpha/, Amb/ subfolders within A/
  4. Navigate to Amb/, organize again → creates 001/, 002/ sub-subfolders
• Folders starting with # are skipped (e.g., #Sort, #Archive)

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
• IMG/DSC Only - Camera file detection

🧠 AI SCANNER TAB (NEW!):
• Intelligent Pattern Detection with Machine Learning
• Learns from your organization choices
• Auto-detects: Camera tags, Sequential files, Delimiter patterns
• Confidence scoring: 80-99%
• View learned patterns and statistics
• The more you use it, the smarter it gets!

📝 TIPS:
• Always preview before organizing
• Check operation history regularly
• Use undo if something goes wrong
• Configure skip_folders for system dirs
• Enable hash detection for accuracy

═══════════════════════════════════════════════════
Version 6.2 — In-Place Organization
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
    "📅 By Date": [
        ("By Year (YYYY)", lambda: run_organizer(by_date_year, operation_name="By Year")),
        ("By Month (YYYY-MM)", lambda: run_organizer(by_date_month, operation_name="By Month")),
        ("By Day (YYYY-MM-DD)", lambda: run_organizer(by_date_full, operation_name="By Date")),
        ("Preview", lambda: run_organizer(by_date_year, preview=True)),
    ],
    "🧠 Intelligent Scanner": [
        ("🧠 Organize with AI Learning", lambda: run_organizer(by_intelligent, operation_name="Intelligent Pattern")),
        ("👁️ Preview Patterns", lambda: run_organizer(by_intelligent, preview=True)),
        ("📚 View Learned Patterns", lambda: show_learned_patterns()),
        ("🔬 Pattern Statistics", lambda: show_pattern_statistics()),
    ],
    "📤 Extract": [
        ("Extract All to Parent", extract_all_to_parent),
        ("Extract Up N Levels", extract_up_levels),
    ],
    "📁 Folder Tools": [
        ("Create A-Z + 0-9 Folders", create_alphanumeric_folders),
        ("Create Custom Hierarchy", create_custom_hierarchy_gui),
        ("🔍 Scan for Missing Files", scan_missing_files_gui),
    ],
    "🔍 Pattern Search": [
        ("Search & Collect by Pattern", search_and_collect),
    ],
    "🔧 Tools": [
        ("🔍 Pattern Scanner", show_pattern_scanner),
        ("📊 Statistics", show_statistics),
        ("🔄 View History & Undo", show_undo_window),
    ],
    "📊 Database Scanner": [
        ("📊 Scan & Learn", show_database_scanner),
    ],
}

# ── TABBED ACTIONS (v6.3) ──────────────────────────────────────────────────────
# Group sections into tabs for better organization
tab_groups = {
    "📂 Organize": ["By Extension", "Alphabetize", "IMG/DSC", "📅 By Date"],
    "🧠 AI Scanner": ["🧠 Intelligent Scanner"],
    "📊 DB Scanner": ["📊 Database Scanner"],
    "🔧 Tools": ["📤 Extract", "📁 Folder Tools", "🔍 Pattern Search"],
    "⚙️ Advanced": ["🔧 Tools"],
}

def create_scrollable_tab(parent):
    """Create a scrollable frame for a tab"""
    canvas = tk.Canvas(parent, highlightthickness=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set, height=200)
    canvas.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")

    content = ttk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    content.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Mouse wheel scrolling
    def on_mousewheel(event):
        if hasattr(event, "delta") and event.delta:
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        elif hasattr(event, "num"):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    return content

# Create notebook for tabs
notebook = ttk.Notebook(root)
notebook.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(0, 8))

# Create tabs
tabs = {}
for tab_name, section_list in tab_groups.items():
    tab_frame = ttk.Frame(notebook)
    tab_frame.columnconfigure(0, weight=1)
    tab_frame.rowconfigure(0, weight=1)
    notebook.add(tab_frame, text=tab_name)
    tabs[tab_name] = create_scrollable_tab(tab_frame)

# Render sections into tabs
for title in sorted(sections.keys()):
    # Find which tab this section belongs to
    target_tab = None
    for tab_name, section_list in tab_groups.items():
        if title in section_list:
            target_tab = tabs[tab_name]
            break

    if not target_tab:
        continue  # Skip sections not in any tab

    if title == "📁 Folder Tools":
        # Add special section with checkboxes for folder creation
        sect = ttk.LabelFrame(target_tab, text=title, style="Section.TLabelframe")
        sect.pack(fill="x", padx=0, pady=(0, 6))

        # Button row
        button_row = ttk.Frame(sect)
        button_row.pack(fill="x", padx=6, pady=(6,3))
        ttk.Button(button_row, text="Create A-Z + 0-9 Folders", command=create_alphanumeric_folders).pack(side="left", padx=(0, 6))
        ttk.Button(button_row, text="Create Custom Hierarchy", command=create_custom_hierarchy_gui).pack(side="left", padx=(0, 6))
        ttk.Button(button_row, text="🔍 Scan for Missing Files", command=scan_missing_files_gui).pack(side="left", padx=(0, 6))

        # Options row (for A-Z + 0-9 creation)
        options_row = ttk.Frame(sect)
        options_row.pack(fill="x", padx=6, pady=(0,6))
        ttk.Label(options_row, text="A-Z Options:", foreground="gray").pack(side="left", padx=(0,6))
        ttk.Checkbutton(options_row, text="A-Z", variable=var_create_az).pack(side="left", padx=(0,6))
        ttk.Checkbutton(options_row, text="0-9", variable=var_create_09).pack(side="left", padx=(0,6))
        ttk.Checkbutton(options_row, text="!@#$", variable=var_create_special).pack(side="left", padx=(0,6))
        ttk.Radiobutton(options_row, text="UPPER", variable=var_folder_case, value="upper").pack(side="left", padx=(12,6))
        ttk.Radiobutton(options_row, text="lower", variable=var_folder_case, value="lower").pack(side="left")

        ttk.Separator(target_tab, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

    elif title == "🔍 Pattern Search":
        # Add special section with input fields for pattern search
        sect = ttk.LabelFrame(target_tab, text=title, style="Section.TLabelframe")
        sect.pack(fill="x", padx=0, pady=(0, 6))

        # Pattern input row
        pattern_row = ttk.Frame(sect)
        pattern_row.pack(fill="x", padx=6, pady=(6,3))
        ttk.Label(pattern_row, text="Pattern:", width=12).pack(side="left")
        ttk.Entry(pattern_row, textvariable=var_search_pattern, width=30).pack(side="left", padx=(0,6), fill="x", expand=True)
        ttk.Label(pattern_row, text="(e.g., IMG*, *-001-*, *.jpg)", foreground="gray", font=("Segoe UI", 8)).pack(side="left")

        # Folder name row
        folder_row = ttk.Frame(sect)
        folder_row.pack(fill="x", padx=6, pady=(3,3))
        ttk.Label(folder_row, text="Folder Name:", width=12).pack(side="left")
        ttk.Entry(folder_row, textvariable=var_search_folder, width=30).pack(side="left", padx=(0,6), fill="x", expand=True)

        # Button row
        button_row = ttk.Frame(sect)
        button_row.pack(fill="x", padx=6, pady=(3,6))
        ttk.Button(button_row, text="🔍 Search & Collect Files", command=search_and_collect).pack(side="left", padx=(0,6))
        ttk.Label(button_row, text="Searches all source directories for matching files", foreground="gray", font=("Segoe UI", 8)).pack(side="left")

        ttk.Separator(target_tab, orient="horizontal").pack(fill="x", padx=0, pady=(0, 6))

    else:
        add_section(target_tab, title, sections[title])

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
footer.columnconfigure(3, weight=1)
ttk.Button(footer, text="Clear Preview", command=lambda: preview_text.delete("1.0", tk.END)).grid(row=0, column=0, pady=2, padx=4)
ttk.Button(footer, text="🛑 Cancel Operation", command=cancel_operation).grid(row=0, column=1, pady=2, padx=4)
ttk.Button(footer, text="Help", command=show_help).grid(row=0, column=2, pady=2, padx=4)
ttk.Label(footer, text=VERSION, foreground="gray").grid(row=0, column=3, pady=2)

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
Welcome to File Organizer — {VERSION}!

🧠 AI SCANNER TAB (NEW!):
• Intelligent Pattern Detection with Machine Learning
• Learns from your organization choices
• Confidence scoring: 80-99%
• View learned patterns & statistics
• The more you use it, the smarter it gets!

✨ Core Features:
• Hash-based duplicate detection
• Operation logging & UNDO
• Memory-efficient processing
• Statistics & analytics
• Pre-flight validation

📁 Data Directory:
{DATA_DIR.base_dir}

Ready to organize! Try the 🧠 AI Scanner tab!
"""
    preview_text.insert("1.0", welcome)

root.after(100, show_welcome)
root.after(150, load_recent_directories)  # v6.3: Load recent directories on startup

# START GUI
root.mainloop()
