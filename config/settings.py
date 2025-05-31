"""
Configuration management for the video player application
"""

import configparser
import os
from pathlib import Path
from utils.logger import Logger

class Settings:
    """Application settings manager"""
    
    def __init__(self, config_file=None):
        """Initialize settings manager"""
        self.logger = Logger.get_logger()
        self.config_file = config_file or Path(__file__).parent / "config.ini"
        self.config = configparser.ConfigParser()
        self._load_defaults()
        self.load()
    
    def _load_defaults(self):
        """Load default configuration values"""
        defaults = {
            'window': {
                'default_size': '1200x800',
                'fullscreen': 'False',
                'always_on_top': 'False',
                'theme': 'dark'
            },
            'player': {
                'auto_play': 'True',
                'remember_position': 'True',
                'loop_mode': 'False',
                'default_volume': '70',
                'mute_on_start': 'False'
            },
            'controls': {
                'show_controls': 'True',
                'auto_hide_controls': 'True',
                'hide_delay': '3000',
                'show_time_remaining': 'False',
                'skip_duration': '10'
            },
            'files': {
                'last_directory': '',
                'recent_files_count': '10',
                'supported_formats': 'mp4,avi,mov,mkv,wmv,flv,webm,m4v',
                'auto_load_subtitles': 'True'
            },
            'performance': {
                'hardware_acceleration': 'True',
                'buffer_size': '1024',
                'fps_limit': '60',
                'quality_auto_adjust': 'True'
            },
            'keyboard': {
                'space_play_pause': 'True',
                'arrow_seek': 'True',
                'f_fullscreen': 'True',
                'esc_exit_fullscreen': 'True',
                'volume_keys': 'True'
            }
        }
        
        for section, options in defaults.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.info("Configuration file not found, using defaults")
                self.save()  # Create default config file
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            self.logger.debug(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get(self, section, option, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getboolean(self, section, option, fallback=False):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getint(self, section, option, fallback=0):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section, option, fallback=0.0):
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section, option, value):
        """Set configuration value"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, option, str(value))
        except Exception as e:
            self.logger.error(f"Error setting configuration value: {e}")
    
    def get_recent_files(self):
        """Get list of recent files"""
        try:
            recent_files = []
            count = self.getint('files', 'recent_files_count', 10)
            
            for i in range(count):
                file_path = self.get('recent_files', f'file_{i}', '')
                if file_path and Path(file_path).exists():
                    recent_files.append(file_path)
            
            return recent_files
            
        except Exception as e:
            self.logger.error(f"Error getting recent files: {e}")
            return []
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        try:
            if not self.config.has_section('recent_files'):
                self.config.add_section('recent_files')
            
            recent_files = self.get_recent_files()
            
            # Remove if already in list
            if file_path in recent_files:
                recent_files.remove(file_path)
            
            # Add to beginning
            recent_files.insert(0, file_path)
            
            # Limit list size
            max_count = self.getint('files', 'recent_files_count', 10)
            recent_files = recent_files[:max_count]
            
            # Save back to config
            for i, file in enumerate(recent_files):
                self.set('recent_files', f'file_{i}', file)
            
            # Clear any remaining entries
            for i in range(len(recent_files), max_count):
                if self.config.has_option('recent_files', f'file_{i}'):
                    self.config.remove_option('recent_files', f'file_{i}')
            
        except Exception as e:
            self.logger.error(f"Error adding recent file: {e}")
    
    def get_supported_formats(self):
        """Get list of supported video formats"""
        formats_str = self.get('files', 'supported_formats', 'mp4,avi,mov,mkv,wmv,flv,webm,m4v')
        return [fmt.strip().lower() for fmt in formats_str.split(',')]
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        try:
            self.config.clear()
            self._load_defaults()
            self.save()
            self.logger.info("Configuration reset to defaults")
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
