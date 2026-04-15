# utils.py
import json
import random
import math
import pygame
from pathlib import Path

_image_cache = {}
_text_cache = {}

def load_image(path, use_alpha=True):
    """Load image with proper conversion and caching - CRITICAL for performance"""
    if path in _image_cache:
        return _image_cache[path]
    
    try:
        if use_alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        _image_cache[path] = img
        return img
    except:
        return None

def scale_image_cached(img, width, height):
    """Scale image and cache the result"""
    cache_key = f"scaled_{id(img)}_{width}_{height}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    scaled = pygame.transform.smoothscale(img, (width, height))
    _image_cache[cache_key] = scaled
    return scaled

def clear_image_cache():
    _image_cache.clear()
    _text_cache.clear()

def get_cached_text(font, text, color, antialias=True):
    """Cache rendered text surfaces to avoid re-rendering every frame"""
    cache_key = (id(font), text, color, antialias)
    if cache_key not in _text_cache:
        _text_cache[cache_key] = font.render(text, antialias, color)
    return _text_cache[cache_key]

def load_word_bank(filepath="data/words.json"):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Word bank missing: {filepath}")
    with open(path, 'r') as f:
        return json.load(f)

def get_random_word(category=None):
    bank = load_word_bank()
    if category and category in bank:
        words = bank[category]
        return random.choice(words).upper()
    all_categories = list(bank.keys())
    chosen_category = random.choice(all_categories)
    return random.choice(bank[chosen_category]).upper(), chosen_category

def get_categories():
    bank = load_word_bank()
    return list(bank.keys())

def calculate_points(word, is_correct, streak=0):
    if not is_correct:
        return 0
    if len(word) < 5:
        base = 10
    else:
        base = 25
    return base * (1 + streak)

def load_high_score(filepath="data/highscore.json"):
    path = Path(filepath)
    if path.exists():
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get("high_score", 0)
    return 0

def save_high_score(score, filepath="data/highscore.json"):
    path = Path(filepath)
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump({"high_score": score}, f)

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def draw_glass_rect(surface, rect, color, radius, border_width=1, border_color=None, shadow=True):
    if shadow:
        shadow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), (5, 5, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surf, (rect.x - 5, rect.y - 5))
    
    glass_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glass_surf, color, (0, 0, rect.width, rect.height), border_radius=radius)
    
    if border_width > 0:
        if border_color is None:
            border_color = (255, 255, 255, 40)
        pygame.draw.rect(glass_surf, border_color, (0, 0, rect.width, rect.height), border_width, border_radius=radius)
    
    surface.blit(glass_surf, rect.topleft)

def create_nebula_background(width, height):
    """Create and cache a nebula background surface"""
    cache_key = f"nebula_bg_{width}_{height}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    bg = pygame.Surface((width, height))
    center = (width // 2, height // 2)
    radius = max(width, height) // 1.2
    
    for r in range(int(radius), 0, -1):
        ratio = r / radius
        color = (
            int(COLORS["nebula_deep"][0] * (1 - ratio) + COLORS["nebula_mid"][0] * ratio),
            int(COLORS["nebula_deep"][1] * (1 - ratio) + COLORS["nebula_mid"][1] * ratio),
            int(COLORS["nebula_deep"][2] * (1 - ratio) + COLORS["nebula_mid"][2] * ratio)
        )
        pygame.draw.circle(bg, color, center, r)
    
    accent_center = (width // 3, height // 3)
    glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*COLORS["violet_deep"], 30), accent_center, 200)
    bg.blit(glow_surf, (0, 0))
    
    accent_center2 = (width * 2 // 3, height * 2 // 3)
    glow_surf2 = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf2, (*COLORS["nebula_accent"], 20), accent_center2, 180)
    bg.blit(glow_surf2, (0, 0))
    
    bg = bg.convert()
    _image_cache[cache_key] = bg
    return bg

from theme import COLORS