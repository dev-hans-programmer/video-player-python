"""
Keyboard shortcut handling for the video player
"""

import tkinter as tk
from typing import Dict, Callable, Optional
from utils.logger import Logger

class KeyboardHandler:
    """Handles keyboard shortcuts and bindings"""
    
    def __init__(self, settings):
        """Initialize keyboard handler"""
        self.settings = settings
        self.logger = Logger.get_logger()
        
        # Key bindings storage
        self.bindings = {}
        self.callbacks = {}
        
        # Modifier key state
        self.modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False
        }
        
        # Key mapping for special keys
        self.key_mapping = {
            'space': ' ',
            'return': '\r',
            'enter': '\r',
            'escape': '\x1b',
            'tab': '\t',
            'backspace': '\x08',
            'delete': '\x7f',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right',
            'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
            'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
            'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12'
        }
        
        self.logger.info("Keyboard handler initialized")
    
    def setup_bindings(self, widget: tk.Widget, callbacks: Dict[str, Callable]):
        """Setup keyboard bindings for a widget"""
        try:
            self.callbacks = callbacks
            
            # Clear existing bindings
            self.clear_bindings(widget)
            
            # Set up individual key bindings based on settings
            self._setup_default_bindings(widget)
            
            # Set up global key event handlers
            widget.bind('<KeyPress>', self._on_key_press)
            widget.bind('<KeyRelease>', self._on_key_release)
            
            # Focus handling
            widget.focus_set()
            
            self.logger.debug("Keyboard bindings setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up keyboard bindings: {e}")
    
    def _setup_default_bindings(self, widget: tk.Widget):
        """Setup default keyboard bindings based on settings"""
        try:
            # Play/Pause - Space
            if self.settings.getboolean('keyboard', 'space_play_pause', True):
                self.add_binding(widget, '<space>', 'play_pause')
            
            # Seek controls - Arrow keys
            if self.settings.getboolean('keyboard', 'arrow_seek', True):
                self.add_binding(widget, '<Left>', 'seek_backward')
                self.add_binding(widget, '<Right>', 'seek_forward')
            
            # Volume controls - Up/Down arrows (if enabled)
            if self.settings.getboolean('keyboard', 'volume_keys', True):
                self.add_binding(widget, '<Up>', 'volume_up')
                self.add_binding(widget, '<Down>', 'volume_down')
            
            # Fullscreen - F key
            if self.settings.getboolean('keyboard', 'f_fullscreen', True):
                self.add_binding(widget, '<f>', 'fullscreen')
                self.add_binding(widget, '<F>', 'fullscreen')
            
            # Exit fullscreen - Escape
            if self.settings.getboolean('keyboard', 'esc_exit_fullscreen', True):
                self.add_binding(widget, '<Escape>', 'fullscreen')
            
            # Media controls
            self.add_binding(widget, '<s>', 'stop')
            self.add_binding(widget, '<S>', 'stop')
            self.add_binding(widget, '<m>', 'mute')
            self.add_binding(widget, '<M>', 'mute')
            self.add_binding(widget, '<n>', 'next')
            self.add_binding(widget, '<N>', 'next')
            self.add_binding(widget, '<p>', 'previous')
            self.add_binding(widget, '<P>', 'previous')
            
            # File operations
            self.add_binding(widget, '<Control-o>', 'open_file')
            self.add_binding(widget, '<Control-O>', 'open_file')
            self.add_binding(widget, '<Control-q>', 'quit')
            self.add_binding(widget, '<Control-Q>', 'quit')
            
            # Additional shortcuts
            self.add_binding(widget, '<F11>', 'fullscreen')
            self.add_binding(widget, '<plus>', 'volume_up')
            self.add_binding(widget, '<minus>', 'volume_down')
            self.add_binding(widget, '<equal>', 'volume_up')  # For + without shift
            
        except Exception as e:
            self.logger.error(f"Error setting up default bindings: {e}")
    
    def add_binding(self, widget: tk.Widget, key_sequence: str, action: str):
        """Add a keyboard binding"""
        try:
            def handler(event):
                return self._handle_key_action(action, event)
            
            widget.bind(key_sequence, handler)
            self.bindings[key_sequence] = action
            
            self.logger.debug(f"Added binding: {key_sequence} -> {action}")
            
        except Exception as e:
            self.logger.error(f"Error adding binding {key_sequence}: {e}")
    
    def remove_binding(self, widget: tk.Widget, key_sequence: str):
        """Remove a keyboard binding"""
        try:
            widget.unbind(key_sequence)
            if key_sequence in self.bindings:
                del self.bindings[key_sequence]
            
            self.logger.debug(f"Removed binding: {key_sequence}")
            
        except Exception as e:
            self.logger.error(f"Error removing binding {key_sequence}: {e}")
    
    def clear_bindings(self, widget: tk.Widget):
        """Clear all keyboard bindings"""
        try:
            for key_sequence in list(self.bindings.keys()):
                self.remove_binding(widget, key_sequence)
            
            self.bindings.clear()
            self.logger.debug("Cleared all bindings")
            
        except Exception as e:
            self.logger.error(f"Error clearing bindings: {e}")
    
    def _handle_key_action(self, action: str, event: tk.Event = None) -> str:
        """Handle keyboard action"""
        try:
            if action in self.callbacks:
                callback = self.callbacks[action]
                if callable(callback):
                    callback()
                    return 'break'  # Prevent further event propagation
            else:
                self.logger.warning(f"No callback registered for action: {action}")
            
        except Exception as e:
            self.logger.error(f"Error handling key action {action}: {e}")
        
        return None
    
    def _on_key_press(self, event: tk.Event):
        """Handle key press events"""
        try:
            # Update modifier state
            if event.keysym in ['Control_L', 'Control_R']:
                self.modifiers['ctrl'] = True
            elif event.keysym in ['Shift_L', 'Shift_R']:
                self.modifiers['shift'] = True
            elif event.keysym in ['Alt_L', 'Alt_R']:
                self.modifiers['alt'] = True
            
            # Log key press for debugging
            self.logger.debug(f"Key pressed: {event.keysym} (char: {repr(event.char)})")
            
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")
    
    def _on_key_release(self, event: tk.Event):
        """Handle key release events"""
        try:
            # Update modifier state
            if event.keysym in ['Control_L', 'Control_R']:
                self.modifiers['ctrl'] = False
            elif event.keysym in ['Shift_L', 'Shift_R']:
                self.modifiers['shift'] = False
            elif event.keysym in ['Alt_L', 'Alt_R']:
                self.modifiers['alt'] = False
            
        except Exception as e:
            self.logger.error(f"Error handling key release: {e}")
    
    def is_modifier_pressed(self, modifier: str) -> bool:
        """Check if a modifier key is currently pressed"""
        return self.modifiers.get(modifier.lower(), False)
    
    def get_key_description(self, key_sequence: str) -> str:
        """Get human-readable description of a key sequence"""
        try:
            # Convert Tkinter key sequence to readable format
            key_desc = key_sequence.strip('<>')
            
            # Handle modifiers
            modifiers = []
            key_parts = key_desc.split('-')
            
            for i, part in enumerate(key_parts[:-1]):
                if part.lower() == 'control':
                    modifiers.append('Ctrl')
                elif part.lower() == 'shift':
                    modifiers.append('Shift')
                elif part.lower() == 'alt':
                    modifiers.append('Alt')
                else:
                    modifiers.append(part.title())
            
            # Get the main key
            main_key = key_parts[-1]
            
            # Convert special keys
            special_keys = {
                'space': 'Space',
                'return': 'Enter',
                'escape': 'Esc',
                'tab': 'Tab',
                'backspace': 'Backspace',
                'delete': 'Delete',
                'up': '↑',
                'down': '↓',
                'left': '←',
                'right': '→',
                'plus': '+',
                'minus': '-',
                'equal': '='
            }
            
            main_key = special_keys.get(main_key.lower(), main_key.upper())
            
            # Combine modifiers and main key
            if modifiers:
                return '+'.join(modifiers) + '+' + main_key
            else:
                return main_key
                
        except Exception as e:
            self.logger.error(f"Error getting key description: {e}")
            return key_sequence
    
    def get_all_bindings(self) -> Dict[str, str]:
        """Get all current key bindings"""
        return self.bindings.copy()
    
    def get_bindings_for_action(self, action: str) -> list:
        """Get all key bindings for a specific action"""
        return [key for key, act in self.bindings.items() if act == action]
    
    def export_bindings(self, file_path: str) -> bool:
        """Export current bindings to a file"""
        try:
            import json
            
            export_data = {
                'bindings': self.bindings,
                'settings': {
                    'space_play_pause': self.settings.getboolean('keyboard', 'space_play_pause', True),
                    'arrow_seek': self.settings.getboolean('keyboard', 'arrow_seek', True),
                    'f_fullscreen': self.settings.getboolean('keyboard', 'f_fullscreen', True),
                    'esc_exit_fullscreen': self.settings.getboolean('keyboard', 'esc_exit_fullscreen', True),
                    'volume_keys': self.settings.getboolean('keyboard', 'volume_keys', True)
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Bindings exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting bindings: {e}")
            return False
    
    def import_bindings(self, file_path: str, widget: tk.Widget) -> bool:
        """Import bindings from a file"""
        try:
            import json
            
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            # Clear current bindings
            self.clear_bindings(widget)
            
            # Import bindings
            bindings = import_data.get('bindings', {})
            for key_sequence, action in bindings.items():
                self.add_binding(widget, key_sequence, action)
            
            # Update settings if provided
            settings = import_data.get('settings', {})
            for setting_key, value in settings.items():
                self.settings.set('keyboard', setting_key, str(value))
            
            self.logger.info(f"Bindings imported from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing bindings: {e}")
            return False
    
    def create_shortcuts_help(self) -> Dict[str, list]:
        """Create organized shortcuts help data"""
        try:
            shortcuts = {
                'Playback': [],
                'Navigation': [],
                'Volume': [],
                'View': [],
                'File': []
            }
            
            # Categorize shortcuts
            action_categories = {
                'play_pause': 'Playback',
                'stop': 'Playback',
                'next': 'Navigation',
                'previous': 'Navigation',
                'seek_forward': 'Navigation',
                'seek_backward': 'Navigation',
                'volume_up': 'Volume',
                'volume_down': 'Volume',
                'mute': 'Volume',
                'fullscreen': 'View',
                'open_file': 'File',
                'quit': 'File'
            }
            
            action_descriptions = {
                'play_pause': 'Play/Pause',
                'stop': 'Stop',
                'next': 'Next Video',
                'previous': 'Previous Video',
                'seek_forward': 'Seek Forward',
                'seek_backward': 'Seek Backward',
                'volume_up': 'Volume Up',
                'volume_down': 'Volume Down',
                'mute': 'Mute/Unmute',
                'fullscreen': 'Toggle Fullscreen',
                'open_file': 'Open File',
                'quit': 'Quit Application'
            }
            
            for key_sequence, action in self.bindings.items():
                category = action_categories.get(action, 'Other')
                description = action_descriptions.get(action, action.replace('_', ' ').title())
                key_desc = self.get_key_description(key_sequence)
                
                if category not in shortcuts:
                    shortcuts[category] = []
                
                shortcuts[category].append({
                    'key': key_desc,
                    'description': description,
                    'action': action
                })
            
            # Sort each category
            for category in shortcuts:
                shortcuts[category].sort(key=lambda x: x['description'])
            
            return shortcuts
            
        except Exception as e:
            self.logger.error(f"Error creating shortcuts help: {e}")
            return {}
    
    def validate_key_sequence(self, key_sequence: str) -> bool:
        """Validate if a key sequence is valid"""
        try:
            # Basic validation for Tkinter key sequences
            if not key_sequence.startswith('<') or not key_sequence.endswith('>'):
                return False
            
            # Check for valid modifiers and key names
            inner = key_sequence[1:-1]
            parts = inner.split('-')
            
            valid_modifiers = {'Control', 'Shift', 'Alt', 'Meta'}
            valid_keys = set(self.key_mapping.values()) | set(self.key_mapping.keys())
            valid_keys.update(['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'])
            valid_keys.update([chr(i) for i in range(ord('a'), ord('z') + 1)])
            valid_keys.update([chr(i) for i in range(ord('A'), ord('Z') + 1)])
            valid_keys.update([str(i) for i in range(10)])
            
            # Check modifiers (all but last part)
            for modifier in parts[:-1]:
                if modifier not in valid_modifiers:
                    return False
            
            # Check main key (last part)
            main_key = parts[-1]
            if main_key not in valid_keys and len(main_key) != 1:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating key sequence: {e}")
            return False
