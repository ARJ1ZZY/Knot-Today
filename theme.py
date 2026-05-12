# theme.py - Retro 8-Bit Color Scheme
COLORS = {
    # Retro 8-bit palette
    "bg_primary": (28, 28, 32),        # Charcoal black #1C1C20
    "bg_secondary": (20, 20, 24),      # Darker charcoal #141418
    "bg_tertiary": (40, 40, 44),       # Light charcoal #28282C
    
    # Text colors
    "text_primary": (240, 240, 240),   # Almost white #F0F0F0
    "text_secondary": (180, 180, 180), # Gray #B4B4B4
    "text_muted": (100, 100, 110),     # Muted gray #64646E
    
    # Accent colors
    "accent_primary": (200, 40, 40),   # Deep red #C82828
    "accent_secondary": (180, 30, 30), # Darker red #B41E1E
    "accent_hover": (220, 60, 60),     # Bright red on hover #DC3C3C
    "accent_disabled": (80, 30, 30),   # Dim red #501E1E
    
    # Status colors (8-bit style)
    "success": (80, 200, 80),          # Pixel green #50C850
    "error": (220, 50, 50),            # Pixel red #DC3232
    "warning": (220, 180, 50),         # Pixel yellow #DCB432
    
    # UI element colors
    "border_light": (80, 80, 90),      # #50505A
    "border_dark": (15, 15, 20),       # #0F0F14
    "surface_dark": (25, 25, 32),      # #191920
    "surface_light": (50, 50, 60),     # #32323C
    
    # Keyboard specific
    "key_normal": (35, 35, 42),        # #23232A
    "key_hover": (55, 55, 65),         # #373741
    "key_pressed": (25, 25, 32),       # #191920
    "key_disabled": (20, 20, 28),      # #14141C
    "key_text": (220, 220, 220),       # #DCDCDC
    "key_text_disabled": (80, 80, 90), # #50505A
    
    # Shadow and overlay
    "shadow": (0, 0, 0, 180),
    "overlay": (0, 0, 0, 220),
    "pixel_outline": (0, 0, 0, 255)
}

ANIMATION = {
    "button_hover_scale": 1.02,
    "button_press_scale": 0.98,
    "popup_duration": 45,
    "shake_intensity": 3,
    "float_speed": 0.01,
    "particle_count": 6
}