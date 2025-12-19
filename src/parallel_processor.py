"""Parallel conflict processing with rate limiting and colored diff output."""

import os
import sys
import select
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any, Callable

# For keyboard input on Unix systems
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Standard colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'

    @classmethod
    def supports_color(cls) -> bool:
        """Check if terminal supports colors."""
        if not hasattr(sys.stdout, 'isatty'):
            return False
        if not sys.stdout.isatty():
            return False
        if os.environ.get('NO_COLOR'):
            return False
        return True


class PauseController:
    """Controls pause/resume state with keyboard listener."""

    def __init__(self):
        self._paused = threading.Event()
        self._stop_listener = threading.Event()
        self._listener_thread: Optional[threading.Thread] = None
        self._old_settings = None
        self._print_lock = threading.Lock()

    def start(self):
        """Start the keyboard listener."""
        if not HAS_TERMIOS or not sys.stdin.isatty():
            return  # Can't listen for keys without terminal

        self._listener_thread = threading.Thread(target=self._listen_for_keys, daemon=True)
        self._listener_thread.start()

    def stop(self):
        """Stop the keyboard listener and restore terminal."""
        self._stop_listener.set()
        if self._listener_thread:
            self._listener_thread.join(timeout=0.5)
        self._restore_terminal()

    def _listen_for_keys(self):
        """Listen for keypress in background thread."""
        try:
            # Save terminal settings
            self._old_settings = termios.tcgetattr(sys.stdin)
            # Set terminal to raw mode (no echo, immediate input)
            tty.setcbreak(sys.stdin.fileno())

            while not self._stop_listener.is_set():
                # Check if input is available (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char.lower() == 'p' or char == ' ':
                        self._toggle_pause()
                    elif char.lower() == 'q':
                        # Could add quit functionality here
                        pass
        except Exception:
            pass  # Silently handle errors in keyboard listener
        finally:
            self._restore_terminal()

    def _restore_terminal(self):
        """Restore terminal to original settings."""
        if self._old_settings and HAS_TERMIOS:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass

    def _toggle_pause(self):
        """Toggle between paused and running states."""
        with self._print_lock:
            if self._paused.is_set():
                self._paused.clear()
                print(f"\n{Colors.GREEN}{Colors.BOLD}▶ RESUMED{Colors.RESET} - Processing continues...")
                print(f"{Colors.DIM}Press [P] or [Space] to pause{Colors.RESET}\n")
            else:
                self._paused.set()
                print(f"\n{Colors.YELLOW}{Colors.BOLD}⏸ PAUSED{Colors.RESET} - Processing paused")
                print(f"{Colors.DIM}Press [P] or [Space] to resume{Colors.RESET}\n")

    def wait_if_paused(self):
        """Block if paused, return immediately if not."""
        while self._paused.is_set():
            time.sleep(0.1)

    @property
    def is_paused(self) -> bool:
        return self._paused.is_set()


class ResolutionType(Enum):
    """Type of resolution applied to a conflict."""
    KEPT_EXISTING = "kept_existing"
    TRANSLATED = "translated"
    FAILED = "failed"


