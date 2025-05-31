"""
Main window for the video player application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

from ui.controls import PlayerControls
from ui.styles import apply_modern_style
from ui.dialogs import AboutDialog, SettingsDialog
from player.video_player import VideoPlayer
from player.playlist_manager import PlaylistManager
from utils.keyboard_handler import KeyboardHandler
from utils.logger import Logger
from utils.file_manager import FileManager

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, settings):
        """Initialize the main window"""
        self.root = root
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Initialize components
        self.video_player = None
        self.playlist_manager = PlaylistManager(settings)
        self.keyboard_handler = KeyboardHandler(settings)
        self.file_manager = FileManager(settings)
        
        # Window state
        self.is_fullscreen = False
        self.normal_geometry = None
        self.controls_visible = True
        self.auto_hide_timer = None
        
        # Setup UI
        self._create_menu()
        self._create_main_frame()
        self._create_video_frame()
        self._create_controls()
        self._setup_bindings()
        
        # Apply modern styling
        apply_modern_style(self.root)
        
        self.logger.info("Main window initialized")
    
    def _create_menu(self):
        """Create the application menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder...", command=self.open_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._update_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Fullscreen", command=self.toggle_fullscreen, accelerator="F")
        view_menu.add_command(label="Always on Top", command=self.toggle_always_on_top)
        view_menu.add_separator()
        view_menu.add_command(label="Show/Hide Controls", command=self.toggle_controls, accelerator="C")
        
        # Playback menu
        playback_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Playback", menu=playback_menu)
        playback_menu.add_command(label="Play/Pause", command=self.toggle_playback, accelerator="Space")
        playback_menu.add_command(label="Stop", command=self.stop_playback, accelerator="S")
        playback_menu.add_separator()
        playback_menu.add_command(label="Previous", command=self.previous_video, accelerator="P")
        playback_menu.add_command(label="Next", command=self.next_video, accelerator="N")
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Settings", command=self.show_settings)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def _create_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def _create_video_frame(self):
        """Create the video display frame"""
        self.video_frame = tk.Frame(self.main_frame, bg='black')
        self.video_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        
        # Video canvas
        self.video_canvas = tk.Canvas(
            self.video_frame,
            bg='black',
            highlightthickness=0
        )
        self.video_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text
        self.placeholder_text = self.video_canvas.create_text(
            0, 0,
            text="Drop a video file here or use File > Open File",
            fill='white',
            font=('Arial', 16),
            anchor='center'
        )
        
        # Initialize video player
        self.video_player = VideoPlayer(self.video_canvas, self.settings)
        
        # Bind canvas events
        self.video_canvas.bind('<Configure>', self._on_canvas_configure)
        self.video_canvas.bind('<Button-1>', self._on_canvas_click)
        self.video_canvas.bind('<Double-Button-1>', self.toggle_fullscreen)
        
        # Drag and drop support
        self._setup_drag_drop()
    
    def _create_controls(self):
        """Create the player controls"""
        self.controls = PlayerControls(
            self.main_frame,
            self.video_player,
            self.playlist_manager,
            self.settings
        )
        self.controls.frame.grid(row=1, column=0, sticky='ew', padx=2, pady=2)
        
        # Bind control events
        self.controls.on_file_open = self.open_file
        self.controls.on_fullscreen = self.toggle_fullscreen
    
    def _setup_bindings(self):
        """Setup keyboard and window bindings"""
        # Keyboard bindings
        self.keyboard_handler.setup_bindings(self.root, {
            'play_pause': self.toggle_playback,
            'stop': self.stop_playback,
            'fullscreen': self.toggle_fullscreen,
            'volume_up': self.volume_up,
            'volume_down': self.volume_down,
            'mute': self.toggle_mute,
            'seek_forward': self.seek_forward,
            'seek_backward': self.seek_backward,
            'next': self.next_video,
            'previous': self.previous_video,
            'open_file': self.open_file,
            'quit': self.root.quit
        })
        
        # Window events
        self.root.bind('<Configure>', self._on_window_configure)
        self.root.bind('<Motion>', self._on_mouse_motion)
        
        # Focus events
        self.root.bind('<FocusIn>', self._on_focus_in)
        self.root.bind('<FocusOut>', self._on_focus_out)
    
    def _setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            # Enable drag and drop
            self.video_canvas.drop_target_register('DND_Files')
            self.video_canvas.dnd_bind('<<Drop>>', self._on_file_drop)
        except Exception as e:
            self.logger.debug(f"Drag and drop not available: {e}")
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update placeholder text position
        canvas_width = event.width
        canvas_height = event.height
        self.video_canvas.coords(
            self.placeholder_text,
            canvas_width // 2,
            canvas_height // 2
        )
        
        # Update video player
        if self.video_player:
            self.video_player.resize(canvas_width, canvas_height)
    
    def _on_canvas_click(self, event):
        """Handle canvas click"""
        # Toggle play/pause on single click
        if self.video_player and self.video_player.is_loaded():
            self.toggle_playback()
    
    def _on_window_configure(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            if not self.is_fullscreen:
                # Save normal geometry
                self.normal_geometry = self.root.geometry()
    
    def _on_mouse_motion(self, event):
        """Handle mouse movement for auto-hiding controls"""
        if self.settings.getboolean('controls', 'auto_hide_controls'):
            self.show_controls()
            self._schedule_hide_controls()
    
    def _on_focus_in(self, event):
        """Handle window focus in"""
        if self.video_player:
            self.video_player.resume_if_playing()
    
    def _on_focus_out(self, event):
        """Handle window focus out"""
        # Optionally pause when losing focus
        pass
    
    def _on_file_drop(self, event):
        """Handle file drop"""
        try:
            files = event.data.split()
            if files:
                self.load_video(files[0])
        except Exception as e:
            self.logger.error(f"Error handling file drop: {e}")
    
    def _update_recent_files_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, 'end')
        
        recent_files = self.settings.get_recent_files()
        if not recent_files:
            self.recent_menu.add_command(label="(No recent files)", state='disabled')
            return
        
        for file_path in recent_files:
            filename = Path(file_path).name
            self.recent_menu.add_command(
                label=filename,
                command=lambda f=file_path: self.load_video(f)
            )
        
        self.recent_menu.add_separator()
        self.recent_menu.add_command(label="Clear Recent Files", command=self._clear_recent_files)
    
    def _clear_recent_files(self):
        """Clear recent files list"""
        if messagebox.askyesno("Clear Recent Files", "Are you sure you want to clear the recent files list?"):
            # Clear from config
            if self.settings.config.has_section('recent_files'):
                self.settings.config.remove_section('recent_files')
                self.settings.save()
            self._update_recent_files_menu()
    
    def _schedule_hide_controls(self):
        """Schedule hiding controls after delay"""
        if self.auto_hide_timer:
            self.root.after_cancel(self.auto_hide_timer)
        
        delay = self.settings.getint('controls', 'hide_delay', 3000)
        self.auto_hide_timer = self.root.after(delay, self.hide_controls)
    
    # Public methods for video control
    def open_file(self):
        """Open file dialog to select video"""
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
            ("MP4 files", "*.mp4"),
            ("AVI files", "*.avi"),
            ("MOV files", "*.mov"),
            ("All files", "*.*")
        ]
        
        initial_dir = self.settings.get('files', 'last_directory', '')
        
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=file_types,
            initialdir=initial_dir
        )
        
        if filename:
            self.load_video(filename)
    
    def open_folder(self):
        """Open folder dialog to load playlist"""
        initial_dir = self.settings.get('files', 'last_directory', '')
        
        folder = filedialog.askdirectory(
            title="Select Folder with Videos",
            initialdir=initial_dir
        )
        
        if folder:
            self.load_folder(folder)
    
    def load_video(self, file_path):
        """Load and play video file"""
        try:
            if not Path(file_path).exists():
                messagebox.showerror("Error", f"File not found: {file_path}")
                return
            
            # Hide placeholder text
            self.video_canvas.itemconfig(self.placeholder_text, state='hidden')
            
            # Load video
            if self.video_player.load_video(file_path):
                # Update window title
                filename = Path(file_path).name
                self.root.title(f"Beautiful Video Player - {filename}")
                
                # Add to recent files
                self.settings.add_recent_file(file_path)
                self._update_recent_files_menu()
                
                # Save last directory
                self.settings.set('files', 'last_directory', str(Path(file_path).parent))
                
                # Auto-play if enabled
                if self.settings.getboolean('player', 'auto_play'):
                    self.video_player.play()
                
                self.logger.info(f"Video loaded: {file_path}")
            else:
                messagebox.showerror("Error", "Failed to load video file")
                
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            messagebox.showerror("Error", f"Error loading video: {e}")
    
    def load_folder(self, folder_path):
        """Load all videos from folder into playlist"""
        try:
            video_files = self.file_manager.get_video_files(folder_path)
            
            if not video_files:
                messagebox.showwarning("Warning", "No video files found in the selected folder")
                return
            
            # Load into playlist
            self.playlist_manager.load_folder(folder_path)
            
            # Load first video
            if video_files:
                self.load_video(video_files[0])
            
            self.logger.info(f"Folder loaded: {folder_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading folder: {e}")
            messagebox.showerror("Error", f"Error loading folder: {e}")
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.video_player and self.video_player.is_loaded():
            if self.video_player.is_playing():
                self.video_player.pause()
            else:
                self.video_player.play()
    
    def stop_playback(self):
        """Stop video playback"""
        if self.video_player:
            self.video_player.stop()
    
    def next_video(self):
        """Play next video in playlist"""
        next_file = self.playlist_manager.get_next()
        if next_file:
            self.load_video(next_file)
    
    def previous_video(self):
        """Play previous video in playlist"""
        prev_file = self.playlist_manager.get_previous()
        if prev_file:
            self.load_video(prev_file)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.normal_geometry = self.root.geometry()
            self.root.attributes('-fullscreen', True)
            self.hide_controls()
        else:
            self.root.attributes('-fullscreen', False)
            if self.normal_geometry:
                self.root.geometry(self.normal_geometry)
            self.show_controls()
    
    def toggle_always_on_top(self):
        """Toggle always on top"""
        current = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current)
    
    def toggle_controls(self):
        """Toggle controls visibility"""
        if self.controls_visible:
            self.hide_controls()
        else:
            self.show_controls()
    
    def show_controls(self):
        """Show player controls"""
        if not self.controls_visible:
            self.controls.frame.grid()
            self.controls_visible = True
    
    def hide_controls(self):
        """Hide player controls"""
        if self.controls_visible and self.is_fullscreen:
            self.controls.frame.grid_remove()
            self.controls_visible = False
    
    def volume_up(self):
        """Increase volume"""
        if self.video_player:
            self.video_player.volume_up()
    
    def volume_down(self):
        """Decrease volume"""
        if self.video_player:
            self.video_player.volume_down()
    
    def toggle_mute(self):
        """Toggle mute"""
        if self.video_player:
            self.video_player.toggle_mute()
    
    def seek_forward(self):
        """Seek forward"""
        if self.video_player:
            self.video_player.seek_relative(10)
    
    def seek_backward(self):
        """Seek backward"""
        if self.video_player:
            self.video_player.seek_relative(-10)
    
    def show_about(self):
        """Show about dialog"""
        AboutDialog(self.root)
    
    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self.root, self.settings)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts = [
            ("Space", "Play/Pause"),
            ("F", "Toggle Fullscreen"),
            ("C", "Show/Hide Controls"),
            ("S", "Stop"),
            ("M", "Mute/Unmute"),
            ("↑/↓", "Volume Up/Down"),
            ("←/→", "Seek Backward/Forward"),
            ("N", "Next Video"),
            ("P", "Previous Video"),
            ("Ctrl+O", "Open File"),
            ("Ctrl+Q", "Quit")
        ]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        for i, (key, action) in enumerate(shortcuts):
            ttk.Label(frame, text=key, font=('Courier', 10, 'bold')).grid(
                row=i, column=0, sticky='w', padx=(0, 20), pady=2
            )
            ttk.Label(frame, text=action).grid(
                row=i, column=1, sticky='w', pady=2
            )
        
        ttk.Button(frame, text="Close", command=dialog.destroy).grid(
            row=len(shortcuts), column=0, columnspan=2, pady=20
        )
    
    def cleanup(self):
        """Cleanup resources before closing"""
        try:
            if self.video_player:
                self.video_player.cleanup()
            
            if self.auto_hide_timer:
                self.root.after_cancel(self.auto_hide_timer)
            
            self.logger.info("Main window cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
