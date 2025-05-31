"""
Helper utilities and common functions for the video player
"""

import os
import sys
import time
import threading
import functools
from pathlib import Path
from typing import Any, Callable, Optional, Union
import tkinter as tk
from tkinter import messagebox

from utils.logger import Logger

def setup_exception_handler():
    """Setup global exception handler for unhandled exceptions"""
    logger = Logger.get_logger()
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            logger.info("Application interrupted by user")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logger.critical(
            "Unhandled exception occurred",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Show error dialog in main thread
        try:
            if threading.current_thread() is threading.main_thread():
                error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
                messagebox.showerror("Critical Error", error_msg)
        except Exception:
            pass  # Ignore errors in error handler
    
    # Set the exception handler
    sys.excepthook = handle_exception
    logger.info("Global exception handler installed")

def safe_call(func: Callable, *args, default=None, **kwargs) -> Any:
    """Safely call a function and return default value on error"""
    logger = Logger.get_logger()
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe call failed for {func.__name__}: {e}")
        return default

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator to retry function on failure"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = Logger.get_logger()
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    else:
                        logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                        time.sleep(delay)
            
        return wrapper
    return decorator

def debounce(wait_time: float):
    """Decorator to debounce function calls"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, '_timer'):
                wrapper._timer = None
            
            def call_function():
                wrapper._timer = None
                return func(*args, **kwargs)
            
            # Cancel previous timer
            if wrapper._timer is not None:
                wrapper._timer.cancel()
            
            # Start new timer
            wrapper._timer = threading.Timer(wait_time, call_function)
            wrapper._timer.start()
            
        return wrapper
    return decorator

def throttle(min_interval: float):
    """Decorator to throttle function calls"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, '_last_called'):
                wrapper._last_called = 0
            
            now = time.time()
            if now - wrapper._last_called >= min_interval:
                wrapper._last_called = now
                return func(*args, **kwargs)
            
        return wrapper
    return decorator

def ensure_main_thread(func: Callable) -> Callable:
    """Decorator to ensure function runs in main thread"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)
        else:
            # Schedule on main thread
            root = tk._default_root
            if root:
                return root.after_idle(lambda: func(*args, **kwargs))
            else:
                logger = Logger.get_logger()
                logger.warning(f"Cannot schedule {func.__name__} on main thread - no Tkinter root")
                
    return wrapper

def format_time(seconds: float) -> str:
    """Format time in HH:MM:SS or MM:SS format"""
    if seconds < 0:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end"""
    return start + (end - start) * clamp(t, 0.0, 1.0)

def ease_in_out(t: float) -> float:
    """Ease in-out animation curve"""
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def validate_path(path: Union[str, Path], must_exist: bool = True, must_be_file: bool = False, must_be_dir: bool = False) -> bool:
    """Validate file/directory path"""
    try:
        path = Path(path)
        
        if must_exist and not path.exists():
            return False
        
        if path.exists():
            if must_be_file and not path.is_file():
                return False
            if must_be_dir and not path.is_dir():
                return False
        
        return True
        
    except Exception:
        return False

def get_unique_name(base_name: str, existing_names: list) -> str:
    """Get unique name by adding number suffix"""
    if base_name not in existing_names:
        return base_name
    
    counter = 1
    while True:
        unique_name = f"{base_name} ({counter})"
        if unique_name not in existing_names:
            return unique_name
        counter += 1
        
        # Safety break
        if counter > 1000:
            import uuid
            return f"{base_name} ({uuid.uuid4().hex[:8]})"

def is_process_running(process_name: str) -> bool:
    """Check if a process with given name is running"""
    try:
        import psutil
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return False
        
    except ImportError:
        # psutil not available, use platform-specific methods
        if sys.platform == "win32":
            import subprocess
            try:
                output = subprocess.check_output(['tasklist'], shell=True, text=True)
                return process_name.lower() in output.lower()
            except subprocess.CalledProcessError:
                return False
        else:
            import subprocess
            try:
                output = subprocess.check_output(['ps', 'aux'], text=True)
                return process_name.lower() in output.lower()
            except subprocess.CalledProcessError:
                return False

def get_system_info() -> dict:
    """Get system information"""
    info = {
        'platform': sys.platform,
        'python_version': sys.version,
        'executable': sys.executable,
        'cwd': os.getcwd(),
        'pid': os.getpid()
    }
    
    try:
        import platform
        info.update({
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        })
    except ImportError:
        pass
    
    try:
        import psutil
        info.update({
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').total if sys.platform != 'win32' else psutil.disk_usage('C:').total
        })
    except ImportError:
        pass
    
    return info

def create_backup(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """Create backup of a file"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        if backup_dir is None:
            backup_dir = file_path.parent / "backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        # Copy file
        import shutil
        shutil.copy2(str(file_path), str(backup_path))
        
        return backup_path
        
    except Exception as e:
        logger = Logger.get_logger()
        logger.error(f"Error creating backup: {e}")
        return None

def cleanup_backups(backup_dir: Union[str, Path], max_backups: int = 10):
    """Clean up old backup files, keeping only the most recent ones"""
    try:
        backup_dir = Path(backup_dir)
        
        if not backup_dir.exists():
            return
        
        # Get all backup files
        backup_files = []
        for file_path in backup_dir.iterdir():
            if file_path.is_file():
                backup_files.append((file_path, file_path.stat().st_mtime))
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        for file_path, _ in backup_files[max_backups:]:
            try:
                file_path.unlink()
            except Exception as e:
                logger = Logger.get_logger()
                logger.warning(f"Could not delete backup file {file_path}: {e}")
        
    except Exception as e:
        logger = Logger.get_logger()
        logger.error(f"Error cleaning up backups: {e}")

def monitor_memory_usage(threshold_mb: int = 500):
    """Monitor memory usage and log warnings if threshold is exceeded"""
    try:
        import psutil
        
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > threshold_mb:
            logger = Logger.get_logger()
            logger.warning(f"High memory usage detected: {memory_mb:.1f} MB")
        
        return memory_mb
        
    except ImportError:
        return 0

def create_thread_safe_dict():
    """Create a thread-safe dictionary"""
    class ThreadSafeDict:
        def __init__(self):
            self._dict = {}
            self._lock = threading.RLock()
        
        def __getitem__(self, key):
            with self._lock:
                return self._dict[key]
        
        def __setitem__(self, key, value):
            with self._lock:
                self._dict[key] = value
        
        def __delitem__(self, key):
            with self._lock:
                del self._dict[key]
        
        def __contains__(self, key):
            with self._lock:
                return key in self._dict
        
        def get(self, key, default=None):
            with self._lock:
                return self._dict.get(key, default)
        
        def pop(self, key, default=None):
            with self._lock:
                return self._dict.pop(key, default)
        
        def keys(self):
            with self._lock:
                return list(self._dict.keys())
        
        def values(self):
            with self._lock:
                return list(self._dict.values())
        
        def items(self):
            with self._lock:
                return list(self._dict.items())
        
        def clear(self):
            with self._lock:
                self._dict.clear()
        
        def update(self, other):
            with self._lock:
                self._dict.update(other)
    
    return ThreadSafeDict()

class PerformanceTimer:
    """Context manager for measuring execution time"""
    
    def __init__(self, name: str = "Operation", log_result: bool = True):
        self.name = name
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.logger = Logger.get_logger()
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        
        if self.log_result:
            self.logger.debug(f"{self.name} completed in {self.duration:.4f} seconds")
    
    def get_duration(self) -> float:
        """Get duration in seconds"""
        return self.duration or 0.0

class RateLimiter:
    """Rate limiter to control function call frequency"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def allow_call(self) -> bool:
        """Check if call is allowed within rate limit"""
        with self.lock:
            now = time.time()
            
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # Check if we can make another call
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Get time to wait before next call is allowed"""
        with self.lock:
            if len(self.calls) < self.max_calls:
                return 0.0
            
            oldest_call = min(self.calls)
            return max(0.0, self.time_window - (time.time() - oldest_call))

def extract_error_info(exception: Exception) -> dict:
    """Extract detailed information from an exception"""
    import traceback
    
    return {
        'type': exception.__class__.__name__,
        'message': str(exception),
        'module': exception.__class__.__module__,
        'traceback': traceback.format_exc(),
        'args': exception.args if hasattr(exception, 'args') else []
    }

def schedule_periodic_task(func: Callable, interval: float, run_immediately: bool = False) -> threading.Timer:
    """Schedule a function to run periodically"""
    def run_periodic():
        try:
            func()
        except Exception as e:
            logger = Logger.get_logger()
            logger.error(f"Error in periodic task {func.__name__}: {e}")
        finally:
            # Schedule next run
            timer = threading.Timer(interval, run_periodic)
            timer.daemon = True
            timer.start()
            return timer
    
    if run_immediately:
        # Run once immediately, then start periodic execution
        try:
            func()
        except Exception as e:
            logger = Logger.get_logger()
            logger.error(f"Error in immediate execution of {func.__name__}: {e}")
    
    # Start periodic execution
    timer = threading.Timer(interval, run_periodic)
    timer.daemon = True
    timer.start()
    return timer
