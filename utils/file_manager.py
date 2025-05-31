"""
File management utilities for the video player
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Union
import json

from utils.logger import Logger

class FileManager:
    """File operations and management"""
    
    def __init__(self, settings):
        """Initialize file manager"""
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # File type mappings
        self.video_extensions = set()
        self.audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
        self.subtitle_extensions = {'.srt', '.vtt', '.ass', '.ssa', '.sub', '.idx'}
        
        # Load supported formats
        self._load_supported_formats()
        
        self.logger.info("File manager initialized")
    
    def _load_supported_formats(self):
        """Load supported video formats from settings"""
        formats = self.settings.get_supported_formats()
        self.video_extensions = {f'.{fmt}' for fmt in formats}
    
    def get_video_files(self, directory: Union[str, Path], recursive: bool = False) -> List[Path]:
        """Get all video files from directory"""
        try:
            directory = Path(directory)
            
            if not directory.exists() or not directory.is_dir():
                self.logger.warning(f"Directory not found: {directory}")
                return []
            
            video_files = []
            
            if recursive:
                pattern = "**/*"
                paths = directory.glob(pattern)
            else:
                paths = directory.iterdir()
            
            for path in paths:
                if path.is_file() and self.is_video_file(path):
                    video_files.append(path)
            
            # Sort naturally
            video_files.sort(key=lambda x: x.name.lower())
            
            self.logger.debug(f"Found {len(video_files)} video files in {directory}")
            return video_files
            
        except Exception as e:
            self.logger.error(f"Error getting video files: {e}")
            return []
    
    def is_video_file(self, file_path: Union[str, Path]) -> bool:
        """Check if file is a supported video file"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            return extension in self.video_extensions
            
        except Exception as e:
            self.logger.error(f"Error checking video file: {e}")
            return False
    
    def is_audio_file(self, file_path: Union[str, Path]) -> bool:
        """Check if file is an audio file"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            return extension in self.audio_extensions
            
        except Exception as e:
            self.logger.error(f"Error checking audio file: {e}")
            return False
    
    def is_subtitle_file(self, file_path: Union[str, Path]) -> bool:
        """Check if file is a subtitle file"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            return extension in self.subtitle_extensions
            
        except Exception as e:
            self.logger.error(f"Error checking subtitle file: {e}")
            return False
    
    def find_subtitle_files(self, video_path: Union[str, Path]) -> List[Path]:
        """Find subtitle files for a video"""
        try:
            video_path = Path(video_path)
            video_dir = video_path.parent
            video_stem = video_path.stem
            
            subtitle_files = []
            
            # Look for subtitle files with same name
            for subtitle_ext in self.subtitle_extensions:
                subtitle_path = video_dir / f"{video_stem}{subtitle_ext}"
                if subtitle_path.exists():
                    subtitle_files.append(subtitle_path)
            
            # Look for subtitle files with language codes
            for file_path in video_dir.iterdir():
                if (file_path.is_file() and 
                    file_path.stem.startswith(video_stem) and 
                    file_path.suffix.lower() in self.subtitle_extensions):
                    if file_path not in subtitle_files:
                        subtitle_files.append(file_path)
            
            self.logger.debug(f"Found {len(subtitle_files)} subtitle files for {video_path}")
            return subtitle_files
            
        except Exception as e:
            self.logger.error(f"Error finding subtitle files: {e}")
            return []
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict:
        """Get detailed file information"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {}
            
            stat = file_path.stat()
            
            info = {
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'parent': str(file_path.parent),
                'absolute_path': str(file_path.absolute())
            }
            
            # Add MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            info['mime_type'] = mime_type
            
            # Add file type category
            if self.is_video_file(file_path):
                info['category'] = 'video'
            elif self.is_audio_file(file_path):
                info['category'] = 'audio'
            elif self.is_subtitle_file(file_path):
                info['category'] = 'subtitle'
            else:
                info['category'] = 'other'
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {}
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        try:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                
        except Exception as e:
            self.logger.error(f"Error formatting file size: {e}")
            return "Unknown"
    
    def get_safe_filename(self, filename: str) -> str:
        """Get safe filename by removing invalid characters"""
        try:
            # Remove invalid characters for Windows/Unix
            invalid_chars = '<>:"/\\|?*'
            safe_name = ''.join(c for c in filename if c not in invalid_chars)
            
            # Remove leading/trailing spaces and dots
            safe_name = safe_name.strip(' .')
            
            # Ensure it's not empty
            if not safe_name:
                safe_name = "untitled"
            
            return safe_name
            
        except Exception as e:
            self.logger.error(f"Error creating safe filename: {e}")
            return "untitled"
    
    def create_directory(self, directory: Union[str, Path]) -> bool:
        """Create directory if it doesn't exist"""
        try:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Directory created: {directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating directory {directory}: {e}")
            return False
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy file to destination"""
        try:
            source = Path(source)
            destination = Path(destination)
            
            if not source.exists():
                self.logger.error(f"Source file not found: {source}")
                return False
            
            # Create destination directory if needed
            self.create_directory(destination.parent)
            
            # Copy file
            shutil.copy2(str(source), str(destination))
            self.logger.info(f"File copied: {source} -> {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying file: {e}")
            return False
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Move file to destination"""
        try:
            source = Path(source)
            destination = Path(destination)
            
            if not source.exists():
                self.logger.error(f"Source file not found: {source}")
                return False
            
            # Create destination directory if needed
            self.create_directory(destination.parent)
            
            # Move file
            shutil.move(str(source), str(destination))
            self.logger.info(f"File moved: {source} -> {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
            return False
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Delete file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.warning(f"File not found: {file_path}")
                return True
            
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(str(file_path))
            
            self.logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            return False
    
    def get_unique_filename(self, file_path: Union[str, Path]) -> Path:
        """Get unique filename by adding number suffix if file exists"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return file_path
            
            stem = file_path.stem
            suffix = file_path.suffix
            parent = file_path.parent
            
            counter = 1
            while True:
                new_name = f"{stem} ({counter}){suffix}"
                new_path = parent / new_name
                
                if not new_path.exists():
                    return new_path
                
                counter += 1
                
                # Safety break
                if counter > 1000:
                    break
            
            # Fallback
            import time
            timestamp = int(time.time())
            return parent / f"{stem}_{timestamp}{suffix}"
            
        except Exception as e:
            self.logger.error(f"Error creating unique filename: {e}")
            return file_path
    
    def scan_media_directory(self, directory: Union[str, Path]) -> Dict:
        """Scan directory for media files and return organized results"""
        try:
            directory = Path(directory)
            
            if not directory.exists():
                return {}
            
            results = {
                'video_files': [],
                'audio_files': [],
                'subtitle_files': [],
                'other_files': [],
                'subdirectories': [],
                'total_size': 0,
                'total_files': 0
            }
            
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        file_info = self.get_file_info(item)
                        results['total_files'] += 1
                        results['total_size'] += file_info.get('size', 0)
                        
                        if file_info.get('category') == 'video':
                            results['video_files'].append(file_info)
                        elif file_info.get('category') == 'audio':
                            results['audio_files'].append(file_info)
                        elif file_info.get('category') == 'subtitle':
                            results['subtitle_files'].append(file_info)
                        else:
                            results['other_files'].append(file_info)
                    
                    elif item.is_dir():
                        results['subdirectories'].append({
                            'name': item.name,
                            'path': str(item),
                            'absolute_path': str(item.absolute())
                        })
                
                except Exception as item_error:
                    self.logger.warning(f"Error processing item {item}: {item_error}")
                    continue
            
            # Sort results
            for category in ['video_files', 'audio_files', 'subtitle_files', 'other_files']:
                results[category].sort(key=lambda x: x['name'].lower())
            
            results['subdirectories'].sort(key=lambda x: x['name'].lower())
            
            self.logger.debug(f"Scanned directory {directory}: {results['total_files']} files, {len(results['subdirectories'])} subdirs")
            return results
            
        except Exception as e:
            self.logger.error(f"Error scanning directory: {e}")
            return {}
    
    def export_file_list(self, files: List[Path], output_path: Union[str, Path], format: str = 'json') -> bool:
        """Export file list to various formats"""
        try:
            output_path = Path(output_path)
            self.create_directory(output_path.parent)
            
            file_data = []
            for file_path in files:
                file_info = self.get_file_info(file_path)
                file_data.append(file_info)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(file_data, f, indent=2, ensure_ascii=False, default=str)
            
            elif format.lower() == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    for file_info in file_data:
                        f.write(f"{file_info['absolute_path']}\n")
            
            elif format.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if file_data:
                        writer = csv.DictWriter(f, fieldnames=file_data[0].keys())
                        writer.writeheader()
                        writer.writerows(file_data)
            
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
            
            self.logger.info(f"File list exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting file list: {e}")
            return False
    
    def validate_file_integrity(self, file_path: Union[str, Path]) -> bool:
        """Basic file integrity check"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
            
            # Check if file is readable
            with open(file_path, 'rb') as f:
                # Try to read first and last bytes
                f.read(1)
                if file_path.stat().st_size > 1:
                    f.seek(-1, 2)
                    f.read(1)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"File integrity check failed for {file_path}: {e}")
            return False
    
    def get_directory_size(self, directory: Union[str, Path]) -> int:
        """Get total size of directory"""
        try:
            directory = Path(directory)
            total_size = 0
            
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        continue
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"Error calculating directory size: {e}")
            return 0
    
    def cleanup_temp_files(self, temp_dir: Union[str, Path] = None) -> int:
        """Clean up temporary files"""
        try:
            if temp_dir is None:
                temp_dir = Path.cwd() / "temp"
            else:
                temp_dir = Path(temp_dir)
            
            if not temp_dir.exists():
                return 0
            
            cleaned_count = 0
            for item in temp_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                        cleaned_count += 1
                    elif item.is_dir():
                        shutil.rmtree(str(item))
                        cleaned_count += 1
                except (OSError, PermissionError):
                    continue
            
            self.logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {e}")
            return 0