@dataclass
class ConflictResult:
    """Result of processing a single conflict."""
    file_path: str
    conflict_index: int
    total_conflicts: int
    resolution_type: ResolutionType
    original_text: str  # The "current" (translated) version
    incoming_text: str  # The "incoming" (English) version
    resolved_text: Optional[str]  # The final resolution
    reasoning: Optional[str] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class DiffPrinter:
    """Prints colored diffs to terminal."""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color and Colors.supports_color()
        self._lock = threading.Lock()

    def _c(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_color:
            return f"{color}{text}{Colors.RESET}"
        return text

    def print_conflict_header(self, file_path: str, conflict_idx: int, total: int,
                              file_idx: int, total_files: int):
        """Print header for a conflict being processed."""
        with self._lock:
            rel_path = os.path.basename(file_path)
            parent = os.path.basename(os.path.dirname(file_path))
            short_path = f"{parent}/{rel_path}"

            header = f"[{file_idx}/{total_files}] {short_path} • Conflict {conflict_idx}/{total}"
            print(f"\n{self._c('━' * 70, Colors.DIM)}")
            print(self._c(header, Colors.BOLD + Colors.CYAN))

    def print_diff(self, result: ConflictResult):
        """Print a colored diff showing the change made."""
        with self._lock:
            if result.resolution_type == ResolutionType.FAILED:
                self._print_failed(result)
            elif result.resolution_type == ResolutionType.KEPT_EXISTING:
                self._print_kept_existing(result)
            else:
                self._print_translated(result)

    def _print_failed(self, result: ConflictResult):
        """Print a failed resolution."""
        print(self._c("  ✗ FAILED", Colors.RED + Colors.BOLD), end="")
        if result.error:
            print(self._c(f" - {result.error}", Colors.RED))
        else:
            print(self._c(" - Marked for manual review", Colors.RED))
        print()
        self._print_text_block("  Incoming (EN)", result.incoming_text, Colors.YELLOW, max_lines=3)

    def _print_kept_existing(self, result: ConflictResult):
        """Print when existing translation was kept."""
        print(self._c("  ✓ KEPT EXISTING", Colors.GREEN + Colors.BOLD), end="")
        if result.reasoning:
            print(self._c(f" - {result.reasoning[:60]}{'...' if len(result.reasoning) > 60 else ''}", Colors.DIM))
        else:
            print()
        print()
        self._print_text_block("  Current", result.original_text, Colors.GREEN, max_lines=3)

    def _print_translated(self, result: ConflictResult):
        """Print a translation diff with before/after."""
        print(self._c("  ⟳ TRANSLATED", Colors.BLUE + Colors.BOLD))
        print()

        # Show the change: incoming (EN) -> resolved (translated)
        self._print_inline_diff(result.incoming_text, result.resolved_text)

    def _print_text_block(self, label: str, text: str, color: str, max_lines: int = 5):
        """Print a labeled block of text."""
        lines = text.split('\n')
        truncated = len(lines) > max_lines
        display_lines = lines[:max_lines]

        print(self._c(f"{label}:", Colors.DIM))
        for line in display_lines:
            # Truncate long lines
            if len(line) > 80:
                line = line[:77] + "..."
            print(self._c(f"    {line}", color))

        if truncated:
            print(self._c(f"    ... ({len(lines) - max_lines} more lines)", Colors.DIM))

    def _print_inline_diff(self, old_text: str, new_text: str, max_lines: int = 6):
        """Print side-by-side style diff showing old -> new."""
        old_lines = old_text.split('\n')
        new_lines = new_text.split('\n') if new_text else []

        # Show removed (English)
        print(self._c("  ── Incoming (English) ──", Colors.RED + Colors.DIM))
        for i, line in enumerate(old_lines[:max_lines // 2]):
            if len(line) > 75:
                line = line[:72] + "..."
            print(self._c(f"  - {line}", Colors.RED))
        if len(old_lines) > max_lines // 2:
            print(self._c(f"    ... ({len(old_lines) - max_lines // 2} more lines)", Colors.DIM))

        print()

        # Show added (translated)
        print(self._c("  ++ Resolved (Translated) ++", Colors.GREEN + Colors.DIM))
        for i, line in enumerate(new_lines[:max_lines // 2]):
            if len(line) > 75:
                line = line[:72] + "..."
            print(self._c(f"  + {line}", Colors.GREEN))
        if len(new_lines) > max_lines // 2:
            print(self._c(f"    ... ({len(new_lines) - max_lines // 2} more lines)", Colors.DIM))

    def print_progress_bar(self, current: int, total: int, width: int = 40):
        """Print a progress bar."""
        with self._lock:
            filled = int(width * current / total) if total > 0 else 0
            bar = '█' * filled + '░' * (width - filled)
            pct = (current / total * 100) if total > 0 else 0
            print(f"\r{self._c(f'Progress: [{bar}] {pct:.1f}% ({current}/{total})', Colors.CYAN)}",
                  end='', flush=True)

    def print_summary(self, results: List[ConflictResult], elapsed_time: float):
        """Print final summary of all processing."""
        with self._lock:
            kept = sum(1 for r in results if r.resolution_type == ResolutionType.KEPT_EXISTING)
            translated = sum(1 for r in results if r.resolution_type == ResolutionType.TRANSLATED)
            failed = sum(1 for r in results if r.resolution_type == ResolutionType.FAILED)
            total = len(results)

            print(f"\n{self._c('═' * 70, Colors.BOLD)}")
            print(self._c("PARALLEL PROCESSING COMPLETE", Colors.BOLD + Colors.CYAN))
            print(self._c('═' * 70, Colors.BOLD))

            print(f"\n  {self._c('Total conflicts:', Colors.WHITE)} {total}")
            print(f"  {self._c('✓ Kept existing:', Colors.GREEN)} {kept}")
            print(f"  {self._c('⟳ Translated:', Colors.BLUE)} {translated}")
            print(f"  {self._c('✗ Failed:', Colors.RED)} {failed}")
            print(f"\n  {self._c('Time elapsed:', Colors.WHITE)} {elapsed_time:.1f}s")

            if total > 0:
                rate = total / elapsed_time if elapsed_time > 0 else 0
                print(f"  {self._c('Processing rate:', Colors.WHITE)} {rate:.2f} conflicts/sec")

            print()


class ParallelConflictProcessor:
    """Processes conflicts in parallel with rate limiting."""

    def __init__(self, openai_client, translation_checker,
                 max_workers: int = 5,
                 rate_limit_delay: float = 0.2,
                 file_processor=None):
        """
        Initialize the parallel processor.

        Args:
            openai_client: The OpenAI client for translations
            translation_checker: The translation checker
            max_workers: Maximum concurrent API calls
            rate_limit_delay: Minimum delay between API calls (seconds)
            file_processor: Optional FileProcessor for immediate writes
        """
        self.openai_client = openai_client
        self.translation_checker = translation_checker
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.file_processor = file_processor

        self._semaphore = threading.Semaphore(max_workers)
        self._rate_limit_lock = threading.Lock()
        self._last_api_call = 0.0
        self._results: List[ConflictResult] = []
        self._results_lock = threading.Lock()
        self._print_lock = threading.Lock()  # Separate lock for atomic output

        self.diff_printer = DiffPrinter()
        self.pause_controller = PauseController()

        # Track files written for summary
        self._files_written: List[str] = []
        self._files_written_lock = threading.Lock()

    def _rate_limited_api_call(self, func: Callable, *args, **kwargs):
        """Execute an API call with rate limiting."""
        with self._rate_limit_lock:
            now = time.time()
            elapsed = now - self._last_api_call
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
            self._last_api_call = time.time()

        return func(*args, **kwargs)

    def _process_single_conflict(self,
                                  file_path: str,
                                  conflict_section: Dict[str, Any],
                                  conflict_idx: int,
                                  total_conflicts: int,
                                  file_idx: int,
                                  total_files: int) -> ConflictResult:
        """Process a single conflict and return the result."""
        # Wait if paused before starting
        self.pause_controller.wait_if_paused()

        start_time = time.time()

        translated_version = conflict_section['current']
        english_version = conflict_section['incoming']

        with self._semaphore:
            try:
                # Check if existing translation is close enough
                should_keep = self._rate_limited_api_call(
                    self.translation_checker.check_translation_closeness,
                    self.openai_client,
                    english_version,
                    translated_version
                )

                if should_keep:
                    result = ConflictResult(
                        file_path=file_path,
                        conflict_index=conflict_idx,
                        total_conflicts=total_conflicts,
                        resolution_type=ResolutionType.KEPT_EXISTING,
                        original_text=translated_version,
                        incoming_text=english_version,
                        resolved_text=translated_version,
                        reasoning="Translation is close enough",
                        processing_time=time.time() - start_time
                    )
                else:
                    # Need to translate
                    new_translation = self._rate_limited_api_call(
                        self.openai_client.translate,
                        english_version
                    )

                    if new_translation:
                        result = ConflictResult(
                            file_path=file_path,
                            conflict_index=conflict_idx,
                            total_conflicts=total_conflicts,
                            resolution_type=ResolutionType.TRANSLATED,
                            original_text=translated_version,
                            incoming_text=english_version,
                            resolved_text=new_translation,
                            processing_time=time.time() - start_time
                        )
                    else:
                        result = ConflictResult(
                            file_path=file_path,
                            conflict_index=conflict_idx,
                            total_conflicts=total_conflicts,
                            resolution_type=ResolutionType.FAILED,
                            original_text=translated_version,
                            incoming_text=english_version,
                            resolved_text=None,
                            error="Translation returned None",
                            processing_time=time.time() - start_time
                        )

            except Exception as e:
                result = ConflictResult(
                    file_path=file_path,
                    conflict_index=conflict_idx,
                    total_conflicts=total_conflicts,
                    resolution_type=ResolutionType.FAILED,
                    original_text=translated_version,
                    incoming_text=english_version,
                    resolved_text=None,
                    error=str(e),
                    processing_time=time.time() - start_time
                )

        # Print header and diff atomically (separate from API semaphore)
        with self._print_lock:
            self.diff_printer.print_conflict_header(
                file_path, conflict_idx, total_conflicts, file_idx, total_files
            )
            self.diff_printer.print_diff(result)

        # Store result
        with self._results_lock:
            self._results.append(result)

        return result

    def _write_file_if_ready(self, conflict_file: Dict[str, Any], codebase_path: str, dry_run: bool = False):
        """Write a file immediately after all its conflicts are resolved."""
        if not self.file_processor or dry_run:
            return

        file_path = conflict_file['file_path']
        relative_path = os.path.relpath(file_path, codebase_path)

        # Check if all conflicts in this file have been processed (have resolution key)
        all_processed = all('resolution' in c for c in conflict_file['conflicts'])
        if not all_processed:
            return

        # Check if any conflicts were resolved
        resolved_count = sum(1 for c in conflict_file['conflicts'] if c.get('resolution') is not None)
        if resolved_count == 0:
            return

        # Write the file
        with self._print_lock:
            if self.file_processor.resolve_conflicts_in_file(file_path, conflict_file):
                print(f"\n{self.diff_printer._c(f'  💾 SAVED: {relative_path}', Colors.GREEN + Colors.BOLD)}")
                with self._files_written_lock:
                    self._files_written.append(relative_path)

    def process_all_conflicts(self, conflicts: List[Dict[str, Any]],
                              codebase_path: str,
                              dry_run: bool = False) -> List[ConflictResult]:
        """
        Process all conflicts in parallel, writing files immediately.

        Args:
            conflicts: List of conflict file data from ConflictDetector
            codebase_path: Base path for relative path display
            dry_run: If True, don't write files

        Returns:
            List of ConflictResult objects
        """
        self._results = []
        self._files_written = []
        start_time = time.time()

        # Start keyboard listener for pause/resume
        self.pause_controller.start()

        try:
            # Count total conflicts
            total_files = len(conflicts)
            total_conflict_count = sum(len(cf['conflicts']) for cf in conflicts)

            print(f"\n{self.diff_printer._c(f'Processing {total_conflict_count} conflicts across {total_files} files...', Colors.CYAN + Colors.BOLD)}")
            print(f"{self.diff_printer._c(f'Using {self.max_workers} parallel workers with {self.rate_limit_delay}s rate limit', Colors.DIM)}")
            if not dry_run and self.file_processor:
                print(f"{self.diff_printer._c('Files will be saved immediately after processing', Colors.DIM)}")
            print(f"{self.diff_printer._c('Press [P] or [Space] to pause/resume', Colors.YELLOW)}")

            # Process file by file for immediate writes
            for file_idx, conflict_file in enumerate(conflicts, 1):
                # Wait if paused before starting a new file
                self.pause_controller.wait_if_paused()

                file_path = conflict_file['file_path']
                total_conflicts_in_file = len(conflict_file['conflicts'])

                # Build tasks for this file
                file_tasks = []
                for conflict_idx, conflict_section in enumerate(conflict_file['conflicts'], 1):
                    file_tasks.append({
                        'file_path': file_path,
                        'conflict_section': conflict_section,
                        'conflict_idx': conflict_idx,
                        'total_conflicts': total_conflicts_in_file,
                        'file_idx': file_idx,
                        'total_files': total_files
                    })

                # Process this file's conflicts in parallel
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {}
                    for task in file_tasks:
                        future = executor.submit(
                            self._process_single_conflict,
                            task['file_path'],
                            task['conflict_section'],
                            task['conflict_idx'],
                            task['total_conflicts'],
                            task['file_idx'],
                            task['total_files']
                        )
                        futures[future] = task

                    # Wait for all conflicts in this file to complete
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            task = futures[future]
                            task['conflict_section']['resolution'] = result.resolved_text
                        except Exception as e:
                            print(f"\n{self.diff_printer._c(f'Error processing conflict: {e}', Colors.RED)}")

                # Write file immediately after all its conflicts are done
                self._write_file_if_ready(conflict_file, codebase_path, dry_run)

        finally:
            # Always stop the keyboard listener
            self.pause_controller.stop()

        elapsed = time.time() - start_time
        self.diff_printer.print_summary(self._results, elapsed)

        # Show files written
        if self._files_written:
            with self._print_lock:
                print(f"\n{self.diff_printer._c(f'Files written: {len(self._files_written)}', Colors.GREEN)}")
                for f in self._files_written[:5]:
                    print(f"  {self.diff_printer._c(f'• {f}', Colors.DIM)}")
                if len(self._files_written) > 5:
                    print(f"  {self.diff_printer._c(f'... and {len(self._files_written) - 5} more', Colors.DIM)}")

        return self._results
