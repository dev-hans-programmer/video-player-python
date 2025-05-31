"""
Icon assets and graphics for the video player UI
Using SVG and Unicode symbols for cross-platform compatibility
"""

from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk
import base64
from io import BytesIO

class Icons:
    """Icon manager for the video player"""
    
    # Unicode symbols for basic controls
    SYMBOLS = {
        'play': '▶',
        'pause': '⏸',
        'stop': '⏹',
        'previous': '⏮',
        'next': '⏭',
        'rewind': '⏪',
        'fast_forward': '⏩',
        'volume_high': '🔊',
        'volume_medium': '🔉',
        'volume_low': '🔈',
        'volume_mute': '🔇',
        'fullscreen': '⛶',
        'exit_fullscreen': '⤧',
        'folder': '📁',
        'file': '📄',
        'video': '🎬',
        'audio': '🎵',
        'subtitle': '💬',
        'settings': '⚙',
        'playlist': '📋',
        'shuffle': '🔀',
        'repeat': '🔁',
        'repeat_one': '🔂',
        'search': '🔍',
        'download': '⬇',
        'upload': '⬆',
        'close': '✕',
        'minimize': '🗕',
        'maximize': '🗖',
        'restore': '🗗',
        'info': 'ℹ',
        'warning': '⚠',
        'error': '❌',
        'success': '✓',
        'loading': '⟳',
        'bookmark': '🔖',
        'star': '⭐',
        'heart': '♥',
        'thumbs_up': '👍',
        'thumbs_down': '👎'
    }
    
    # Simple SVG icons (as strings for embedding)
    SVG_ICONS = {
        'play': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
        </svg>''',
        
        'pause': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
        </svg>''',
        
        'stop': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 6h12v12H6z"/>
        </svg>''',
        
        'volume_up': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
        </svg>''',
        
        'volume_off': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
        </svg>''',
        
        'fullscreen': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
        </svg>''',
        
        'exit_fullscreen': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
        </svg>''',
        
        'folder': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
        </svg>''',
        
        'settings': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
        </svg>''',
        
        'playlist': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15,6H3V8H15V6M15,10H3V12H15V10M3,16H11V14H3V16M17,6V14.18C16.69,14.07 16.35,14 16,14A3,3 0 0,0 13,17A3,3 0 0,0 16,20A3,3 0 0,0 19,17V8H22V6H17Z"/>
        </svg>''',
        
        'close': '''<svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>'''
    }
    
    def __init__(self):
        """Initialize icon manager"""
        self._icon_cache = {}
        self._font_cache = {}
    
    @staticmethod
    def get_symbol(name: str, default: str = '?') -> str:
        """Get Unicode symbol for icon"""
        return Icons.SYMBOLS.get(name, default)
    
    @staticmethod
    def get_svg(name: str) -> Optional[str]:
        """Get SVG icon as string"""
        return Icons.SVG_ICONS.get(name)
    
    def create_icon_font(self, size: int = 12, family: str = 'Segoe UI Emoji') -> tuple:
        """Create font configuration for icon symbols"""
        font_key = (family, size)
        
        if font_key not in self._font_cache:
            self._font_cache[font_key] = (family, size)
        
        return self._font_cache[font_key]
    
    def create_button_with_icon(self, parent, icon_name: str, text: str = '', command=None, 
                               size: int = 16, style: str = None) -> ttk.Button:
        """Create button with icon"""
        symbol = self.get_symbol(icon_name)
        
        if text:
            button_text = f"{symbol} {text}"
        else:
            button_text = symbol
        
        btn = ttk.Button(
            parent,
            text=button_text,
            command=command,
            style=style
        )
        
        # Configure font for icon
        icon_font = self.create_icon_font(size)
        btn.configure(font=icon_font)
        
        return btn
    
    def create_label_with_icon(self, parent, icon_name: str, text: str = '', 
                              size: int = 16, **kwargs) -> tk.Label:
        """Create label with icon"""
        symbol = self.get_symbol(icon_name)
        
        if text:
            label_text = f"{symbol} {text}"
        else:
            label_text = symbol
        
        # Set default styling
        default_kwargs = {
            'font': self.create_icon_font(size),
            'compound': tk.LEFT,
            'anchor': tk.W
        }
        default_kwargs.update(kwargs)
        
        return tk.Label(parent, text=label_text, **default_kwargs)
    
    def update_button_icon(self, button: ttk.Button, icon_name: str, text: str = ''):
        """Update button icon"""
        symbol = self.get_symbol(icon_name)
        
        if text:
            button_text = f"{symbol} {text}"
        else:
            button_text = symbol
        
        button.configure(text=button_text)
    
    def get_playback_icon(self, state: str) -> str:
        """Get appropriate playback icon based on state"""
        icon_map = {
            'playing': 'pause',
            'paused': 'play',
            'stopped': 'play',
            'loading': 'loading'
        }
        return self.get_symbol(icon_map.get(state, 'play'))
    
    def get_volume_icon(self, volume: float, muted: bool = False) -> str:
        """Get appropriate volume icon based on level"""
        if muted or volume == 0:
            return self.get_symbol('volume_mute')
        elif volume < 33:
            return self.get_symbol('volume_low')
        elif volume < 66:
            return self.get_symbol('volume_medium')
        else:
            return self.get_symbol('volume_high')
    
    def get_repeat_icon(self, mode: str) -> str:
        """Get appropriate repeat icon based on mode"""
        icon_map = {
            'none': '',
            'single': 'repeat_one',
            'all': 'repeat'
        }
        return self.get_symbol(icon_map.get(mode, ''))
    
    def create_animated_icon(self, parent, icon_name: str, duration: int = 1000) -> tk.Label:
        """Create animated rotating icon (for loading, etc.)"""
        label = self.create_label_with_icon(parent, icon_name)
        
        def animate():
            # Simple animation by changing the icon periodically
            current_text = label.cget('text')
            if current_text:
                # For now, just flash the icon
                label.configure(fg='gray')
                parent.after(duration // 2, lambda: label.configure(fg='white'))
            
            parent.after(duration, animate)
        
        animate()
        return label
    
    def create_status_icon(self, status: str) -> str:
        """Get status icon symbol"""
        status_map = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info',
            'loading': 'loading'
        }
        return self.get_symbol(status_map.get(status, 'info'))
    
    def export_svg_icon(self, name: str, file_path: str, size: int = 24, color: str = '#000000') -> bool:
        """Export SVG icon to file"""
        try:
            svg_content = self.get_svg(name)
            if not svg_content:
                return False
            
            # Create complete SVG file
            full_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}">
    {svg_content}
