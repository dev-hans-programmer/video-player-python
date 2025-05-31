"""
Player controls interface for the video player
"""

import tkinter as tk
from tkinter import ttk
import threading
from assets.icons import Icons
from utils.logger import Logger

class PlayerControls:
    """Player controls widget"""
    
    def __init__(self, parent, video_player, playlist_manager, settings):
        """Initialize player controls"""
        self.parent = parent
        self.video_player = video_player
        self.playlist_manager = playlist_manager
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Control state
        self.is_seeking = False
        self.update_timer = None
        
        # Callbacks
        self.on_file_open = None
        self.on_fullscreen = None
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self._create_controls()
        self._start_update_timer()
    
    def _create_controls(self):
        """Create control widgets"""
        # Main control frame
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left controls (playback)
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Playback buttons
        self._create_playback_buttons(left_frame)
        
        # Center controls (time and seek)
        center_frame = ttk.Frame(control_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Time and seek bar
        self._create_time_controls(center_frame)
        
        # Right controls (volume and options)
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Volume and utility buttons
        self._create_volume_controls(right_frame)
        self._create_utility_buttons(right_frame)
    
    def _create_playback_buttons(self, parent):
        """Create playback control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(side=tk.LEFT)
        
        # Previous button
        self.prev_btn = ttk.Button(
            button_frame,
            text="⏮",
            width=3,
            command=self._on_previous
        )
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        # Play/Pause button
        self.play_btn = ttk.Button(
            button_frame,
            text="▶",
            width=3,
            command=self._on_play_pause
        )
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹",
            width=3,
            command=self._on_stop
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Next button
        self.next_btn = ttk.Button(
            button_frame,
            text="⏭",
            width=3,
            command=self._on_next
        )
        self.next_btn.pack(side=tk.LEFT, padx=2)
    
    def _create_time_controls(self, parent):
        """Create time display and seek bar"""
        # Time frame
        time_frame = ttk.Frame(parent)
        time_frame.pack(fill=tk.X, pady=2)
        
        # Current time label
        self.current_time_label = ttk.Label(time_frame, text="00:00")
        self.current_time_label.pack(side=tk.LEFT)
        
        # Seek bar frame
        seek_frame = ttk.Frame(time_frame)
        seek_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Seek bar
        self.seek_var = tk.DoubleVar()
        self.seek_bar = ttk.Scale(
            seek_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.seek_var,
            command=self._on_seek
        )
        self.seek_bar.pack(fill=tk.X)
        
        # Bind seek events
        self.seek_bar.bind('<Button-1>', self._on_seek_start)
        self.seek_bar.bind('<ButtonRelease-1>', self._on_seek_end)
        
        # Duration label
        self.duration_label = ttk.Label(time_frame, text="00:00")
        self.duration_label.pack(side=tk.RIGHT)
    
    def _create_volume_controls(self, parent):
        """Create volume control widgets"""
        volume_frame = ttk.Frame(parent)
        volume_frame.pack(side=tk.LEFT, padx=10)
        
        # Mute button
        self.mute_btn = ttk.Button(
            volume_frame,
            text="🔊",
            width=3,
            command=self._on_mute
        )
        self.mute_btn.pack(side=tk.LEFT, padx=2)
        
        # Volume slider
        self.volume_var = tk.DoubleVar()
        self.volume_var.set(self.settings.getint('player', 'default_volume', 70))
        
        self.volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=80,
            variable=self.volume_var,
            command=self._on_volume_change
        )
        self.volume_scale.pack(side=tk.LEFT, padx=5)
        
        # Volume percentage label
        self.volume_label = ttk.Label(volume_frame, text="70%", width=4)
        self.volume_label.pack(side=tk.LEFT, padx=2)
    
    def _create_utility_buttons(self, parent):
        """Create utility buttons"""
        utility_frame = ttk.Frame(parent)
        utility_frame.pack(side=tk.LEFT, padx=10)
        
        # Open file button
        self.open_btn = ttk.Button(
            utility_frame,
            text="📁",
            width=3,
            command=self._on_open_file
        )
        self.open_btn.pack(side=tk.LEFT, padx=2)
        
        # Playlist toggle button
        self.playlist_btn = ttk.Button(
            utility_frame,
            text="📋",
            width=3,
            command=self._on_playlist_toggle
        )
        self.playlist_btn.pack(side=tk.LEFT, padx=2)
        
        # Fullscreen button
        self.fullscreen_btn = ttk.Button(
            utility_frame,
            text="⛶",
            width=3,
            command=self._on_fullscreen
        )
        self.fullscreen_btn.pack(side=tk.LEFT, padx=2)
    
    def _start_update_timer(self):
        """Start the control update timer"""
        self._update_controls()
    
    def _update_controls(self):
        """Update control states and displays"""
        try:
            if self.video_player and self.video_player.is_loaded():
                # Update play/pause button
                if self.video_player.is_playing():
                    self.play_btn.config(text="⏸")
                else:
                    self.play_btn.config(text="▶")
                
                # Update time displays and seek bar
                if not self.is_seeking:
                    current_time = self.video_player.get_current_time()
                    duration = self.video_player.get_duration()
                    
                    if duration > 0:
                        progress = (current_time / duration) * 100
                        self.seek_var.set(progress)
                    
                    self.current_time_label.config(text=self._format_time(current_time))
                    self.duration_label.config(text=self._format_time(duration))
                
                # Update volume display
                volume = self.video_player.get_volume()
                if not self.volume_scale.get() == volume:
                    self.volume_var.set(volume)
                self.volume_label.config(text=f"{int(volume)}%")
                
                # Update mute button
                if self.video_player.is_muted():
                    self.mute_btn.config(text="🔇")
                else:
                    self.mute_btn.config(text="🔊")
                
                # Enable controls
                self._enable_controls()
            else:
                # Disable controls when no video
                self._disable_controls()
                self._reset_displays()
            
            # Update playlist buttons
            self._update_playlist_buttons()
            
        except Exception as e:
            self.logger.error(f"Error updating controls: {e}")
        
        finally:
            # Schedule next update
            self.update_timer = self.frame.after(100, self._update_controls)
    
    def _enable_controls(self):
        """Enable all control buttons"""
        controls = [
            self.play_btn, self.stop_btn, self.seek_bar,
            self.volume_scale, self.mute_btn
        ]
        for control in controls:
            control.config(state='normal')
    
    def _disable_controls(self):
        """Disable control buttons when no video"""
        controls = [
            self.play_btn, self.stop_btn, self.seek_bar,
            self.volume_scale, self.mute_btn
        ]
        for control in controls:
            control.config(state='disabled')
    
    def _reset_displays(self):
        """Reset time displays"""
        self.current_time_label.config(text="00:00")
        self.duration_label.config(text="00:00")
        self.seek_var.set(0)
        self.play_btn.config(text="▶")
    
    def _update_playlist_buttons(self):
        """Update playlist navigation buttons"""
        has_previous = self.playlist_manager.has_previous()
        has_next = self.playlist_manager.has_next()
        
        self.prev_btn.config(state='normal' if has_previous else 'disabled')
        self.next_btn.config(state='normal' if has_next else 'disabled')
    
    def _format_time(self, seconds):
        """Format time in MM:SS or HH:MM:SS format"""
        if seconds < 0:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    # Event handlers
    def _on_play_pause(self):
        """Handle play/pause button click"""
        if self.video_player and self.video_player.is_loaded():
            if self.video_player.is_playing():
                self.video_player.pause()
            else:
                self.video_player.play()
    
    def _on_stop(self):
        """Handle stop button click"""
        if self.video_player:
            self.video_player.stop()
    
    def _on_previous(self):
        """Handle previous button click"""
        prev_file = self.playlist_manager.get_previous()
        if prev_file and self.on_file_open:
            # Use callback to load previous video
            threading.Thread(
                target=lambda: self.on_file_open(prev_file),
                daemon=True
            ).start()
    
    def _on_next(self):
        """Handle next button click"""
        next_file = self.playlist_manager.get_next()
        if next_file and self.on_file_open:
            # Use callback to load next video
            threading.Thread(
                target=lambda: self.on_file_open(next_file),
                daemon=True
            ).start()
    
    def _on_seek_start(self, event):
        """Handle seek start"""
        self.is_seeking = True
    
    def _on_seek_end(self, event):
        """Handle seek end"""
        self.is_seeking = False
        if self.video_player and self.video_player.is_loaded():
            duration = self.video_player.get_duration()
            if duration > 0:
                position = (self.seek_var.get() / 100) * duration
                self.video_player.seek_to(position)
    
    def _on_seek(self, value):
        """Handle seek bar change"""
        if self.is_seeking and self.video_player and self.video_player.is_loaded():
            duration = self.video_player.get_duration()
            if duration > 0:
                position = (float(value) / 100) * duration
                self.current_time_label.config(text=self._format_time(position))
    
    def _on_volume_change(self, value):
        """Handle volume change"""
        volume = float(value)
        if self.video_player:
            self.video_player.set_volume(volume)
        self.volume_label.config(text=f"{int(volume)}%")
    
    def _on_mute(self):
        """Handle mute button click"""
        if self.video_player:
            self.video_player.toggle_mute()
    
    def _on_open_file(self):
        """Handle open file button click"""
        if self.on_file_open:
            self.on_file_open()
    
    def _on_playlist_toggle(self):
        """Handle playlist toggle button click"""
        # TODO: Implement playlist panel toggle
        pass
    
    def _on_fullscreen(self):
        """Handle fullscreen button click"""
        if self.on_fullscreen:
            self.on_fullscreen()
    
    def cleanup(self):
        """Cleanup control resources"""
        try:
            if self.update_timer:
                self.frame.after_cancel(self.update_timer)
        except Exception as e:
            self.logger.error(f"Error during controls cleanup: {e}")
