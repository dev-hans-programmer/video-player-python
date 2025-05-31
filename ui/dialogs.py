"""
Dialog windows for the video player application
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from ui.styles import COLORS
from utils.logger import Logger

class AboutDialog:
    """About dialog window"""
    
    def __init__(self, parent):
        """Initialize about dialog"""
        self.parent = parent
        self.logger = Logger.get_logger()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Beautiful Video Player")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Configure dialog
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create content
        self._create_content()
    
    def _center_dialog(self):
        """Center dialog relative to parent"""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate dialog position
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_content(self):
        """Create dialog content"""
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Application icon/logo (text-based)
        icon_label = tk.Label(
            main_frame,
            text="🎬",
            bg=COLORS['bg_primary'],
            fg=COLORS['accent'],
            font=('Segoe UI', 48)
        )
        icon_label.pack(pady=10)
        
        # Application name
        name_label = tk.Label(
            main_frame,
            text="Beautiful Video Player",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 16, 'bold')
        )
        name_label.pack()
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 1.0.0",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 10)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_label = tk.Label(
            main_frame,
            text="A modern, responsive video player built with Python and Tkinter.\nFeatures beautiful interface, smooth playback, and modular architecture.",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_primary'],
            font=('Segoe UI', 9),
            justify='center',
            wraplength=350
        )
        desc_label.pack(pady=15)
        
        # Copyright
        copyright_label = tk.Label(
            main_frame,
            text="© 2024 Beautiful Video Player\nBuilt with Python, Tkinter, and OpenCV",
            bg=COLORS['bg_primary'],
            fg=COLORS['fg_secondary'],
            font=('Segoe UI', 8),
            justify='center'
        )
        copyright_label.pack(pady=10)
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        )
        close_btn.pack(pady=10)

class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, settings):
        """Initialize settings dialog"""
        self.parent = parent
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Configure dialog
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create content
        self._create_content()
        
        # Load current settings
        self._load_settings()
    
    def _center_dialog(self):
        """Center dialog relative to parent"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_content(self):
        """Create settings dialog content"""
        # Main frame with scrollbar
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create tabs
        self._create_general_tab()
        self._create_playback_tab()
        self._create_controls_tab()
        self._create_performance_tab()
        self._create_keyboard_tab()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply", command=self._apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_general_tab(self):
        """Create general settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="General")
        
        # Window settings
        window_group = ttk.LabelFrame(frame, text="Window Settings", padding=10)
        window_group.pack(fill=tk.X, padx=10, pady=5)
        
        # Default window size
        ttk.Label(window_group, text="Default Window Size:").grid(row=0, column=0, sticky='w', pady=2)
        self.window_size_var = tk.StringVar()
        size_combo = ttk.Combobox(window_group, textvariable=self.window_size_var, width=15)
        size_combo['values'] = ('800x600', '1024x768', '1200x800', '1920x1080')
        size_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Always on top
        self.always_on_top_var = tk.BooleanVar()
        ttk.Checkbutton(window_group, text="Always on top", variable=self.always_on_top_var).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=2
        )
        
        # Theme settings
        theme_group = ttk.LabelFrame(frame, text="Appearance", padding=10)
        theme_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(theme_group, text="Theme:").grid(row=0, column=0, sticky='w', pady=2)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(theme_group, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ('Dark', 'Light')
        theme_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # File settings
        file_group = ttk.LabelFrame(frame, text="File Management", padding=10)
        file_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(file_group, text="Recent Files Count:").grid(row=0, column=0, sticky='w', pady=2)
        self.recent_count_var = tk.StringVar()
        recent_spin = ttk.Spinbox(file_group, from_=1, to=50, textvariable=self.recent_count_var, width=5)
        recent_spin.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        self.auto_load_subtitles_var = tk.BooleanVar()
        ttk.Checkbutton(file_group, text="Auto-load subtitles", variable=self.auto_load_subtitles_var).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=2
        )
    
    def _create_playback_tab(self):
        """Create playback settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Playback")
        
        # Auto-play settings
        auto_group = ttk.LabelFrame(frame, text="Auto-play", padding=10)
        auto_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_play_var = tk.BooleanVar()
        ttk.Checkbutton(auto_group, text="Auto-play when file is loaded", variable=self.auto_play_var).pack(anchor='w')
        
        self.remember_position_var = tk.BooleanVar()
        ttk.Checkbutton(auto_group, text="Remember playback position", variable=self.remember_position_var).pack(anchor='w')
        
        self.loop_mode_var = tk.BooleanVar()
        ttk.Checkbutton(auto_group, text="Loop mode", variable=self.loop_mode_var).pack(anchor='w')
        
        # Volume settings
        volume_group = ttk.LabelFrame(frame, text="Audio", padding=10)
        volume_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(volume_group, text="Default Volume:").grid(row=0, column=0, sticky='w', pady=2)
        self.default_volume_var = tk.DoubleVar()
        volume_scale = ttk.Scale(volume_group, from_=0, to=100, variable=self.default_volume_var, orient=tk.HORIZONTAL, length=200)
        volume_scale.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        self.volume_label = ttk.Label(volume_group, text="70%")
        self.volume_label.grid(row=0, column=2, sticky='w', padx=(5, 0), pady=2)
        
        volume_scale.configure(command=self._update_volume_label)
        
        self.mute_on_start_var = tk.BooleanVar()
        ttk.Checkbutton(volume_group, text="Mute on start", variable=self.mute_on_start_var).grid(
            row=1, column=0, columnspan=3, sticky='w', pady=2
        )
    
    def _create_controls_tab(self):
        """Create controls settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Controls")
        
        # Control visibility
        visibility_group = ttk.LabelFrame(frame, text="Control Visibility", padding=10)
        visibility_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.show_controls_var = tk.BooleanVar()
        ttk.Checkbutton(visibility_group, text="Show controls", variable=self.show_controls_var).pack(anchor='w')
        
        self.auto_hide_controls_var = tk.BooleanVar()
        ttk.Checkbutton(visibility_group, text="Auto-hide controls in fullscreen", variable=self.auto_hide_controls_var).pack(anchor='w')
        
        ttk.Label(visibility_group, text="Hide delay (ms):").pack(anchor='w', pady=(5, 0))
        self.hide_delay_var = tk.StringVar()
        ttk.Spinbox(visibility_group, from_=1000, to=10000, increment=500, textvariable=self.hide_delay_var, width=10).pack(anchor='w')
        
        # Time display
        time_group = ttk.LabelFrame(frame, text="Time Display", padding=10)
        time_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.show_time_remaining_var = tk.BooleanVar()
        ttk.Checkbutton(time_group, text="Show time remaining instead of elapsed", variable=self.show_time_remaining_var).pack(anchor='w')
        
        ttk.Label(time_group, text="Skip duration (seconds):").pack(anchor='w', pady=(5, 0))
        self.skip_duration_var = tk.StringVar()
        ttk.Spinbox(time_group, from_=1, to=60, textvariable=self.skip_duration_var, width=10).pack(anchor='w')
    
    def _create_performance_tab(self):
        """Create performance settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Performance")
        
        # Hardware acceleration
        hw_group = ttk.LabelFrame(frame, text="Hardware Acceleration", padding=10)
        hw_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.hardware_acceleration_var = tk.BooleanVar()
        ttk.Checkbutton(hw_group, text="Enable hardware acceleration", variable=self.hardware_acceleration_var).pack(anchor='w')
        
        # Buffer settings
        buffer_group = ttk.LabelFrame(frame, text="Buffering", padding=10)
        buffer_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(buffer_group, text="Buffer size (KB):").grid(row=0, column=0, sticky='w', pady=2)
        self.buffer_size_var = tk.StringVar()
        ttk.Spinbox(buffer_group, from_=256, to=4096, increment=256, textvariable=self.buffer_size_var, width=10).grid(
            row=0, column=1, sticky='w', padx=(10, 0), pady=2
        )
        
        # Quality settings
        quality_group = ttk.LabelFrame(frame, text="Quality", padding=10)
        quality_group.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(quality_group, text="FPS limit:").grid(row=0, column=0, sticky='w', pady=2)
        self.fps_limit_var = tk.StringVar()
        fps_combo = ttk.Combobox(quality_group, textvariable=self.fps_limit_var, width=10)
        fps_combo['values'] = ('30', '60', '120', 'Unlimited')
        fps_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        self.quality_auto_adjust_var = tk.BooleanVar()
        ttk.Checkbutton(quality_group, text="Auto-adjust quality based on performance", variable=self.quality_auto_adjust_var).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=2
        )
    
    def _create_keyboard_tab(self):
        """Create keyboard shortcuts tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Keyboard")
        
        # Enable/disable shortcuts
        enable_group = ttk.LabelFrame(frame, text="Enable Shortcuts", padding=10)
        enable_group.pack(fill=tk.X, padx=10, pady=5)
        
        self.space_play_pause_var = tk.BooleanVar()
        ttk.Checkbutton(enable_group, text="Space for Play/Pause", variable=self.space_play_pause_var).pack(anchor='w')
        
        self.arrow_seek_var = tk.BooleanVar()
        ttk.Checkbutton(enable_group, text="Arrow keys for seeking", variable=self.arrow_seek_var).pack(anchor='w')
        
        self.f_fullscreen_var = tk.BooleanVar()
        ttk.Checkbutton(enable_group, text="F for fullscreen", variable=self.f_fullscreen_var).pack(anchor='w')
        
        self.esc_exit_fullscreen_var = tk.BooleanVar()
        ttk.Checkbutton(enable_group, text="Escape to exit fullscreen", variable=self.esc_exit_fullscreen_var).pack(anchor='w')
        
        self.volume_keys_var = tk.BooleanVar()
        ttk.Checkbutton(enable_group, text="Up/Down arrows for volume", variable=self.volume_keys_var).pack(anchor='w')
    
    def _update_volume_label(self, value):
        """Update volume label"""
        self.volume_label.config(text=f"{int(float(value))}%")
    
    def _load_settings(self):
        """Load current settings into dialog"""
        # General settings
        self.window_size_var.set(self.settings.get('window', 'default_size', '1200x800'))
        self.always_on_top_var.set(self.settings.getboolean('window', 'always_on_top', False))
        self.theme_var.set(self.settings.get('window', 'theme', 'dark').title())
        self.recent_count_var.set(str(self.settings.getint('files', 'recent_files_count', 10)))
        self.auto_load_subtitles_var.set(self.settings.getboolean('files', 'auto_load_subtitles', True))
        
        # Playback settings
        self.auto_play_var.set(self.settings.getboolean('player', 'auto_play', True))
        self.remember_position_var.set(self.settings.getboolean('player', 'remember_position', True))
        self.loop_mode_var.set(self.settings.getboolean('player', 'loop_mode', False))
        self.default_volume_var.set(self.settings.getint('player', 'default_volume', 70))
        self.mute_on_start_var.set(self.settings.getboolean('player', 'mute_on_start', False))
        
        # Controls settings
        self.show_controls_var.set(self.settings.getboolean('controls', 'show_controls', True))
        self.auto_hide_controls_var.set(self.settings.getboolean('controls', 'auto_hide_controls', True))
        self.hide_delay_var.set(str(self.settings.getint('controls', 'hide_delay', 3000)))
        self.show_time_remaining_var.set(self.settings.getboolean('controls', 'show_time_remaining', False))
        self.skip_duration_var.set(str(self.settings.getint('controls', 'skip_duration', 10)))
        
        # Performance settings
        self.hardware_acceleration_var.set(self.settings.getboolean('performance', 'hardware_acceleration', True))
        self.buffer_size_var.set(str(self.settings.getint('performance', 'buffer_size', 1024)))
        self.fps_limit_var.set(str(self.settings.getint('performance', 'fps_limit', 60)))
        self.quality_auto_adjust_var.set(self.settings.getboolean('performance', 'quality_auto_adjust', True))
        
        # Keyboard settings
        self.space_play_pause_var.set(self.settings.getboolean('keyboard', 'space_play_pause', True))
        self.arrow_seek_var.set(self.settings.getboolean('keyboard', 'arrow_seek', True))
        self.f_fullscreen_var.set(self.settings.getboolean('keyboard', 'f_fullscreen', True))
        self.esc_exit_fullscreen_var.set(self.settings.getboolean('keyboard', 'esc_exit_fullscreen', True))
        self.volume_keys_var.set(self.settings.getboolean('keyboard', 'volume_keys', True))
        
        # Update volume label
        self._update_volume_label(str(self.default_volume_var.get()))
    
    def _apply_settings(self):
        """Apply settings changes"""
        try:
            # General settings
            self.settings.set('window', 'default_size', self.window_size_var.get())
            self.settings.set('window', 'always_on_top', str(self.always_on_top_var.get()))
            self.settings.set('window', 'theme', self.theme_var.get().lower())
            self.settings.set('files', 'recent_files_count', self.recent_count_var.get())
            self.settings.set('files', 'auto_load_subtitles', str(self.auto_load_subtitles_var.get()))
            
            # Playback settings
            self.settings.set('player', 'auto_play', str(self.auto_play_var.get()))
            self.settings.set('player', 'remember_position', str(self.remember_position_var.get()))
            self.settings.set('player', 'loop_mode', str(self.loop_mode_var.get()))
            self.settings.set('player', 'default_volume', str(int(self.default_volume_var.get())))
            self.settings.set('player', 'mute_on_start', str(self.mute_on_start_var.get()))
            
            # Controls settings
            self.settings.set('controls', 'show_controls', str(self.show_controls_var.get()))
            self.settings.set('controls', 'auto_hide_controls', str(self.auto_hide_controls_var.get()))
            self.settings.set('controls', 'hide_delay', self.hide_delay_var.get())
            self.settings.set('controls', 'show_time_remaining', str(self.show_time_remaining_var.get()))
            self.settings.set('controls', 'skip_duration', self.skip_duration_var.get())
            
            # Performance settings
            self.settings.set('performance', 'hardware_acceleration', str(self.hardware_acceleration_var.get()))
            self.settings.set('performance', 'buffer_size', self.buffer_size_var.get())
            self.settings.set('performance', 'fps_limit', self.fps_limit_var.get())
            self.settings.set('performance', 'quality_auto_adjust', str(self.quality_auto_adjust_var.get()))
            
            # Keyboard settings
            self.settings.set('keyboard', 'space_play_pause', str(self.space_play_pause_var.get()))
            self.settings.set('keyboard', 'arrow_seek', str(self.arrow_seek_var.get()))
            self.settings.set('keyboard', 'f_fullscreen', str(self.f_fullscreen_var.get()))
            self.settings.set('keyboard', 'esc_exit_fullscreen', str(self.esc_exit_fullscreen_var.get()))
            self.settings.set('keyboard', 'volume_keys', str(self.volume_keys_var.get()))
            
            # Save settings
            self.settings.save()
            
            messagebox.showinfo("Settings", "Settings applied successfully!")
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Error", f"Error applying settings: {e}")
    
    def _reset_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings.reset_to_defaults()
            self._load_settings()
            messagebox.showinfo("Settings", "Settings reset to defaults!")
    
    def _ok_clicked(self):
        """Handle OK button click"""
        self._apply_settings()
        self.dialog.destroy()

class PlaylistDialog:
    """Playlist management dialog"""
    
    def __init__(self, parent, playlist_manager):
        """Initialize playlist dialog"""
        self.parent = parent
        self.playlist_manager = playlist_manager
        self.logger = Logger.get_logger()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Playlist")
        self.dialog.geometry("600x400")
        
        # Configure dialog
        self.dialog.configure(bg=COLORS['bg_primary'])
        self.dialog.transient(parent)
        
        # Create content
        self._create_content()
        
        # Load playlist
        self._refresh_playlist()
    
    def _create_content(self):
        """Create playlist dialog content"""
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Playlist listbox with scrollbar
        list_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.playlist_listbox = tk.Listbox(
            list_frame,
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['fg_primary'],
            font=('Segoe UI', 9)
        )
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.playlist_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_listbox.config(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(button_frame, text="Add Files", command=self._add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove", command=self._remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self._clear_playlist).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _refresh_playlist(self):
        """Refresh playlist display"""
        self.playlist_listbox.delete(0, tk.END)
        
        files = self.playlist_manager.get_files()
        current_index = self.playlist_manager.get_current_index()
        
        for i, file_path in enumerate(files):
            filename = file_path.name if hasattr(file_path, 'name') else str(file_path).split('/')[-1]
            
            if i == current_index:
                self.playlist_listbox.insert(tk.END, f"► {filename}")
                self.playlist_listbox.selection_set(i)
            else:
                self.playlist_listbox.insert(tk.END, f"   {filename}")
    
    def _add_files(self):
        """Add files to playlist"""
        # Implementation would use file dialog
        pass
    
    def _remove_selected(self):
        """Remove selected item from playlist"""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            self.playlist_manager.remove_file(index)
            self._refresh_playlist()
    
    def _clear_playlist(self):
        """Clear entire playlist"""
        if messagebox.askyesno("Clear Playlist", "Are you sure you want to clear the entire playlist?"):
            self.playlist_manager.clear()
            self._refresh_playlist()
