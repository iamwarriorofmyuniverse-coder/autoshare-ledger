"""
Custom UI Theme and Component Engine for Tkinter
Provides styled cards, metric widgets, buttons, and segmented tabs.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFilter, ImageTk

# Theme Color Palette
BG_COLOR = "#0b0f19"           # Main window background
SURFACE_CARD = "#141c2e"       # Card surface background
SURFACE_INNER = "#0d1322"      # Inset surface
BORDER_COLOR = "#232f48"       # Card border outline
TEXT_PRIMARY = "#f8fafc"       # Primary text
TEXT_SECONDARY = "#94a3b8"     # Secondary text
TEXT_MUTED = "#64748b"         # Muted text

# Accent Color Definitions
ACCENT_BLUE = "#38bdf8"        # Blue accent
ACCENT_INDIGO = "#6366f1"      # Indigo accent
ACCENT_EMERALD = "#10b981"     # Emerald accent
ACCENT_ROSE = "#f43f5e"        # Rose accent
ACCENT_AMBER = "#fbbf24"       # Amber accent
ACCENT_PURPLE = "#a855f7"      # Purple accent

PALETTE = {
    "blue": {
        "bg_hex": "#13233c",
        "bg_rgb": (19, 35, 60),
        "border": "#2563eb",
        "accent": "#38bdf8",
        "fg": "#e0f2fe",
        "glow": (56, 189, 248, 60)
    },
    "emerald": {
        "bg_hex": "#112a28",
        "bg_rgb": (17, 42, 40),
        "border": "#059669",
        "accent": "#34d399",
        "fg": "#d1fae5",
        "glow": (52, 211, 153, 60)
    },
    "rose": {
        "bg_hex": "#2e1520",
        "bg_rgb": (46, 21, 32),
        "border": "#e11d48",
        "accent": "#fb7185",
        "fg": "#ffe4e6",
        "glow": (251, 113, 133, 60)
    },
    "amber": {
        "bg_hex": "#2b2112",
        "bg_rgb": (43, 33, 18),
        "border": "#d97706",
        "accent": "#fbbf24",
        "fg": "#fef3c7",
        "glow": (251, 191, 36, 60)
    },
    "indigo": {
        "bg_hex": "#1e1b38",
        "bg_rgb": (30, 27, 56),
        "border": "#6366f1",
        "accent": "#818cf8",
        "fg": "#e0e7ff",
        "glow": (129, 140, 248, 60)
    },
    "default": {
        "bg_hex": "#182235",
        "bg_rgb": (24, 34, 53),
        "border": "#334155",
        "accent": "#94a3b8",
        "fg": "#f8fafc",
        "glow": (148, 163, 184, 40)
    }
}

_IMAGE_CACHE = {}

def get_glow_card_image(width, height, radius=14, theme="default", state="normal", offset=4, blur=8):
    """
    Renders a glowing dark glass card with ambient neon rim and soft shadow.
    """
    t_data = PALETTE.get(theme, PALETTE["default"])
    bg_rgb = t_data["bg_rgb"]
    border_hex = t_data["border"]
    glow_rgba = t_data["glow"]

    cache_key = (width, height, radius, theme, state, offset, blur)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    pad = offset + blur + 4
    canvas_w = max(width + pad * 2, 1)
    canvas_h = max(height + pad * 2, 1)

    scale = 2
    sw, sh, spad, sr, soff, sblur = canvas_w * scale, canvas_h * scale, pad * scale, radius * scale, offset * scale, blur * scale
    rw, rh = width * scale, height * scale

    img = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))

    # Ambient Colored Glow Layer
    glow_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow_layer)
    g_box = [spad, spad + soff // 2, spad + rw, spad + rh + soff // 2]
    g_draw.rounded_rectangle(g_box, radius=sr, fill=glow_rgba)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(sblur))
    img = Image.alpha_composite(img, glow_layer)

    # Main Card Body
    main_layer = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    m_draw = ImageDraw.Draw(main_layer)
    m_box = [spad, spad, spad + rw, spad + rh]
    m_draw.rounded_rectangle(m_box, radius=sr, fill=(*bg_rgb, 245))

    # High-Tech Colored Border
    br_r, br_g, br_b = int(border_hex[1:3], 16), int(border_hex[3:5], 16), int(border_hex[5:7], 16)
    m_draw.rounded_rectangle(m_box, radius=sr, outline=(br_r, br_g, br_b, 180), width=scale)

    # Subtle top highlight gloss
    m_draw.rounded_rectangle([spad + 2, spad + 2, spad + rw - 2, spad + (rh // 3)],
                             radius=max(0, sr - 2), fill=(255, 255, 255, 12))

    img = Image.alpha_composite(img, main_layer)

    img = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    _IMAGE_CACHE[cache_key] = (photo, pad)
    return photo, pad

class ModernButton(tk.Canvas):
    """
    Modern Glowing Push Button with vivid gradients and tactile active states.
    """
    def __init__(self, parent, text="", command=None, width=130, height=38, radius=10,
                 theme="default", font=('Segoe UI', 10, 'bold'), cursor="hand2", **kwargs):
        self.btn_w = width
        self.btn_h = height
        self.radius = radius
        self.text = text
        self.command = command
        self.font = font
        self.theme_name = theme

        t_data = PALETTE.get(theme, PALETTE["default"])
        self.fg_color = t_data["fg"]
        self.accent = t_data["accent"]

        self.pad = 6
        canvas_w = self.btn_w + self.pad * 2
        canvas_h = self.btn_h + self.pad * 2

        super().__init__(parent, width=canvas_w, height=canvas_h, bg=BG_COLOR,
                         highlightthickness=0, bd=0, cursor=cursor, **kwargs)

        self.state = 'normal'
        self.render()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def render(self):
        self.delete("all")
        photo, pad = get_glow_card_image(self.btn_w, self.btn_h, radius=self.radius,
                                          theme=self.theme_name, state=self.state, offset=2, blur=4)
        self._bg_photo = photo
        self.create_image(pad + self.btn_w // 2, pad + self.btn_h // 2, image=photo)

        y_off = 1 if self.state == 'pressed' else 0
        self.create_text(pad + self.btn_w // 2, pad + self.btn_h // 2 + y_off,
                         text=self.text, fill=self.fg_color, font=self.font)

    def _on_enter(self, event):
        self.state = 'hover'
        self.render()

    def _on_leave(self, event):
        self.state = 'normal'
        self.render()

    def _on_press(self, event):
        self.state = 'pressed'
        self.render()

    def _on_release(self, event):
        self.state = 'normal'
        self.render()
        if self.command:
            self.command()

class ModernStatCard(tk.Canvas):
    """
    High-Tech Glowing Metric / KPI Card with vivid icons and neon accents.
    """
    def __init__(self, parent, title="", value="0", icon="📊", theme="blue", width=225, height=96, **kwargs):
        self.card_w = width
        self.card_h = height
        self.title = title
        self.value = value
        self.icon = icon
        self.theme_name = theme

        t_data = PALETTE.get(theme, PALETTE["default"])
        self.accent_color = t_data["accent"]
        self.fg_color = t_data["fg"]

        self.pad = 8
        canvas_w = self.card_w + self.pad * 2
        canvas_h = self.card_h + self.pad * 2

        super().__init__(parent, width=canvas_w, height=canvas_h, bg=BG_COLOR,
                         highlightthickness=0, bd=0, **kwargs)
        self.render()

    def render(self):
        self.delete("all")
        photo, pad = get_glow_card_image(self.card_w, self.card_h, radius=14,
                                          theme=self.theme_name, state='normal', offset=3, blur=6)
        self._bg_photo = photo
        self.create_image(pad + self.card_w // 2, pad + self.card_h // 2, image=photo)

        # Left Glowing Icon Disc
        ax = pad + 16
        ay = pad + 14
        self.create_oval(ax, ay, ax + 28, ay + 28, fill=self.accent_color, outline="")
        self.create_text(ax + 14, ay + 14, text=self.icon, font=('Segoe UI Emoji', 12))

        # Title
        self.create_text(ax + 38, ay + 14, text=self.title, font=('Segoe UI', 9, 'bold'),
                         fill=self.fg_color, anchor="w")

        # Value
        self.create_text(pad + 18, pad + 62, text=self.value, font=('Segoe UI', 18, 'bold'),
                         fill=TEXT_PRIMARY, anchor="w")

    def update_value(self, new_val):
        self.value = str(new_val)
        self.render()

class ModernSegmentedTab(tk.Canvas):
    """
    Futuristic Glow Segmented Tab Bar.
    """
    def __init__(self, parent, tabs, on_select=None, width=760, height=44, **kwargs):
        self.tabs = tabs
        self.on_select = on_select
        self.tab_w = width
        self.tab_h = height
        self.selected_idx = 0
        self.pad = 6

        canvas_w = self.tab_w + self.pad * 2
        canvas_h = self.tab_h + self.pad * 2

        super().__init__(parent, width=canvas_w, height=canvas_h, bg=BG_COLOR,
                         highlightthickness=0, bd=0, cursor="hand2", **kwargs)

        self.bind("<Button-1>", self._on_click)
        self.render()

    def render(self):
        self.delete("all")
        num_tabs = len(self.tabs)
        segment_w = (self.tab_w - 6) // num_tabs

        # Outer Dark Glass Track
        track_photo, pad = get_glow_card_image(self.tab_w, self.tab_h, radius=12, theme="default", offset=2, blur=3)
        self._track_photo = track_photo
        self.create_image(pad + self.tab_w // 2, pad + self.tab_h // 2, image=track_photo)

        # Active Glowing Pill
        pill_x = pad + 3 + self.selected_idx * segment_w
        pill_y = pad + 3
        pill_w = segment_w
        pill_h = self.tab_h - 6

        pill_photo, p_pad = get_glow_card_image(pill_w, pill_h, radius=10, theme="indigo", offset=2, blur=3)
        self._pill_photo = pill_photo
        self.create_image(pill_x + pill_w // 2, pill_y + pill_h // 2, image=pill_photo)

        # Tab Text
        for idx, tab_name in enumerate(self.tabs):
            tx = pad + 3 + idx * segment_w + segment_w // 2
            ty = pad + self.tab_h // 2
            is_active = (idx == self.selected_idx)
            f_col = "#ffffff" if is_active else TEXT_SECONDARY
            f_weight = 'bold' if is_active else 'normal'
            self.create_text(tx, ty, text=tab_name, fill=f_col, font=('Segoe UI', 10, f_weight))

    def _on_click(self, event):
        pad = self.pad
        num_tabs = len(self.tabs)
        segment_w = (self.tab_w - 6) // num_tabs
        rel_x = event.x - pad - 3
        if 0 <= rel_x <= (self.tab_w - 6):
            idx = int(rel_x // segment_w)
            if 0 <= idx < num_tabs and idx != self.selected_idx:
                self.selected_idx = idx
                self.render()
                if self.on_select:
                    self.on_select(idx)
