"""
Modern styling for the video player interface
"""

import tkinter as tk
from tkinter import ttk

# Color scheme
COLORS = {
    'bg_primary': '#2b2b2b',      # Dark background
    'bg_secondary': '#3c3c3c',    # Lighter dark background
    'bg_tertiary': '#4a4a4a',     # Button background
    'fg_primary': '#ffffff',      # Primary text
    'fg_secondary': '#b0b0b0',    # Secondary text
    'accent': '#007acc',          # Accent color (blue)
    'accent_hover': '#1a8cff',    # Accent hover
    'border': '#555555',          # Border color
    'success': '#28a745',         # Success green
    'warning': '#ffc107',         # Warning yellow
    'error': '#dc3545',           # Error red
}

def apply_modern_style(root):
    """Apply modern styling to the application"""
    
    # Configure root window
    root.configure(bg=COLORS['bg_primary'])
    
    # Create and configure custom style
    style = ttk.Style()
    
    # Use 'clam' theme as base
    style.theme_use('clam')
    
    # Configure general styles
    style.configure('.',
        background=COLORS['bg_primary'],
        foreground=COLORS['fg_primary'],
        bordercolor=COLORS['border'],
        focuscolor=COLORS['accent'],
        selectbackground=COLORS['accent'],
        selectforeground=COLORS['fg_primary']
    )
    
    # Frame styles
    style.configure('TFrame',
        background=COLORS['bg_primary'],
        borderwidth=0,
        relief='flat'
    )
    
    style.configure('Controls.TFrame',
        background=COLORS['bg_secondary'],
        borderwidth=1,
        relief='solid'
    )
    
    # Label styles
    style.configure('TLabel',
        background=COLORS['bg_primary'],
        foreground=COLORS['fg_primary'],
        font=('Segoe UI', 9)
    )
    
    style.configure('Time.TLabel',
        background=COLORS['bg_secondary'],
        foreground=COLORS['fg_secondary'],
        font=('Consolas', 9)
    )
    
    style.configure('Title.TLabel',
        background=COLORS['bg_primary'],
        foreground=COLORS['fg_primary'],
        font=('Segoe UI', 12, 'bold')
    )
    
    # Button styles
    style.configure('TButton',
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_primary'],
        borderwidth=1,
        relief='flat',
        padding=(10, 5),
        font=('Segoe UI', 9)
    )
    
    style.map('TButton',
        background=[
            ('active', COLORS['accent']),
            ('pressed', COLORS['accent_hover'])
        ],
        foreground=[
            ('active', COLORS['fg_primary']),
            ('pressed', COLORS['fg_primary'])
        ],
        relief=[
            ('pressed', 'flat'),
            ('!pressed', 'flat')
        ]
    )
    
    # Control button styles (smaller)
    style.configure('Control.TButton',
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_primary'],
        borderwidth=1,
        relief='flat',
        padding=(8, 4),
        font=('Segoe UI', 11)
    )
    
    style.map('Control.TButton',
        background=[
            ('active', COLORS['accent']),
            ('pressed', COLORS['accent_hover']),
            ('disabled', COLORS['bg_secondary'])
        ],
        foreground=[
            ('active', COLORS['fg_primary']),
            ('pressed', COLORS['fg_primary']),
            ('disabled', COLORS['fg_secondary'])
        ]
    )
    
    # Scale (slider) styles
    style.configure('TScale',
        background=COLORS['bg_secondary'],
        troughcolor=COLORS['bg_tertiary'],
        borderwidth=0,
        lightcolor=COLORS['accent'],
        darkcolor=COLORS['accent']
    )
    
    style.configure('Horizontal.TScale',
        background=COLORS['bg_secondary'],
        troughcolor=COLORS['bg_tertiary'],
        borderwidth=0,
        sliderthickness=20,
        gripcount=0
    )
    
    style.map('Horizontal.TScale',
        background=[
            ('active', COLORS['accent']),
            ('!active', COLORS['bg_tertiary'])
        ],
        troughcolor=[
            ('focus', COLORS['bg_tertiary']),
            ('!focus', COLORS['bg_tertiary'])
        ]
    )
    
    # Progress bar styles
    style.configure('TProgressbar',
        background=COLORS['accent'],
        troughcolor=COLORS['bg_tertiary'],
        borderwidth=0,
        lightcolor=COLORS['accent'],
        darkcolor=COLORS['accent']
    )
    
    # Entry styles
    style.configure('TEntry',
        fieldbackground=COLORS['bg_tertiary'],
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_primary'],
        bordercolor=COLORS['border'],
        insertcolor=COLORS['fg_primary'],
        selectbackground=COLORS['accent'],
        selectforeground=COLORS['fg_primary']
    )
    
    style.map('TEntry',
        fieldbackground=[
            ('focus', COLORS['bg_secondary']),
            ('!focus', COLORS['bg_tertiary'])
        ],
        bordercolor=[
            ('focus', COLORS['accent']),
            ('!focus', COLORS['border'])
        ]
    )
    
    # Checkbutton styles
    style.configure('TCheckbutton',
        background=COLORS['bg_primary'],
        foreground=COLORS['fg_primary'],
        focuscolor=COLORS['accent'],
        font=('Segoe UI', 9)
    )
    
    style.map('TCheckbutton',
        background=[
            ('active', COLORS['bg_primary']),
            ('pressed', COLORS['bg_primary'])
        ],
        foreground=[
            ('active', COLORS['accent']),
            ('pressed', COLORS['accent'])
        ]
    )
    
    # Radiobutton styles
    style.configure('TRadiobutton',
        background=COLORS['bg_primary'],
        foreground=COLORS['fg_primary'],
        focuscolor=COLORS['accent'],
        font=('Segoe UI', 9)
    )
    
    style.map('TRadiobutton',
        background=[
            ('active', COLORS['bg_primary']),
            ('pressed', COLORS['bg_primary'])
        ],
        foreground=[
            ('active', COLORS['accent']),
            ('pressed', COLORS['accent'])
        ]
    )
    
    # Combobox styles
    style.configure('TCombobox',
        fieldbackground=COLORS['bg_tertiary'],
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_primary'],
        bordercolor=COLORS['border'],
        selectbackground=COLORS['accent'],
        selectforeground=COLORS['fg_primary'],
        font=('Segoe UI', 9)
    )
    
    style.map('TCombobox',
        fieldbackground=[
            ('focus', COLORS['bg_secondary']),
            ('!focus', COLORS['bg_tertiary'])
        ],
        bordercolor=[
            ('focus', COLORS['accent']),
            ('!focus', COLORS['border'])
        ]
    )
    
    # Notebook (tab) styles
    style.configure('TNotebook',
        background=COLORS['bg_primary'],
        borderwidth=0
    )
    
    style.configure('TNotebook.Tab',
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_secondary'],
        padding=[20, 8],
        font=('Segoe UI', 9)
    )
    
    style.map('TNotebook.Tab',
        background=[
            ('selected', COLORS['bg_primary']),
            ('active', COLORS['bg_secondary']),
            ('!selected', COLORS['bg_tertiary'])
        ],
        foreground=[
            ('selected', COLORS['fg_primary']),
            ('active', COLORS['fg_primary']),
            ('!selected', COLORS['fg_secondary'])
        ]
    )
    
    # Treeview styles
    style.configure('Treeview',
        background=COLORS['bg_secondary'],
        foreground=COLORS['fg_primary'],
        fieldbackground=COLORS['bg_secondary'],
        selectbackground=COLORS['accent'],
        selectforeground=COLORS['fg_primary'],
        font=('Segoe UI', 9)
    )
    
    style.configure('Treeview.Heading',
        background=COLORS['bg_tertiary'],
        foreground=COLORS['fg_primary'],
        font=('Segoe UI', 9, 'bold')
    )
    
    style.map('Treeview.Heading',
        background=[
            ('active', COLORS['accent']),
            ('pressed', COLORS['accent_hover'])
        ]
    )