</svg>'''
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_svg)
            
            return True
            
        except Exception:
            return False
    
    def create_icon_grid(self, parent, columns: int = 8) -> tk.Frame:
        """Create a grid showing all available icons"""
        frame = tk.Frame(parent)
        
        row = 0
        col = 0
        
        for name, symbol in self.SYMBOLS.items():
            icon_frame = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
            icon_frame.grid(row=row, column=col, padx=2, pady=2)
            
            # Icon
            icon_label = tk.Label(icon_frame, text=symbol, font=('Segoe UI Emoji', 16))
            icon_label.pack()
            
            # Name
            name_label = tk.Label(icon_frame, text=name, font=('Arial', 8))
            name_label.pack()
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        return frame
    
    @staticmethod
    def create_custom_icon(symbol: str, size: int = 16, color: str = 'white', 
                          bg_color: str = 'transparent') -> dict:
        """Create custom icon configuration"""
        return {
            'symbol': symbol,
            'font': ('Segoe UI Emoji', size),
            'fg': color,
            'bg': bg_color
        }
    
    def get_file_type_icon(self, file_extension: str) -> str:
        """Get icon for file type"""
        ext = file_extension.lower().lstrip('.')
        
        video_exts = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
        audio_exts = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'}
        subtitle_exts = {'srt', 'vtt', 'ass', 'ssa', 'sub'}
        
        if ext in video_exts:
            return self.get_symbol('video')
        elif ext in audio_exts:
            return self.get_symbol('audio')
        elif ext in subtitle_exts:
            return self.get_symbol('subtitle')
        else:
            return self.get_symbol('file')
    
    def create_toolbar_button(self, parent, icon_name: str, tooltip: str = '', 
                             command=None, size: int = 20) -> tk.Button:
        """Create toolbar-style button with icon"""
        symbol = self.get_symbol(icon_name)
        
        btn = tk.Button(
            parent,
            text=symbol,
            font=self.create_icon_font(size),
            relief=tk.FLAT,
            borderwidth=0,
            command=command,
            cursor='hand2'
        )
        
        # Add hover effects
        def on_enter(event):
            btn.configure(relief=tk.RAISED, borderwidth=1)
        
        def on_leave(event):
            btn.configure(relief=tk.FLAT, borderwidth=0)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        # Add tooltip if provided
        if tooltip:
            self.create_tooltip(btn, tooltip)
        
        return btn
    
    def create_tooltip(self, widget, text: str):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background='lightyellow',
                relief=tk.SOLID,
                borderwidth=1,
                font=('Arial', 9)
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

# Global icon instance
icons = Icons()

# Convenience functions
def get_icon(name: str, default: str = '?') -> str:
    """Get icon symbol"""
    return icons.get_symbol(name, default)

def create_icon_button(parent, icon_name: str, text: str = '', **kwargs) -> ttk.Button:
    """Create button with icon"""
    return icons.create_button_with_icon(parent, icon_name, text, **kwargs)

def create_icon_label(parent, icon_name: str, text: str = '', **kwargs) -> tk.Label:
    """Create label with icon"""
    return icons.create_label_with_icon(parent, icon_name, text, **kwargs)
