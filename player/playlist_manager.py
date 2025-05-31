"""
Playlist management for the video player
"""

import json
import threading
from pathlib import Path
from typing import List, Optional, Union
from utils.logger import Logger

class PlaylistManager:
    """Manages video playlists and playback order"""
    
    def __init__(self, settings):
        """Initialize playlist manager"""
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Playlist state
        self.files = []
        self.current_index = -1
        self.shuffle_mode = False
        self.repeat_mode = 'none'  # 'none', 'single', 'all'
        
        # Shuffle state
        self.shuffle_history = []
        self.original_order = []
        
        # Threading
        self.playlist_lock = threading.Lock()
        
        # Callbacks
        self.on_playlist_changed = None
        self.on_current_changed = None
        
        self.logger.info("Playlist manager initialized")
    
    def add_file(self, file_path: Union[str, Path]) -> bool:
        """Add a single file to the playlist"""
        try:
            with self.playlist_lock:
                file_path = Path(file_path)
                
                if not file_path.exists():
                    self.logger.error(f"File not found: {file_path}")
                    return False
                
                # Check if file is already in playlist
                if file_path in self.files:
                    self.logger.debug(f"File already in playlist: {file_path}")
                    return True
                
                # Validate file format
                if not self._is_supported_format(file_path):
                    self.logger.warning(f"Unsupported file format: {file_path}")
                    return False
                
                # Add to playlist
                self.files.append(file_path)
                
                # Set as current if first file
                if len(self.files) == 1:
                    self.current_index = 0
                    if self.on_current_changed:
                        self.on_current_changed(self.current_index)
                
                # Update shuffle order if needed
                if self.shuffle_mode:
                    self._update_shuffle_order()
                
                if self.on_playlist_changed:
                    self.on_playlist_changed()
                
                self.logger.debug(f"Added file to playlist: {file_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding file to playlist: {e}")
            return False
    
    def add_files(self, file_paths: List[Union[str, Path]]) -> int:
        """Add multiple files to the playlist"""
        added_count = 0
        
        for file_path in file_paths:
            if self.add_file(file_path):
                added_count += 1
        
        self.logger.info(f"Added {added_count} files to playlist")
        return added_count
    
    def remove_file(self, index: int) -> bool:
        """Remove file at specified index"""
        try:
            with self.playlist_lock:
                if not (0 <= index < len(self.files)):
                    return False
                
                # Remove file
                removed_file = self.files.pop(index)
                
                # Adjust current index
                if index < self.current_index:
                    self.current_index -= 1
                elif index == self.current_index:
                    # Current file was removed
                    if self.current_index >= len(self.files):
                        self.current_index = len(self.files) - 1
                    
                    if self.on_current_changed:
                        self.on_current_changed(self.current_index)
                
                # Update shuffle order
                if self.shuffle_mode:
                    self._update_shuffle_order()
                
                if self.on_playlist_changed:
                    self.on_playlist_changed()
                
                self.logger.debug(f"Removed file from playlist: {removed_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing file from playlist: {e}")
            return False
    
    def remove_file_by_path(self, file_path: Union[str, Path]) -> bool:
        """Remove file by path"""
        try:
            file_path = Path(file_path)
            
            with self.playlist_lock:
                try:
                    index = self.files.index(file_path)
                    return self.remove_file(index)
                except ValueError:
                    self.logger.warning(f"File not found in playlist: {file_path}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error removing file by path: {e}")
            return False
    
    def clear(self):
        """Clear the entire playlist"""
        try:
            with self.playlist_lock:
                self.files.clear()
                self.current_index = -1
                self.shuffle_history.clear()
                self.original_order.clear()
                
                if self.on_playlist_changed:
                    self.on_playlist_changed()
                
                if self.on_current_changed:
                    self.on_current_changed(self.current_index)
                
                self.logger.info("Playlist cleared")
                
        except Exception as e:
            self.logger.error(f"Error clearing playlist: {e}")
    
    def get_current(self) -> Optional[Path]:
        """Get currently selected file"""
        try:
            with self.playlist_lock:
                if 0 <= self.current_index < len(self.files):
                    return self.files[self.current_index]
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting current file: {e}")
            return None
    
    def get_next(self) -> Optional[Path]:
        """Get next file in playlist"""
        try:
            with self.playlist_lock:
                if not self.files:
                    return None
                
                if self.repeat_mode == 'single':
                    return self.get_current()
                
                next_index = self._get_next_index()
                
                if next_index is not None:
                    self.current_index = next_index
                    
                    if self.on_current_changed:
                        self.on_current_changed(self.current_index)
                    
                    return self.files[self.current_index]
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting next file: {e}")
            return None
    
    def get_previous(self) -> Optional[Path]:
        """Get previous file in playlist"""
        try:
            with self.playlist_lock:
                if not self.files:
                    return None
                
                if self.repeat_mode == 'single':
                    return self.get_current()
                
                prev_index = self._get_previous_index()
                
                if prev_index is not None:
                    self.current_index = prev_index
                    
                    if self.on_current_changed:
                        self.on_current_changed(self.current_index)
                    
                    return self.files[self.current_index]
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting previous file: {e}")
            return None
    
    def set_current(self, index: int) -> bool:
        """Set current file by index"""
        try:
            with self.playlist_lock:
                if 0 <= index < len(self.files):
                    self.current_index = index
                    
                    if self.on_current_changed:
                        self.on_current_changed(self.current_index)
                    
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting current file: {e}")
            return False
    
    def set_current_by_path(self, file_path: Union[str, Path]) -> bool:
        """Set current file by path"""
        try:
            file_path = Path(file_path)
            
            with self.playlist_lock:
                try:
                    index = self.files.index(file_path)
                    return self.set_current(index)
                except ValueError:
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error setting current file by path: {e}")
            return False
    
    def has_next(self) -> bool:
        """Check if there's a next file"""
        try:
            with self.playlist_lock:
                if not self.files:
                    return False
                
                if self.repeat_mode in ['single', 'all']:
                    return True
                
                return self._get_next_index() is not None
                
        except Exception as e:
            self.logger.error(f"Error checking for next file: {e}")
            return False
    
    def has_previous(self) -> bool:
        """Check if there's a previous file"""
        try:
            with self.playlist_lock:
                if not self.files:
                    return False
                
                if self.repeat_mode in ['single', 'all']:
                    return True
                
                return self._get_previous_index() is not None
                
        except Exception as e:
            self.logger.error(f"Error checking for previous file: {e}")
            return False
    
    def _get_next_index(self) -> Optional[int]:
        """Get next index based on current mode"""
        if not self.files:
            return None
        
        if self.shuffle_mode:
            return self._get_next_shuffle_index()
        else:
            next_index = self.current_index + 1
            
            if next_index < len(self.files):
                return next_index
            elif self.repeat_mode == 'all':
                return 0
            else:
                return None
    
    def _get_previous_index(self) -> Optional[int]:
        """Get previous index based on current mode"""
        if not self.files:
            return None
        
        if self.shuffle_mode:
            return self._get_previous_shuffle_index()
        else:
            prev_index = self.current_index - 1
            
            if prev_index >= 0:
                return prev_index
            elif self.repeat_mode == 'all':
                return len(self.files) - 1
            else:
                return None
    
    def _get_next_shuffle_index(self) -> Optional[int]:
        """Get next index in shuffle mode"""
        if len(self.shuffle_history) >= len(self.files) and self.repeat_mode != 'all':
            return None
        
        # Get unplayed indices
        unplayed = [i for i in range(len(self.files)) if i not in self.shuffle_history]
        
        if not unplayed:
            if self.repeat_mode == 'all':
                # Reset shuffle history and start over
                self.shuffle_history.clear()
                unplayed = list(range(len(self.files)))
            else:
                return None
        
        # Choose random unplayed index
        import random
        next_index = random.choice(unplayed)
        self.shuffle_history.append(next_index)
        
        return next_index
    
    def _get_previous_shuffle_index(self) -> Optional[int]:
        """Get previous index in shuffle mode"""
        if len(self.shuffle_history) < 2:
            return None
        
        # Remove current from history and return previous
        self.shuffle_history.pop()  # Remove current
        return self.shuffle_history[-1] if self.shuffle_history else None
    
    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode"""
        try:
            with self.playlist_lock:
                self.shuffle_mode = not self.shuffle_mode
                
                if self.shuffle_mode:
                    # Enable shuffle
                    self.original_order = self.files.copy()
                    self.shuffle_history = [self.current_index] if self.current_index >= 0 else []
                else:
                    # Disable shuffle
                    self.shuffle_history.clear()
                    self.original_order.clear()
                
                self.logger.info(f"Shuffle mode {'enabled' if self.shuffle_mode else 'disabled'}")
                return self.shuffle_mode
                
        except Exception as e:
            self.logger.error(f"Error toggling shuffle: {e}")
            return self.shuffle_mode
    
    def set_repeat_mode(self, mode: str) -> bool:
        """Set repeat mode ('none', 'single', 'all')"""
        try:
            if mode not in ['none', 'single', 'all']:
                return False
            
            with self.playlist_lock:
                self.repeat_mode = mode
                self.logger.info(f"Repeat mode set to: {mode}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting repeat mode: {e}")
            return False
    
    def cycle_repeat_mode(self) -> str:
        """Cycle through repeat modes"""
        modes = ['none', 'single', 'all']
        current_index = modes.index(self.repeat_mode)
        next_mode = modes[(current_index + 1) % len(modes)]
        self.set_repeat_mode(next_mode)
        return next_mode
    
    def _update_shuffle_order(self):
        """Update shuffle order when playlist changes"""
        if not self.shuffle_mode:
            return
        
        # Remove indices that are no longer valid
        self.shuffle_history = [i for i in self.shuffle_history if i < len(self.files)]
        
        # Ensure current index is in history
        if self.current_index >= 0 and self.current_index not in self.shuffle_history:
            self.shuffle_history.append(self.current_index)
    
    def _is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        supported_formats = self.settings.get_supported_formats()
        return file_path.suffix.lower().lstrip('.') in supported_formats
    
    def load_folder(self, folder_path: Union[str, Path]) -> int:
        """Load all supported video files from a folder"""
        try:
            folder_path = Path(folder_path)
            
            if not folder_path.exists() or not folder_path.is_dir():
                self.logger.error(f"Folder not found: {folder_path}")
                return 0
            
            # Get all video files
            video_files = []
            supported_formats = self.settings.get_supported_formats()
            
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower().lstrip('.') in supported_formats:
                    video_files.append(file_path)
            
            # Sort files naturally
            video_files.sort(key=lambda x: x.name.lower())
            
            # Clear current playlist and add files
            self.clear()
            added_count = self.add_files(video_files)
            
            self.logger.info(f"Loaded {added_count} files from folder: {folder_path}")
            return added_count
            
        except Exception as e:
            self.logger.error(f"Error loading folder: {e}")
            return 0
    
    def save_playlist(self, file_path: Union[str, Path]) -> bool:
        """Save playlist to file"""
        try:
            file_path = Path(file_path)
            
            playlist_data = {
                'version': '1.0',
                'files': [str(f) for f in self.files],
                'current_index': self.current_index,
                'shuffle_mode': self.shuffle_mode,
                'repeat_mode': self.repeat_mode
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(playlist_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Playlist saved to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving playlist: {e}")
            return False
    
    def load_playlist(self, file_path: Union[str, Path]) -> bool:
        """Load playlist from file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"Playlist file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
            
            # Validate and load files
            files = [Path(f) for f in playlist_data.get('files', [])]
            valid_files = [f for f in files if f.exists()]
            
            with self.playlist_lock:
                self.clear()
                self.files = valid_files
                self.current_index = min(playlist_data.get('current_index', 0), len(self.files) - 1)
                self.shuffle_mode = playlist_data.get('shuffle_mode', False)
                self.repeat_mode = playlist_data.get('repeat_mode', 'none')
                
                if self.on_playlist_changed:
                    self.on_playlist_changed()
                
                if self.on_current_changed:
                    self.on_current_changed(self.current_index)
            
            self.logger.info(f"Playlist loaded from: {file_path} ({len(valid_files)} files)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading playlist: {e}")
            return False
    
    def get_files(self) -> List[Path]:
        """Get list of all files in playlist"""
        with self.playlist_lock:
            return self.files.copy()
    
    def get_current_index(self) -> int:
        """Get current file index"""
        return self.current_index
    
    def get_file_count(self) -> int:
        """Get number of files in playlist"""
        return len(self.files)
    
    def is_empty(self) -> bool:
        """Check if playlist is empty"""
        return len(self.files) == 0
    
    def get_shuffle_mode(self) -> bool:
        """Get shuffle mode state"""
        return self.shuffle_mode
    
    def get_repeat_mode(self) -> str:
        """Get repeat mode"""
        return self.repeat_mode
    
    def get_playlist_info(self) -> dict:
        """Get playlist information"""
        return {
            'file_count': len(self.files),
            'current_index': self.current_index,
            'shuffle_mode': self.shuffle_mode,
            'repeat_mode': self.repeat_mode,
            'current_file': str(self.get_current()) if self.get_current() else None
        }
