# utils.py
import json
import random
import math
import pygame
from pathlib import Path

_image_cache = {}
_text_cache = {}

def load_image(path, use_alpha=True):
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
        return random.choice(words).upper(), category
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

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def draw_glass_rect(surface, rect, color, radius, border_width=1, border_color=None, shadow=True):
    if shadow:
        shadow_surf = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (6, 6, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surf, (rect.x - 6, rect.y - 6))
    
    glass_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glass_surf, color, (0, 0, rect.width, rect.height), border_radius=radius)
    
    if border_width > 0:
        if border_color is None:
            border_color = (255, 220, 190, 100)
        pygame.draw.rect(glass_surf, border_color, (0, 0, rect.width, rect.height), border_width, border_radius=radius)
    
    surface.blit(glass_surf, rect.topleft)

def create_warm_background(width, height):
    cache_key = f"warm_bg_{width}_{height}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    bg = pygame.Surface((width, height))
    
    for y in range(height):
        ratio = y / height
        r = int(COLORS["bg_deep"][0] * (1 - ratio) + COLORS["bg_light"][0] * ratio)
        g = int(COLORS["bg_deep"][1] * (1 - ratio) + COLORS["bg_light"][1] * ratio)
        b = int(COLORS["bg_deep"][2] * (1 - ratio) + COLORS["bg_light"][2] * ratio)
        pygame.draw.line(bg, (r, g, b), (0, y), (width, y))
    
    for _ in range(40):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(15, 60)
        alpha = random.randint(10, 25)
        color = (255, 200, 150, alpha)
        glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, color, (x, y), radius)
        bg.blit(glow_surf, (0, 0))
    
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 2)
        brightness = random.randint(180, 255)
        pygame.draw.circle(bg, (brightness, brightness - 20, brightness - 40), (x, y), size)
    
    bg = bg.convert()
    _image_cache[cache_key] = bg
    return bg

def create_nebula_background(width, height):
    return create_warm_background(width, height)

from theme import COLORS