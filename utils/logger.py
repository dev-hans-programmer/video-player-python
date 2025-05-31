"""
Logging utilities for the video player application
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
import threading

class Logger:
    """Centralized logging system for the application"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger if not already initialized"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.logger = None
        self.log_file = None
        self.log_directory = None
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logging configuration"""
        try:
            # Create logs directory
            self.log_directory = Path.cwd() / "logs"
            self.log_directory.mkdir(exist_ok=True)
            
            # Setup log file path
            timestamp = datetime.now().strftime("%Y%m%d")
            self.log_file = self.log_directory / f"video_player_{timestamp}.log"
            
            # Create logger
            self.logger = logging.getLogger("VideoPlayer")
            self.logger.setLevel(logging.DEBUG)
            
            # Clear existing handlers
            self.logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            simple_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            # Error file handler
            error_file = self.log_directory / f"errors_{timestamp}.log"
            error_handler = logging.FileHandler(error_file, encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
            
            # Log startup
            self.logger.info("=" * 80)
            self.logger.info("Beautiful Video Player - Logging System Initialized")
            self.logger.info(f"Log file: {self.log_file}")
            self.logger.info(f"Python version: {sys.version}")
            self.logger.info(f"Platform: {sys.platform}")
            self.logger.info("=" * 80)
            
        except Exception as e:
            # Fallback to basic logging if setup fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            self.logger = logging.getLogger("VideoPlayer")
            self.logger.error(f"Failed to setup advanced logging: {e}")
    
    @classmethod
    def get_logger(cls):
        """Get the logger instance"""
        instance = cls()
        return instance.logger
    
    def set_level(self, level):
        """Set logging level"""
        try:
            if isinstance(level, str):
                level = getattr(logging, level.upper())
            
            self.logger.setLevel(level)
            
            # Update console handler level
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    handler.setLevel(level)
            
            self.logger.info(f"Logging level set to: {logging.getLevelName(level)}")
            
        except Exception as e:
            self.logger.error(f"Error setting log level: {e}")
    
    def add_file_handler(self, file_path, level=logging.DEBUG):
        """Add additional file handler"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            handler = logging.FileHandler(file_path, encoding='utf-8')
            handler.setLevel(level)
            
            formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            self.logger.info(f"Added file handler: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error adding file handler: {e}")
    
    def get_log_files(self):
        """Get list of log files"""
        try:
            if not self.log_directory or not self.log_directory.exists():
                return []
            
            log_files = []
            for file_path in self.log_directory.iterdir():
                if file_path.is_file() and file_path.suffix == '.log':
                    log_files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    })
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            return log_files
            
        except Exception as e:
            self.logger.error(f"Error getting log files: {e}")
            return []
    
    def clear_old_logs(self, days_to_keep=7):
        """Clear log files older than specified days"""
        try:
            if not self.log_directory or not self.log_directory.exists():
                return 0
            
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_time.timestamp()
            
            deleted_count = 0
            for file_path in self.log_directory.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix == '.log' and 
                    file_path.stat().st_mtime < cutoff_timestamp):
                    
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old log file: {file_path.name}")
                    except Exception as del_error:
                        self.logger.warning(f"Could not delete log file {file_path}: {del_error}")
            
            self.logger.info(f"Cleared {deleted_count} old log files")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error clearing old logs: {e}")
            return 0
    
    def export_logs(self, output_file, start_date=None, end_date=None, level=None):
        """Export logs to a file with optional filtering"""
        try:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            exported_lines = 0
            
            with open(output_file, 'w', encoding='utf-8') as out_f:
                # Write header
                out_f.write(f"Video Player Log Export\n")
                out_f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if start_date:
                    out_f.write(f"Start Date: {start_date}\n")
                if end_date:
                    out_f.write(f"End Date: {end_date}\n")
                if level:
                    out_f.write(f"Min Level: {level}\n")
                out_f.write("=" * 80 + "\n\n")
                
                # Process log files
                log_files = self.get_log_files()
                for log_info in log_files:
                    log_path = Path(log_info['path'])
                    
                    try:
                        with open(log_path, 'r', encoding='utf-8') as log_f:
                            for line in log_f:
                                # Apply filters if specified
                                if self._should_include_log_line(line, start_date, end_date, level):
                                    out_f.write(line)
                                    exported_lines += 1
                    
                    except Exception as file_error:
                        self.logger.warning(f"Could not read log file {log_path}: {file_error}")
            
            self.logger.info(f"Exported {exported_lines} log lines to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            return False
    
    def _should_include_log_line(self, line, start_date=None, end_date=None, min_level=None):
        """Check if log line should be included based on filters"""
        try:
            # Basic format check
            if '|' not in line:
                return True  # Include non-standard lines
            
            parts = line.split('|')
            if len(parts) < 3:
                return True
            
            # Extract timestamp and level
            timestamp_str = parts[0].strip()
            level_str = parts[1].strip()
            
            # Date filtering
            if start_date or end_date:
                try:
                    log_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if start_date and log_date < start_date:
                        return False
                    
                    if end_date and log_date > end_date:
                        return False
                        
                except ValueError:
                    pass  # Include if can't parse date
            
            # Level filtering
            if min_level:
                level_hierarchy = {
                    'DEBUG': 0,
                    'INFO': 1,
                    'WARNING': 2,
                    'ERROR': 3,
                    'CRITICAL': 4
                }
                
                line_level = level_hierarchy.get(level_str, 0)
                min_level_num = level_hierarchy.get(min_level.upper(), 0)
                
                if line_level < min_level_num:
                    return False
            
            return True
            
        except Exception:
            return True  # Include line if filtering fails
    
    def get_log_stats(self):
        """Get logging statistics"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
                'current_log': str(self.log_file) if self.log_file else None,
                'log_directory': str(self.log_directory) if self.log_directory else None
            }
            
            log_files = self.get_log_files()
            stats['total_files'] = len(log_files)
            stats['total_size'] = sum(f['size'] for f in log_files)
            
            # Count log levels in current log file
            if self.log_file and self.log_file.exists():
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            for level in stats['levels']:
                                if f'| {level}' in line:
                                    stats['levels'][level] += 1
                                    break
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting log stats: {e}")
            return {}
    
    def create_context_logger(self, context_name):
        """Create a context-specific logger"""
        try:
            context_logger = logging.getLogger(f"VideoPlayer.{context_name}")
            context_logger.setLevel(self.logger.level)
            
            # Add the same handlers as main logger
            for handler in self.logger.handlers:
                context_logger.addHandler(handler)
            
            return context_logger
            
        except Exception as e:
            self.logger.error(f"Error creating context logger: {e}")
            return self.logger

# Performance logging decorator
def log_performance(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        logger = Logger.get_logger()
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
            
    return wrapper

# Error logging decorator
def log_errors(func):
    """Decorator to log function errors"""
    def wrapper(*args, **kwargs):
        logger = Logger.get_logger()
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
            
    return wrapper
