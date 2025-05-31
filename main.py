#!/usr/bin/env python3
"""
Beautiful Video Player - Main Application Entry Point
A modern, responsive video player built with Python and Tkinter
"""

import tkinter as tk
import sys
import os
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from ui.main_window import MainWindow
from utils.logger import Logger
from utils.helpers import setup_exception_handler

class VideoPlayerApp:
    """Main application class for the video player"""
    
    def __init__(self):
        """Initialize the video player application"""
        self.logger = Logger.get_logger()
        self.settings = Settings()
        self.root = None
        self.main_window = None
        
    def initialize(self):
        """Initialize the application components"""
        try:
            # Setup global exception handler
            setup_exception_handler()
            
            # Create main Tkinter root
            self.root = tk.Tk()
            
            # Configure root window
            self.root.title("Beautiful Video Player")
            self.root.geometry(self.settings.get('window', 'default_size', '1200x800'))
            self.root.minsize(800, 600)
            
            # Set application icon (if available)
            try:
                icon_path = project_root / "assets" / "icon.ico"
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except Exception as e:
                self.logger.debug(f"Could not set application icon: {e}")
            
            # Apply modern styling
            self.root.configure(bg='#2b2b2b')
            
            # Create main window
            self.main_window = MainWindow(self.root, self.settings)
            
            # Setup window protocols
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Center window on screen
            self._center_window()
            
            self.logger.info("Video player application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def _center_window(self):
        """Center the main window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        """Start the application main loop"""
        if not self.initialize():
            self.logger.error("Failed to initialize application")
            return 1
        
        try:
            self.logger.info("Starting video player application")
            self.root.mainloop()
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return 0
            
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            return 1
    
    def on_closing(self):
        """Handle application closing"""
        try:
            if self.main_window:
                self.main_window.cleanup()
            
            # Save window geometry
            if self.root:
                geometry = self.root.geometry()
                self.settings.set('window', 'default_size', geometry)
                self.settings.save()
            
            self.logger.info("Application closing gracefully")
            
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {e}")
        
        finally:
            if self.root:
                self.root.quit()
                self.root.destroy()

def main():
    """Main function to start the video player application"""
    app = VideoPlayerApp()
    exit_code = app.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
