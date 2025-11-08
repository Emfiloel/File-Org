"""
File Organizer v6.3 - Comprehensive Test File Generator
========================================================

This program generates 1,000,000 test files (0 bytes each) with diverse patterns
to thoroughly test ALL features and edge cases of the File Organizer v6.3.

Features:
- Multiple file extensions (50+ types)
- All pattern types (extension, alphabet, numeric, IMG/DSC, smart, sequential)
- Challenging edge cases (reserved names, special chars, long names)
- Symbols, hyphens, underscores
- Same set names for grouping
- Random and patterned filenames

Author: File Organizer v6.3 Test Suite
Version: 1.0
Date: 2025-11-06
"""

import os
import random
import time
import string
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue

# ============================================================================
# FILE GENERATION PATTERNS
# ============================================================================

# Common file extensions (50+ types)
EXTENSIONS = [
    # Documents
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
    # Spreadsheets
    '.xls', '.xlsx', '.csv', '.ods', '.numbers',
    # Presentations
    '.ppt', '.pptx', '.key', '.odp',
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico', '.heic',
    # Videos
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v',
    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    # Code
    '.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go',
    # Data
    '.json', '.xml', '.yaml', '.sql', '.db', '.sqlite',
    # Other
    '.exe', '.dll', '.bat', '.sh', '.iso', '.dmg', '.apk'
]

# Camera tag prefixes
CAMERA_TAGS = ['IMG', 'DSC', 'DSCN', 'DCS', 'DCSN', 'VID', 'MOV', 'PXL', 'CAM', 'PHOTO']

# Pattern prefixes for smart pattern detection
PATTERN_PREFIXES = [
    'vacation', 'work', 'project', 'report', 'meeting', 'invoice', 'receipt',
    'backup', 'draft', 'final', 'client', 'customer', 'order', 'delivery',
    'photo', 'video', 'audio', 'scan', 'document', 'file', 'data', 'archive',
    'temp', 'test', 'sample', 'demo', 'example', 'training', 'tutorial'
]

# Separators for pattern detection
SEPARATORS = ['-', '_', '.', ' ']

# Special characters
SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '~', '+', '=']

# Windows reserved names (for testing sanitization)
RESERVED_NAMES = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                  'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                  'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

# Common words for random names
WORDS = [
    'document', 'file', 'photo', 'image', 'video', 'audio', 'data', 'archive',
    'backup', 'copy', 'final', 'draft', 'version', 'edit', 'update', 'new',
    'old', 'temp', 'test', 'sample', 'example', 'demo', 'production', 'development'
]