def create_loading_widget(parent, text="Loading..."):
    """Create a loading widget with spinner"""
    frame = tk.Frame(parent, bg=COLORS['bg_primary'])
    
    # Loading label
    label = tk.Label(
        frame,
        text=text,
        bg=COLORS['bg_primary'],
        fg=COLORS['fg_secondary'],
        font=('Segoe UI', 10)
    )
    label.pack(pady=10)
    
    # Progress bar (indeterminate)
    progress = ttk.Progressbar(
        frame,
        mode='indeterminate',
        length=200
    )
    progress.pack(pady=5)
    progress.start(10)
    
    return frame, progress

def create_error_widget(parent, message, retry_callback=None):
    """Create an error display widget"""
    frame = tk.Frame(parent, bg=COLORS['bg_primary'])
    
    # Error icon (using text)
    icon_label = tk.Label(
        frame,
        text="⚠",
        bg=COLORS['bg_primary'],
        fg=COLORS['error'],
        font=('Segoe UI', 24)
    )
    icon_label.pack(pady=10)
    
    # Error message
    message_label = tk.Label(
        frame,
        text=message,
        bg=COLORS['bg_primary'],
        fg=COLORS['fg_primary'],
        font=('Segoe UI', 10),
        wraplength=300,
        justify='center'
    )
    message_label.pack(pady=5)
    
    # Retry button (if callback provided)
    if retry_callback:
        retry_btn = ttk.Button(
            frame,
            text="Retry",
            command=retry_callback
        )
        retry_btn.pack(pady=10)
    
    return frame

def animate_widget_fade_in(widget, duration=500, steps=20):
    """Animate widget fade in effect"""
    def fade_step(step):
        alpha = step / steps
        try:
            widget.attributes('-alpha', alpha)
            if step < steps:
                widget.after(duration // steps, lambda: fade_step(step + 1))
        except tk.TclError:
            pass  # Widget destroyed
    
    widget.attributes('-alpha', 0)
    fade_step(0)

def animate_widget_slide_in(widget, direction='up', duration=300, distance=50):
    """Animate widget slide in effect"""
    original_y = widget.winfo_y()
    
    if direction == 'up':
        start_y = original_y + distance
    else:
        start_y = original_y - distance
    
    steps = 20
    step_distance = distance / steps
    step_time = duration // steps
    
    def slide_step(step):
        if step <= steps:
            if direction == 'up':
                y = start_y - (step * step_distance)
            else:
                y = start_y + (step * step_distance)
            
            try:
                widget.place(y=y)
                if step < steps:
                    widget.after(step_time, lambda: slide_step(step + 1))
            except tk.TclError:
                pass  # Widget destroyed
    
    widget.place(y=start_y)
    slide_step(0)
