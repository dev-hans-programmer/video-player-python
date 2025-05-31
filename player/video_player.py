"""
Core video player functionality using OpenCV
"""

import cv2
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path

from utils.logger import Logger

class VideoPlayer:
    """Main video player class using OpenCV"""
    
    def __init__(self, canvas, settings):
        """Initialize video player"""
        self.canvas = canvas
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Video state
        self.video_cap = None
        self.current_frame = None
        self.video_loaded = False
        self.is_playing_state = False
        self.is_paused = False
        self.current_position = 0
        self.total_frames = 0
        self.fps = 0
        self.duration = 0
        self.frame_width = 0
        self.frame_height = 0
        
        # Audio state (simplified - OpenCV doesn't handle audio well)
        self.volume = self.settings.getint('player', 'default_volume', 70)
        self.muted = False
        self.previous_volume = self.volume
        
        # Threading
        self.playback_thread = None
        self.playback_lock = threading.Lock()
        self.stop_playback = threading.Event()
        
        # Display state
        self.canvas_width = 0
        self.canvas_height = 0
        self.display_image = None
        
        # Callbacks
        self.on_position_changed = None
        self.on_state_changed = None
        self.on_error = None
        
        self.logger.info("Video player initialized")
    
    def load_video(self, file_path):
        """Load video file"""
        try:
            # Stop current playback
            self.stop()
            
            # Validate file
            if not Path(file_path).exists():
                self.logger.error(f"Video file not found: {file_path}")
                return False
            
            # Open video capture
            self.video_cap = cv2.VideoCapture(str(file_path))
            
            if not self.video_cap.isOpened():
                self.logger.error(f"Failed to open video file: {file_path}")
                return False
            
            # Get video properties
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if self.fps > 0:
                self.duration = self.total_frames / self.fps
            else:
                self.duration = 0
            
            # Reset state
            self.current_position = 0
            self.is_loaded = True
            self.is_playing_state = False
            self.is_paused = False
            
            # Load first frame
            self._load_frame(0)
            
            self.logger.info(f"Video loaded: {file_path} ({self.frame_width}x{self.frame_height}, {self.fps:.2f} fps, {self.duration:.2f}s)")
            
            if self.on_state_changed:
                self.on_state_changed('loaded')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            if self.on_error:
                self.on_error(f"Error loading video: {e}")
            return False
    
    def play(self):
        """Start video playback"""
        if not self.is_loaded:
            return False
        
        try:
            with self.playback_lock:
                if self.is_playing_state:
                    return True
                
                self.is_playing_state = True
                self.is_paused = False
                self.stop_playback.clear()
                
                # Start playback thread
                self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
                self.playback_thread.start()
                
                if self.on_state_changed:
                    self.on_state_changed('playing')
                
                self.logger.debug("Video playback started")
                return True
                
        except Exception as e:
            self.logger.error(f"Error starting playback: {e}")
            return False
    
    def pause(self):
        """Pause video playback"""
        try:
            with self.playback_lock:
                if not self.is_playing_state:
                    return
                
                self.is_playing_state = False
                self.is_paused = True
                self.stop_playback.set()
                
                if self.on_state_changed:
                    self.on_state_changed('paused')
                
                self.logger.debug("Video playback paused")
                
        except Exception as e:
            self.logger.error(f"Error pausing playback: {e}")
    
    def stop(self):
        """Stop video playback"""
        try:
            with self.playback_lock:
                self.is_playing_state = False
                self.is_paused = False
                self.stop_playback.set()
                
                # Wait for playback thread to finish
                if self.playback_thread and self.playback_thread.is_alive():
                    self.playback_thread.join(timeout=1.0)
                
                # Reset to beginning
                if self.is_loaded:
                    self.seek_to(0)
                
                if self.on_state_changed:
                    self.on_state_changed('stopped')
                
                self.logger.debug("Video playback stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping playback: {e}")
    
    def seek_to(self, position):
        """Seek to specific position in seconds"""
        if not self.is_loaded or not self.cap:
            return False
        
        try:
            # Clamp position
            position = max(0, min(position, self.duration))
            
            # Calculate frame number
            frame_number = int(position * self.fps)
            frame_number = max(0, min(frame_number, self.total_frames - 1))
            
            # Seek to frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_position = frame_number / self.fps if self.fps > 0 else 0
            
            # Load the frame
            self._load_current_frame()
            
            if self.on_position_changed:
                self.on_position_changed(self.current_position)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error seeking to position {position}: {e}")
            return False
    
    def seek_relative(self, offset):
        """Seek relative to current position"""
        new_position = self.current_position + offset
        return self.seek_to(new_position)
    
    def _playback_loop(self):
        """Main playback loop (runs in separate thread)"""
        target_frame_time = 1.0 / self.fps if self.fps > 0 else 1.0 / 30.0
        
        while not self.stop_playback.is_set() and self.is_loaded:
            try:
                frame_start_time = time.time()
                
                # Read next frame
                ret, frame = self.cap.read()
                
                if not ret:
                    # End of video
                    self.logger.debug("End of video reached")
                    
                    # Check for loop mode
                    if self.settings.getboolean('player', 'loop_mode', False):
                        self.seek_to(0)
                        continue
                    else:
                        # Stop playback
                        with self.playback_lock:
                            self.is_playing_state = False
                            if self.on_state_changed:
                                self.on_state_changed('finished')
                        break
                
                # Update current position
                current_frame_number = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.current_position = current_frame_number / self.fps if self.fps > 0 else 0
                
                # Display frame
                self._display_frame(frame)
                
                # Notify position change
                if self.on_position_changed:
                    self.on_position_changed(self.current_position)
                
                # Frame timing
                frame_end_time = time.time()
                frame_process_time = frame_end_time - frame_start_time
                sleep_time = max(0, target_frame_time - frame_process_time)
                
                if sleep_time > 0:
                    self.stop_playback.wait(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in playback loop: {e}")
                break
        
        self.logger.debug("Playback loop ended")
    
    def _load_frame(self, frame_number):
        """Load specific frame"""
        if not self.cap:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            
            if ret:
                self._display_frame(frame)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading frame {frame_number}: {e}")
            return False
    
    def _load_current_frame(self):
        """Load and display current frame"""
        if not self.cap:
            return False
        
        try:
            ret, frame = self.cap.read()
            
            if ret:
                self._display_frame(frame)
                # Go back one frame since we just read it
                current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos - 1)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading current frame: {e}")
            return False
    
    def _display_frame(self, frame):
        """Display frame on canvas"""
        try:
            if frame is None:
                return
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get canvas dimensions
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calculate display size maintaining aspect ratio
            frame_aspect = self.frame_width / self.frame_height
            canvas_aspect = canvas_width / canvas_height
            
            if frame_aspect > canvas_aspect:
                # Video is wider than canvas
                display_width = canvas_width
                display_height = int(canvas_width / frame_aspect)
            else:
                # Video is taller than canvas
                display_height = canvas_height
                display_width = int(canvas_height * frame_aspect)
            
            # Resize frame
            resized_frame = cv2.resize(frame_rgb, (display_width, display_height), interpolation=cv2.INTER_LINEAR)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(resized_frame)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update canvas on main thread
            self.canvas.after(0, self._update_canvas, photo, display_width, display_height, canvas_width, canvas_height)
            
        except Exception as e:
            self.logger.error(f"Error displaying frame: {e}")
    
    def _update_canvas(self, photo, display_width, display_height, canvas_width, canvas_height):
        """Update canvas with new image (called on main thread)"""
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Calculate position to center image
            x = (canvas_width - display_width) // 2
            y = (canvas_height - display_height) // 2
            
            # Display image
            self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # Keep reference to prevent garbage collection
            self.display_image = photo
            
        except Exception as e:
            self.logger.error(f"Error updating canvas: {e}")
    
    def resize(self, width, height):
        """Handle canvas resize"""
        self.canvas_width = width
        self.canvas_height = height
        
        # Redraw current frame if paused
        if self.is_loaded and not self.is_playing_state:
            self._load_current_frame()
    
    # Audio control methods (simplified since OpenCV doesn't handle audio well)
    def set_volume(self, volume):
        """Set volume (0-100)"""
        self.volume = max(0, min(100, volume))
        if not self.is_muted:
            # In a real implementation, this would control system audio
            pass
    
    def get_volume(self):
        """Get current volume"""
        return self.volume if not self.is_muted else 0
    
    def volume_up(self, step=5):
        """Increase volume"""
        self.set_volume(self.volume + step)
    
    def volume_down(self, step=5):
        """Decrease volume"""
        self.set_volume(self.volume - step)
    
    def toggle_mute(self):
        """Toggle mute state"""
        if self.is_muted:
            self.is_muted = False
            self.volume = self.previous_volume
        else:
            self.is_muted = True
            self.previous_volume = self.volume
            self.volume = 0
    
    def is_muted(self):
        """Check if muted"""
        return self.muted
    
    # State query methods
    def is_loaded(self):
        """Check if video is loaded"""
        return self.video_loaded
    
    def is_playing(self):
        """Check if video is playing"""
        return self.is_playing_state
    
    def get_current_time(self):
        """Get current playback time in seconds"""
        return self.current_position
    
    def get_duration(self):
        """Get video duration in seconds"""
        return self.duration
    
    def get_position_percentage(self):
        """Get current position as percentage"""
        if self.duration > 0:
            return (self.current_position / self.duration) * 100
        return 0
    
    def get_video_info(self):
        """Get video information"""
        if not self.is_loaded:
            return None
        
        return {
            'width': self.frame_width,
            'height': self.frame_height,
            'fps': self.fps,
            'duration': self.duration,
            'total_frames': self.total_frames,
            'current_frame': int(self.current_position * self.fps) if self.fps > 0 else 0
        }
    
    def resume_if_playing(self):
        """Resume playback if it was playing before"""
        if self.is_paused:
            self.play()
    
    def cleanup(self):
        """Cleanup video player resources"""
        try:
            self.stop()
            
            if self.cap:
                self.cap.release()
                self.cap = None
            
            self.is_loaded = False
            self.current_frame = None
            self.display_image = None
            
            self.logger.info("Video player cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during video player cleanup: {e}")