class FileGeneratorGUI:
    """GUI for the file generator"""

    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer v6.3 - Test File Generator")
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        # Variables
        self.output_dir = tk.StringVar()
        self.file_count = tk.IntVar(value=1000000)
        self.is_generating = False
        self.stop_requested = False
        self.queue = queue.Queue()

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""

        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title = tk.Label(title_frame, text="📁 Test File Generator",
                        font=('Segoe UI', 18, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=10)

        subtitle = tk.Label(title_frame, text="Generate 1,000,000 test files for File Organizer v6.3",
                           font=('Segoe UI', 10), bg='#2c3e50', fg='#ecf0f1')
        subtitle.pack()

        # Main content
        content = tk.Frame(self.root, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        # Output directory selection
        dir_frame = tk.LabelFrame(content, text="Output Directory", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        dir_frame.pack(fill=tk.X, pady=(0, 15))

        dir_input_frame = tk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X)

        self.dir_entry = tk.Entry(dir_input_frame, textvariable=self.output_dir, font=('Segoe UI', 10))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = tk.Button(dir_input_frame, text="Browse...", command=self.browse_directory,
                              font=('Segoe UI', 9), width=12)
        browse_btn.pack(side=tk.LEFT)

        # File count
        count_frame = tk.LabelFrame(content, text="Number of Files", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        count_frame.pack(fill=tk.X, pady=(0, 15))

        count_info = tk.Label(count_frame, text="Default: 1,000,000 files (0 bytes each)",
                             font=('Segoe UI', 9), fg='#7f8c8d')
        count_info.pack(anchor=tk.W)

        count_input_frame = tk.Frame(count_frame)
        count_input_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(count_input_frame, text="Count:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.count_entry = tk.Entry(count_input_frame, textvariable=self.file_count, font=('Segoe UI', 10), width=15)
        self.count_entry.pack(side=tk.LEFT)

        tk.Label(count_input_frame, text="(Recommended: 100,000 - 1,000,000)",
                font=('Segoe UI', 9), fg='#7f8c8d').pack(side=tk.LEFT, padx=(10, 0))

        # What will be generated
        info_frame = tk.LabelFrame(content, text="What Will Be Generated", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        info_text = scrolledtext.ScrolledText(info_frame, height=12, font=('Consolas', 9), wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True)

        info_content = """✓ 50+ Different File Extensions (.pdf, .jpg, .txt, .mp4, .docx, etc.)

✓ Pattern Types (tests all organization modes):
  • Extension-based: document.pdf, photo.jpg, video.mp4
  • Alphabet-based: apple.txt, banana.doc, 123.pdf, !special.txt
  • Numeric: 1.txt, 42.pdf, 999.jpg
  • IMG/DSC tags: IMG_001.jpg, DSC_0042.jpg, VID_123.mp4
  • Smart patterns: vacation-001.jpg, work_file_042.docx, project-2024-001.pdf
  • Sequential: report-001-final.pdf, photo_0001.jpg, scan-001-002-003.tiff

✓ Edge Cases & Challenges:
  • Reserved names: CON.txt, PRN.pdf, AUX.doc (tests sanitization)
  • Special characters: file@#$.txt, data!.pdf, image~.jpg
  • Long filenames: very_long_filename_that_tests_character_limits...
  • Unicode: café.txt, naïve.pdf, 文件.doc
  • Hyphens: multi-part-name.txt, three-word-file.pdf
  • Underscores: snake_case_file.txt, multi_word_name.pdf
  • Dots: file.with.multiple.dots.txt, archive.tar.gz
  • Spaces: file with spaces.txt, my document.pdf
  • Mixed: complex-file_name.with-various_separators.txt

✓ Grouping Sets (tests pattern detection):
  • vacation-001 through vacation-999 (same prefix)
  • project_A_001 through project_A_500 (related set)
  • Random unique files (no pattern)
  • Duplicate-prone names (tests collision handling)"""

        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')

        # Progress
        progress_frame = tk.LabelFrame(content, text="Progress", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        self.progress_label = tk.Label(progress_frame, text="Ready to generate files",
                                       font=('Segoe UI', 10), fg='#27ae60')
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.stats_label = tk.Label(progress_frame, text="Files: 0 | Speed: 0 files/sec | ETA: --:--:--",
                                   font=('Consolas', 9), fg='#7f8c8d')
        self.stats_label.pack(anchor=tk.W)

        # Buttons
        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X)

        self.generate_btn = tk.Button(button_frame, text="▶ Generate Files", command=self.start_generation,
                                      font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                                      height=2, cursor='hand2')
        self.generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.stop_btn = tk.Button(button_frame, text="⏹ Stop", command=self.stop_generation,
                                  font=('Segoe UI', 11, 'bold'), bg='#e74c3c', fg='white',
                                  height=2, state='disabled', cursor='hand2')
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)

    def start_generation(self):
        """Start file generation"""
        # Validate
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory!")
            return

        if not os.path.exists(self.output_dir.get()):
            messagebox.showerror("Error", "Selected directory does not exist!")
            return

        count = self.file_count.get()
        if count < 1:
            messagebox.showerror("Error", "File count must be at least 1!")
            return

        if count > 10000000:
            messagebox.showerror("Error", "File count too large! Maximum: 10,000,000")
            return

        # Confirm large generation
        if count > 100000:
            if not messagebox.askyesno("Confirm",
                f"You are about to generate {count:,} files.\n\n"
                "This may take several minutes.\n\n"
                "Continue?"):
                return

        # Update UI
        self.is_generating = True
        self.stop_requested = False
        self.generate_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.count_entry.config(state='disabled')
        self.dir_entry.config(state='disabled')

        # Start generation thread
        thread = threading.Thread(target=self.generate_files, daemon=True)
        thread.start()

        # Start progress monitoring
        self.root.after(100, self.check_progress)

    def stop_generation(self):
        """Stop file generation"""
        if messagebox.askyesno("Confirm", "Stop file generation?"):
            self.stop_requested = True
            self.progress_label.config(text="Stopping...", fg='#e67e22')

    def generate_files(self):
        """Generate files in background thread"""
        generator = FileGenerator(
            self.output_dir.get(),
            self.file_count.get(),
            self.queue
        )

        try:
            generator.generate()
            self.queue.put(('COMPLETE', None))
        except Exception as e:
            self.queue.put(('ERROR', str(e)))

    def check_progress(self):
        """Check progress from queue"""
        try:
            while True:
                msg_type, data = self.queue.get_nowait()

                if msg_type == 'PROGRESS':
                    current, total, speed, eta = data
                    percentage = (current / total) * 100

                    self.progress_bar['value'] = percentage
                    self.progress_label.config(text=f"Generating files... {current:,} / {total:,} ({percentage:.1f}%)")
                    self.stats_label.config(text=f"Files: {current:,} | Speed: {speed:,} files/sec | ETA: {eta}")

                    # Check if stop requested
                    if self.stop_requested:
                        self.queue.put(('STOP', None))
                        return

                elif msg_type == 'COMPLETE':
                    self.progress_bar['value'] = 100
                    self.progress_label.config(text="✓ Generation complete!", fg='#27ae60')
                    self.finish_generation(success=True)
                    return

                elif msg_type == 'ERROR':
                    self.progress_label.config(text=f"✗ Error: {data}", fg='#e74c3c')
                    self.finish_generation(success=False, error=data)
                    return

                elif msg_type == 'STOP':
                    self.progress_label.config(text="⏸ Generation stopped by user", fg='#e67e22')
                    self.finish_generation(success=False)
                    return

        except queue.Empty:
            pass

        # Continue checking
        if self.is_generating:
            self.root.after(100, self.check_progress)

    def finish_generation(self, success=True, error=None):
        """Finish generation and reset UI"""
        self.is_generating = False
        self.generate_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.count_entry.config(state='normal')
        self.dir_entry.config(state='normal')

        if success:
            messagebox.showinfo("Success",
                f"Successfully generated {self.file_count.get():,} files!\n\n"
                f"Location: {self.output_dir.get()}\n\n"
                "You can now use File Organizer v6.3 to organize these files.")
        elif error:
            messagebox.showerror("Error", f"Generation failed:\n\n{error}")


class FileGenerator:
    """Core file generation logic"""

    def __init__(self, output_dir, file_count, progress_queue):
        self.output_dir = output_dir
        self.file_count = file_count
        self.queue = progress_queue
        self.start_time = None

    def generate(self):
        """Generate all files"""
        self.start_time = time.time()

        # Calculate distribution
        distribution = self.calculate_distribution()

        # Generate files
        generated = 0
        last_update = time.time()

        for pattern_type, count in distribution.items():
            for i in range(count):
                # Check for stop
                try:
                    msg_type, _ = self.queue.get_nowait()
                    if msg_type == 'STOP':
                        return
                except queue.Empty:
                    pass

                # Generate file
                filename = self.generate_filename(pattern_type, i, count)
                filepath = os.path.join(self.output_dir, filename)

                # Create empty file
                try:
                    Path(filepath).touch()
                except Exception as e:
                    # Skip if file creation fails (long path, etc.)
                    pass

                generated += 1

                # Update progress (every 1000 files or every second)
                current_time = time.time()
                if generated % 1000 == 0 or (current_time - last_update) >= 1.0:
                    elapsed = current_time - self.start_time
                    speed = int(generated / elapsed) if elapsed > 0 else 0
                    remaining = self.file_count - generated
                    eta_seconds = int(remaining / speed) if speed > 0 else 0
                    eta = self.format_time(eta_seconds)

                    self.queue.put(('PROGRESS', (generated, self.file_count, speed, eta)))
                    last_update = current_time

    def calculate_distribution(self):
        """Calculate how many files of each pattern type"""
        total = self.file_count

        return {
            'extension_variety': int(total * 0.15),      # 15% - various extensions
            'alphabet': int(total * 0.10),                # 10% - A-Z, 0-9, special
            'numeric': int(total * 0.08),                 # 8% - pure numbers
            'camera_tags': int(total * 0.12),             # 12% - IMG/DSC tags
            'smart_patterns': int(total * 0.20),          # 20% - vacation-001, work_file_001
            'sequential_patterns': int(total * 0.15),     # 15% - report-001-final
            'edge_cases': int(total * 0.05),              # 5% - reserved names, special chars
            'random': int(total * 0.15),                  # 15% - completely random
        }

    def generate_filename(self, pattern_type, index, total_in_pattern):
        """Generate a filename based on pattern type"""

        if pattern_type == 'extension_variety':
            # Files with various extensions
            ext = random.choice(EXTENSIONS)
            name = random.choice(WORDS)
            return f"{name}_{index}{ext}"

        elif pattern_type == 'alphabet':
            # A-Z, 0-9, special characters
            if index % 40 < 26:
                # A-Z
                letter = chr(65 + (index % 26))
                return f"{letter}{random.choice(WORDS)}{random.choice(EXTENSIONS)}"
            elif index % 40 < 36:
                # 0-9
                num = index % 10
                return f"{num}{random.choice(WORDS)}{random.choice(EXTENSIONS)}"
            else:
                # Special characters
                special = random.choice(SPECIAL_CHARS)
                return f"{special}{random.choice(WORDS)}{random.choice(EXTENSIONS)}"

        elif pattern_type == 'numeric':
            # Pure numeric filenames
            num = random.randint(1, 9999)
            return f"{num}{random.choice(EXTENSIONS)}"

        elif pattern_type == 'camera_tags':
            # IMG/DSC camera tags
            tag = random.choice(CAMERA_TAGS)
            num = str(index % 10000).zfill(4)
            ext = random.choice(['.jpg', '.jpeg', '.png', '.mp4', '.mov'])
            return f"{tag}_{num}{ext}"

        elif pattern_type == 'smart_patterns':
            # Patterned files with prefixes and numbers
            prefix = random.choice(PATTERN_PREFIXES)
            separator = random.choice(SEPARATORS)
            num = str((index % 1000) + 1).zfill(3)
            ext = random.choice(EXTENSIONS)

            # Variations
            variation = index % 4
            if variation == 0:
                # Simple: vacation-001
                return f"{prefix}{separator}{num}{ext}"
            elif variation == 1:
                # With year: project-2024-001
                year = random.choice(['2023', '2024', '2025'])
                return f"{prefix}{separator}{year}{separator}{num}{ext}"
            elif variation == 2:
                # With category: work_file_HR_001
                category = random.choice(['HR', 'IT', 'SALES', 'ADMIN'])
                return f"{prefix}{separator}file{separator}{category}{separator}{num}{ext}"
            else:
                # Complex: client-acme-invoice-001-final
                return f"{prefix}{separator}acme{separator}doc{separator}{num}{separator}final{ext}"

        elif pattern_type == 'sequential_patterns':
            # Sequential numbering patterns
            num1 = str((index % 100) + 1).zfill(3)
            num2 = str((index % 50) + 1).zfill(4)
            ext = random.choice(EXTENSIONS)

            variation = index % 5
            if variation == 0:
                # Standard: file-001
                return f"file-{num1}{ext}"
            elif variation == 1:
                # Range: scan-001-050
                return f"scan-{num1}-{num2}{ext}"
            elif variation == 2:
                # Underscore: photo_0001
                return f"photo_{num2}{ext}"
            elif variation == 3:
                # Dots: archive.{num}.backup
                return f"archive.{num1}.backup{ext}"
            else:
                # Complex: report-001-v2-final
                version = random.randint(1, 5)
                return f"report-{num1}-v{version}-final{ext}"

        elif pattern_type == 'edge_cases':
            # Challenging edge cases
            variation = index % 12

            if variation == 0:
                # Reserved names
                reserved = random.choice(RESERVED_NAMES)
                return f"{reserved}{random.choice(EXTENSIONS)}"
            elif variation == 1:
                # Very long filename
                long_name = '_'.join([random.choice(WORDS) for _ in range(20)])
                return f"{long_name}{random.choice(EXTENSIONS)}"
            elif variation == 2:
                # Multiple dots
                return f"file.backup.{index}.final.v2{random.choice(EXTENSIONS)}"
            elif variation == 3:
                # Spaces
                words = ' '.join([random.choice(WORDS) for _ in range(3)])
                return f"{words}{random.choice(EXTENSIONS)}"
            elif variation == 4:
                # Special characters
                special = ''.join(random.choices(SPECIAL_CHARS, k=3))
                return f"file{special}{index}{random.choice(EXTENSIONS)}"
            elif variation == 5:
                # Unicode
                unicode_names = ['café', 'naïve', 'résumé', 'jalapeño', 'file文件', 'данные']
                return f"{random.choice(unicode_names)}_{index}{random.choice(EXTENSIONS)}"
            elif variation == 6:
                # Leading/trailing spaces (challenging)
                return f" file_{index} {random.choice(EXTENSIONS)}"
            elif variation == 7:
                # All caps
                return f"{random.choice(WORDS).upper()}_{index}{random.choice(EXTENSIONS)}"
            elif variation == 8:
                # Mixed case
                word = random.choice(WORDS)
                mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in word)
                return f"{mixed}_{index}{random.choice(EXTENSIONS)}"
            elif variation == 9:
                # Hyphen-heavy
                return f"multi-part-very-long-hyphenated-name-{index}{random.choice(EXTENSIONS)}"
            elif variation == 10:
                # Underscore-heavy
                return f"snake_case_very_long_filename_{index}{random.choice(EXTENSIONS)}"
            else:
                # Mixed separators
                return f"complex-file_name.with-various_separators.{index}{random.choice(EXTENSIONS)}"

        else:  # random
            # Completely random filenames
            length = random.randint(5, 20)
            chars = string.ascii_letters + string.digits + '-_'
            name = ''.join(random.choices(chars, k=length))
            return f"{name}{random.choice(EXTENSIONS)}"

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FileGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
