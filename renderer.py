# renderer.py
import pygame
import theme
import settings as s
import random
import math
from utils import draw_glass_rect, create_warm_background, ease_out_cubic, ease_out_back, clamp, get_cached_text, clear_image_cache
from sound_manager import SoundManager

class HangmanAnimation:
    def __init__(self):
        self.current_part = 0
        self.animation_progress = 0
        self.animation_speed = 2.5
        self.is_animating = False
        self.completed_parts = 0
    
    def start_new_part(self, target_parts):
        if target_parts > self.completed_parts:
            self.current_part = target_parts
            self.animation_progress = 0
            self.is_animating = True
        self.completed_parts = max(self.completed_parts, target_parts)
    
    def update(self, dt):
        if self.is_animating:
            self.animation_progress += dt * self.animation_speed
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
    
    def get_draw_progress(self, part_number):
        if part_number < self.completed_parts:
            return 1.0
        elif part_number == self.current_part and self.is_animating:
            return ease_out_cubic(self.animation_progress)
        elif part_number <= self.completed_parts:
            return 1.0
        return 0
    
    def reset(self):
        self.current_part = 0
        self.animation_progress = 0
        self.is_animating = False
        self.completed_parts = 0

class FloatingText:
    def __init__(self, text, x, y, color, lifetime=40):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.lifetime -= 1
        self.y -= 1.5
        return self.lifetime > 0
    
    def get_alpha(self):
        return int(255 * (self.lifetime / self.max_lifetime))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.lifetime = 25
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class PygameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        
        self._init_fonts()
        self._init_surfaces()
        
        self.buttons = {}
        self.menu_button = None
        self.hint_button = None
        self.hovered_button = None
        self.pressed_button = None
        self.press_timer = 0
        
        self.message = ""
        self.message_timer = 0
        self.message_color = theme.COLORS["incorrect"]
        self.message_surface = None
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_timer = 0
        
        self.flash_alpha = 0
        self.flash_color = (0, 0, 0)
        
        self.hangman_float = 0
        self.float_phase = 0
        
        self.button_hover_scale = {}
        
        self.prev_score = 0
        self.prev_streak = 0
        self.streak_pulse_timer = 0
        
        self.hangman_animation = HangmanAnimation()
        self.current_mistakes = 0
        
        self.pause_buttons = {}
        self.pause_hover = None
        
        self.floating_texts = []
        self.particles = []
        
        self.update_layout()
    
    def _init_fonts(self):
        self.font_title = pygame.font.Font(None, s.FONT_SIZE_HUGE)
        self.font_large = pygame.font.Font(None, s.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, s.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, s.FONT_SIZE_SMALL)
        self.font_tiny = pygame.font.Font(None, s.FONT_SIZE_TINY)
        
    def _init_surfaces(self):
        self.background = None
        self.update_background()
    
    def update_background(self):
        self.background = create_warm_background(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
        
    def update_layout(self):
        self.update_background()
        self._create_keyboard_buttons()
        self._init_fonts()
        self.button_hover_scale = {letter: 0 for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    
    def _create_keyboard_buttons(self):
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]
        
        base_button_size = 50
        button_margin = 8
        
        scale_x = s.SCREEN_WIDTH / s.BASE_WIDTH
        scale_y = s.SCREEN_HEIGHT / s.BASE_HEIGHT
        scale = min(scale_x, scale_y)
        
        button_size = int(base_button_size * scale)
        margin = int(button_margin * scale)
        
        total_keyboard_width = 10 * (button_size + margin) - margin
        start_x = (s.SCREEN_WIDTH - total_keyboard_width) // 2
        base_y = int(s.SCREEN_HEIGHT * 0.72)
        
        row_y_offsets = [0, int(button_size * 0.2), int(button_size * 0.4)]
        
        for row_idx, row in enumerate(rows):
            row_width = len(row) * (button_size + margin) - margin
            row_start_x = start_x + (total_keyboard_width - row_width) // 2
            if row_idx == 1:
                row_start_x += int(button_size * 0.2)
            elif row_idx == 2:
                row_start_x += int(button_size * 0.4)
            
            for col_idx, letter in enumerate(row):
                x = row_start_x + col_idx * (button_size + margin)
                y = base_y + row_y_offsets[row_idx] + row_idx * (button_size + margin)
                self.buttons[letter] = pygame.Rect(x, y, button_size, button_size)
    
    def _create_pause_buttons(self):
        button_w = int(s.SCREEN_WIDTH * 0.18)
        button_h = int(s.SCREEN_HEIGHT * 0.06)
        start_y = s.SCREEN_HEIGHT // 2 - button_h
        
        self.pause_buttons = {
            "resume": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y, button_w, button_h),
            "mute": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + button_h + 15, button_w, button_h),
            "exit": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + 2 * (button_h + 15), button_w, button_h)
        }
    
    def add_floating_text(self, text, x, y, is_positive=True):
        color = theme.COLORS["correct"] if is_positive else theme.COLORS["incorrect"]
        self.floating_texts.append(FloatingText(text, x, y, color, 40))
    
    def add_particles(self, x, y, color):
        for _ in range(10):
            self.particles.append(Particle(x, y, color))
    
    def draw_hangman(self, lives, max_lives):
        base_x = int(s.SCREEN_WIDTH * 0.18)
        base_y = int(s.SCREEN_HEIGHT * 0.32)
        
        self.float_phase += 0.015
        self.hangman_float = math.sin(self.float_phase) * 2
        
        mistakes = max_lives - lives
        
        if mistakes > self.current_mistakes:
            self.hangman_animation.start_new_part(mistakes)
        self.current_mistakes = mistakes
        
        dt = self.clock.get_time() / 1000.0
        self.hangman_animation.update(dt)
        
        platform_w = int(s.SCREEN_WIDTH * 0.16)
        platform = pygame.Rect(base_x - 30, base_y + 150 + self.hangman_float, platform_w, 8)
        pygame.draw.rect(self.screen, theme.COLORS["text_muted"], platform, border_radius=4)
        
        pole_h = int(s.SCREEN_HEIGHT * 0.22)
        pole = pygame.Rect(base_x + 30, base_y - 30 + self.hangman_float, 8, pole_h)
        pygame.draw.rect(self.screen, theme.COLORS["text_muted"], pole, border_radius=4)
        
        beam_w = int(s.SCREEN_WIDTH * 0.1)
        beam = pygame.Rect(base_x + 30, base_y - 30 + self.hangman_float, beam_w, 8)
        pygame.draw.rect(self.screen, theme.COLORS["text_muted"], beam, border_radius=4)
        
        rope_x = base_x + 30 + beam_w - 8
        rope_y_end = base_y + 25 + self.hangman_float
        pygame.draw.line(self.screen, theme.COLORS["text_muted"], 
                        (rope_x, base_y - 22 + self.hangman_float), (rope_x, rope_y_end), 3)
        
        head_y = rope_y_end + 15
        
        if mistakes >= 1:
            progress = self.hangman_animation.get_draw_progress(1)
            if progress > 0:
                head_radius = int(20 * progress)
                inner_radius = int(16 * progress)
                if head_radius > 0:
                    pygame.draw.circle(self.screen, theme.COLORS["accent_primary"], (rope_x, head_y), head_radius)
                    if inner_radius > 0:
                        pygame.draw.circle(self.screen, theme.COLORS["bg_warm"], (rope_x, head_y), inner_radius)
                        pygame.draw.circle(self.screen, theme.COLORS["accent_secondary"], (rope_x, head_y), inner_radius, 2)
                
                if progress > 0.5:
                    eye_y = head_y - 5
                    pygame.draw.circle(self.screen, theme.COLORS["text_primary"], (rope_x - 6, eye_y), 2)
                    pygame.draw.circle(self.screen, theme.COLORS["text_primary"], (rope_x + 6, eye_y), 2)
        
        if mistakes >= 2:
            progress = self.hangman_animation.get_draw_progress(2)
            if progress > 0:
                body_end_y = head_y + 20 + int(50 * progress)
                pygame.draw.line(self.screen, theme.COLORS["accent_primary"], 
                               (rope_x, head_y + 20), (rope_x, body_end_y), 6)
        
        if mistakes >= 3:
            progress = self.hangman_animation.get_draw_progress(3)
            if progress > 0:
                arm_end_x = rope_x - int(30 * progress)
                arm_end_y = head_y + 30 + int(15 * progress)
                pygame.draw.line(self.screen, theme.COLORS["accent_primary"], 
                               (rope_x, head_y + 30), (arm_end_x, arm_end_y), 5)
        
        if mistakes >= 4:
            progress = self.hangman_animation.get_draw_progress(4)
            if progress > 0:
                arm_end_x = rope_x + int(30 * progress)
                arm_end_y = head_y + 30 + int(15 * progress)
                pygame.draw.line(self.screen, theme.COLORS["accent_primary"], 
                               (rope_x, head_y + 30), (arm_end_x, arm_end_y), 5)
        
        if mistakes >= 5:
            progress = self.hangman_animation.get_draw_progress(5)
            if progress > 0:
                leg_end_x = rope_x - int(25 * progress)
                leg_end_y = head_y + 70 + int(30 * progress)
                pygame.draw.line(self.screen, theme.COLORS["accent_primary"], 
                               (rope_x, head_y + 70), (leg_end_x, leg_end_y), 5)
        
        if mistakes >= 6:
            progress = self.hangman_animation.get_draw_progress(6)
            if progress > 0:
                leg_end_x = rope_x + int(25 * progress)
                leg_end_y = head_y + 70 + int(30 * progress)
                pygame.draw.line(self.screen, theme.COLORS["accent_primary"], 
                               (rope_x, head_y + 70), (leg_end_x, leg_end_y), 5)
    
    def draw_category_badge(self, category):
        if not category:
            return
        
        category_text = category.replace('_', ' ').title()
        text = get_cached_text(self.font_small, category_text, theme.COLORS["accent_secondary"])
        
        padding = 20
        bg_width = text.get_width() + padding * 2
        bg_height = text.get_height() + 8
        bg_x = s.SCREEN_WIDTH // 2 - bg_width // 2
        bg_y = int(s.SCREEN_HEIGHT * 0.46)
        
        bg_rect = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
        draw_glass_rect(self.screen, bg_rect, theme.COLORS["glass_dark"], 20, border_width=1, border_color=theme.COLORS["accent_soft"])
        
        text_rect = text.get_rect(center=bg_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_word_display(self, display_word):
        letters = display_word.split()
        letter_spacing = int(s.SCREEN_WIDTH * 0.045)
        total_width = len(letters) * letter_spacing
        start_x = (s.SCREEN_WIDTH - total_width) // 2 + letter_spacing // 2
        
        for i, letter in enumerate(letters):
            x = start_x + i * letter_spacing + self.shake_offset_x
            y = int(s.SCREEN_HEIGHT * 0.54) + self.shake_offset_y
            
            if letter != "_":
                color = theme.COLORS["accent_primary"]
                text = get_cached_text(self.font_large, letter, color)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
            else:
                text = get_cached_text(self.font_large, "_", theme.COLORS["text_muted"])
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
            
            bar_w = int(letter_spacing * 0.7)
            bar_x = x - bar_w//2
            bar_y = y + 35
            
            if letter != "_":
                bar_rect = pygame.Rect(bar_x, bar_y, bar_w, 4)
                pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], bar_rect, border_radius=2)
            else:
                bar_rect = pygame.Rect(bar_x, bar_y, bar_w, 3)
                pygame.draw.rect(self.screen, theme.COLORS["text_muted"], bar_rect, border_radius=2)
    
    def draw_guessed_letters(self, guessed):
        if not guessed:
            return
        
        text_str = " ".join(guessed)
        text = get_cached_text(self.font_small, text_str, theme.COLORS["text_secondary"])
        text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.66)))
        
        padding = 15
        bg = pygame.Rect(text_rect.x - padding, text_rect.y - 6, 
                        text_rect.width + padding * 2, text_rect.height + 12)
        draw_glass_rect(self.screen, bg, theme.COLORS["glass_dark"], 15, 
                       border_width=1, border_color=theme.COLORS["glass_border"])
        self.screen.blit(text, text_rect)
    
    def draw_buttons(self, guessed):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = None
        
        if self.press_timer > 0:
            self.press_timer -= 1
            if self.press_timer == 0:
                self.pressed_button = None
        
        for letter, rect in self.buttons.items():
            is_disabled = letter in guessed
            
            is_hover = rect.collidepoint(mouse_pos) and not is_disabled
            is_pressed = self.pressed_button == letter and self.press_timer > 0
            
            target = 1 if is_hover else 0
            if letter not in self.button_hover_scale:
                self.button_hover_scale[letter] = 0
            self.button_hover_scale[letter] += (target - self.button_hover_scale[letter]) * 0.15
            
            scale = 1.0 + self.button_hover_scale[letter] * 0.05
            if is_pressed:
                scale = 0.95
            
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
            scaled_rect.center = rect.center
            
            if is_disabled:
                color = theme.COLORS["glass_dark"]
                border = theme.COLORS["text_muted"]
                text_color = theme.COLORS["text_muted"]
                draw_glass_rect(self.screen, scaled_rect, color, 12, border_width=1, border_color=border)
                text = get_cached_text(self.font_small, letter, text_color)
                text_rect = text.get_rect(center=scaled_rect.center)
                self.screen.blit(text, text_rect)
                pygame.draw.line(self.screen, theme.COLORS["incorrect"], 
                               (scaled_rect.x + 10, scaled_rect.centery), 
                               (scaled_rect.right - 10, scaled_rect.centery), 2)
            else:
                if is_hover:
                    color = theme.COLORS["glass_light"]
                    border = theme.COLORS["accent_primary"]
                    self.hovered_button = letter
                else:
                    color = theme.COLORS["glass_warm"]
                    border = theme.COLORS["glass_border"]
                    
                draw_glass_rect(self.screen, scaled_rect, color, 12, border_width=2, border_color=border)
                
                text_color = theme.COLORS["accent_primary"] if is_hover else theme.COLORS["text_primary"]
                text = get_cached_text(self.font_small, letter, text_color)
                text_rect = text.get_rect(center=scaled_rect.center)
                self.screen.blit(text, text_rect)
    
    def draw_lives(self, lives, max_lives):
        x = int(s.SCREEN_WIDTH * 0.03)
        y = int(s.SCREEN_HEIGHT * 0.04)
        
        lives_text = get_cached_text(self.font_small, "LIVES", theme.COLORS["text_secondary"])
        self.screen.blit(lives_text, (x, y - 20))
        
        spacing = int(s.SCREEN_WIDTH * 0.03)
        for i in range(max_lives):
            cx = x + i * spacing + 12
            cy = y + 15
            
            if i < lives:
                color = theme.COLORS["incorrect"]
            else:
                color = theme.COLORS["text_muted"]
            
            size = int(s.SCREEN_WIDTH * 0.01)
            heart_points = [
                (cx, cy - size),
                (cx + size, cy - size//2),
                (cx + size//2, cy + size//2),
                (cx, cy + size),
                (cx - size//2, cy + size//2),
                (cx - size, cy - size//2)
            ]
            pygame.draw.polygon(self.screen, color, heart_points)
    
    def draw_score_panel(self, score, streak, hint_cost, can_afford):
        panel_w = int(s.SCREEN_WIDTH * 0.14)
        panel_h = int(s.SCREEN_HEIGHT * 0.13)
        panel_x = s.SCREEN_WIDTH - panel_w - int(s.SCREEN_WIDTH * 0.02)
        panel_y = int(s.SCREEN_HEIGHT * 0.03)
        
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_glass_rect(self.screen, panel, theme.COLORS["glass_dark"], 15,
                       border_width=2, border_color=theme.COLORS["glass_border"])
        
        score_label = get_cached_text(self.font_tiny, "SCORE", theme.COLORS["text_secondary"])
        score_label_rect = score_label.get_rect(center=(panel_x + panel_w//2, panel_y + 18))
        self.screen.blit(score_label, score_label_rect)
        
        score_surface = get_cached_text(self.font_medium, str(score), theme.COLORS["warning"])
        score_rect = score_surface.get_rect(center=(panel_x + panel_w//2, panel_y + 48))
        self.screen.blit(score_surface, score_rect)
        
        if streak > 1:
            streak_surface = get_cached_text(self.font_small, f"STREAK x{streak}", theme.COLORS["accent_primary"])
            streak_rect = streak_surface.get_rect(center=(panel_x + panel_w//2, panel_y + 78))
            self.screen.blit(streak_surface, streak_rect)
        
        hint_color = theme.COLORS["text_primary"] if can_afford else theme.COLORS["text_muted"]
        hint_label = get_cached_text(self.font_tiny, f"HINT: {hint_cost}", hint_color)
        hint_label_rect = hint_label.get_rect(center=(panel_x + panel_w//2, panel_y + 98))
        self.screen.blit(hint_label, hint_label_rect)
    
    def draw_message_popup(self):
        if self.message and self.message_timer > 0:
            alpha = min(255, self.message_timer * 8)
            if self.message_surface is None or self.message_surface.get_alpha() != alpha:
                text = get_cached_text(self.font_medium, self.message, self.message_color)
                self.message_surface = text.copy()
                self.message_surface.set_alpha(alpha)
            
            y_off = (1 - self.message_timer / 45) * 30
            text_rect = self.message_surface.get_rect(center=(s.SCREEN_WIDTH // 2 + self.shake_offset_x, 
                                              int(s.SCREEN_HEIGHT * 0.75) + self.shake_offset_y - y_off))
            bg = pygame.Rect(text_rect.x - 20, text_rect.y - 10, 
                            text_rect.width + 40, text_rect.height + 20)
            draw_glass_rect(self.screen, bg, (60, 45, 55, 200), 20, border_width=1, border_color=(*self.message_color, alpha // 2))
            self.screen.blit(self.message_surface, text_rect)
            self.message_timer -= 1
        else:
            self.message_surface = None
    
    def draw_floating_texts(self):
        for text in self.floating_texts[:]:
            if not text.update():
                self.floating_texts.remove(text)
            else:
                alpha = text.get_alpha()
                surf = get_cached_text(self.font_small, text.text, text.color)
                surf.set_alpha(alpha)
                self.screen.blit(surf, (text.x - surf.get_width() // 2, text.y))
    
    def draw_particles(self):
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(self.screen)
    
    def draw_menu_button(self):
        button_w = int(s.SCREEN_WIDTH * 0.08)
        button_h = int(s.SCREEN_HEIGHT * 0.05)
        self.menu_button = pygame.Rect(
            s.SCREEN_WIDTH - button_w - int(s.SCREEN_WIDTH * 0.02),
            int(s.SCREEN_HEIGHT * 0.19),
            button_w, button_h
        )
        is_hover = self.menu_button.collidepoint(pygame.mouse.get_pos())
        color = theme.COLORS["glass_light"] if is_hover else theme.COLORS["glass_warm"]
        border = theme.COLORS["accent_primary"] if is_hover else theme.COLORS["glass_border"]
        
        draw_glass_rect(self.screen, self.menu_button, color, 10, border_width=2, border_color=border)
        menu_text = get_cached_text(self.font_tiny, "MENU", theme.COLORS["text_primary"])
        text_rect = menu_text.get_rect(center=self.menu_button.center)
        self.screen.blit(menu_text, text_rect)
    
    def draw_hint_button(self, game_state):
        if game_state["game_over"]:
            return
            
        button_w = int(s.SCREEN_WIDTH * 0.08)
        button_h = int(s.SCREEN_HEIGHT * 0.05)
        self.hint_button = pygame.Rect(
            s.SCREEN_WIDTH - button_w - int(s.SCREEN_WIDTH * 0.02),
            int(s.SCREEN_HEIGHT * 0.26),
            button_w, button_h
        )
        is_hover = self.hint_button.collidepoint(pygame.mouse.get_pos())
        can_afford = game_state["can_afford_hint"]
        
        if not can_afford:
            color = (60, 60, 80, 180)
            border = theme.COLORS["text_muted"]
            text_color = theme.COLORS["text_muted"]
        elif is_hover:
            color = theme.COLORS["glass_light"]
            border = theme.COLORS["accent_secondary"]
            text_color = theme.COLORS["accent_primary"]
        else:
            color = theme.COLORS["glass_warm"]
            border = theme.COLORS["glass_border"]
            text_color = theme.COLORS["text_primary"]
            
        draw_glass_rect(self.screen, self.hint_button, color, 10, border_width=2, border_color=border)
        hint_text = get_cached_text(self.font_tiny, "HINT", text_color)
        text_rect = hint_text.get_rect(center=self.hint_button.center)
        self.screen.blit(hint_text, text_rect)
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(theme.COLORS["bg_deep"])
        self.screen.blit(overlay, (0, 0))
        
        self._create_pause_buttons()
        mouse_pos = pygame.mouse.get_pos()
        self.pause_hover = None
        
        paused_title = get_cached_text(self.font_large, "PAUSED", theme.COLORS["accent_primary"])
        title_rect = paused_title.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 3))
        self.screen.blit(paused_title, title_rect)
        
        mute_text_str = "UNMUTE" if not self.sound_manager.enabled else "MUTE"
        resume_text = get_cached_text(self.font_small, "RESUME", theme.COLORS["text_primary"])
        mute_text = get_cached_text(self.font_small, mute_text_str, theme.COLORS["text_primary"])
        exit_text = get_cached_text(self.font_small, "EXIT TO MENU", theme.COLORS["text_primary"])
        
        button_texts = {
            "resume": resume_text,
            "mute": mute_text,
            "exit": exit_text
        }
        
        for name, rect in self.pause_buttons.items():
            is_hover = rect.collidepoint(mouse_pos)
            if is_hover:
                self.pause_hover = name
                color = theme.COLORS["glass_light"]
                border = theme.COLORS["accent_primary"]
            else:
                color = theme.COLORS["glass_warm"]
                border = theme.COLORS["glass_border"]
            
            draw_glass_rect(self.screen, rect, color, 12, border_width=2, border_color=border)
            
            text_rect = button_texts[name].get_rect(center=rect.center)
            self.screen.blit(button_texts[name], text_rect)
    
    def draw_end_screen(self, won, secret, final_score, is_high_score):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(theme.COLORS["bg_deep"])
        self.screen.blit(overlay, (0, 0))
        
        card_w = int(s.SCREEN_WIDTH * 0.45)
        card_h = int(s.SCREEN_HEIGHT * 0.45)
        card_x = (s.SCREEN_WIDTH - card_w) // 2
        card_y = (s.SCREEN_HEIGHT - card_h) // 2
        
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        draw_glass_rect(card, pygame.Rect(0, 0, card_w, card_h), theme.COLORS["glass_warm"], 25,
                       border_width=3, border_color=theme.COLORS["accent_soft"])
        
        if won:
            title = "YOU WIN!"
            title_color = theme.COLORS["correct"]
        else:
            title = "GAME OVER"
            title_color = theme.COLORS["incorrect"]
            
        title_text = get_cached_text(self.font_title, title, title_color)
        title_rect = title_text.get_rect(center=(card_w // 2, 65))
        card.blit(title_text, title_rect)
        
        score_text = get_cached_text(self.font_medium, f"SCORE: {final_score}", theme.COLORS["text_primary"])
        score_rect = score_text.get_rect(center=(card_w // 2, 130))
        card.blit(score_text, score_rect)
        
        if is_high_score:
            high_text = get_cached_text(self.font_small, "NEW HIGH SCORE!", theme.COLORS["warning"])
            high_rect = high_text.get_rect(center=(card_w // 2, 170))
            card.blit(high_text, high_rect)
        
        if not won:
            word_text = get_cached_text(self.font_medium, f"WORD: {secret}", theme.COLORS["accent_secondary"])
            word_rect = word_text.get_rect(center=(card_w // 2, 215 if not is_high_score else 230))
            card.blit(word_text, word_rect)
        
        button_width = 170
        button_height = 45
        button_spacing = 20
        button_y = card_h - 85
        
        play_again_rect = pygame.Rect(card_w // 2 - button_width - button_spacing // 2, button_y, button_width, button_height)
        main_menu_rect = pygame.Rect(card_w // 2 + button_spacing // 2, button_y, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        global_mouse_x = mouse_pos[0] - card_x
        global_mouse_y = mouse_pos[1] - card_y
        
        is_play_hover = play_again_rect.collidepoint(global_mouse_x, global_mouse_y)
        is_menu_hover = main_menu_rect.collidepoint(global_mouse_x, global_mouse_y)
        
        play_color = theme.COLORS["glass_light"] if is_play_hover else theme.COLORS["accent_primary"]
        menu_color = theme.COLORS["glass_light"] if is_menu_hover else theme.COLORS["glass_warm"]
        
        draw_glass_rect(card, play_again_rect, play_color, 10, border_width=2, border_color=theme.COLORS["text_primary"])
        draw_glass_rect(card, main_menu_rect, menu_color, 10, border_width=2, border_color=theme.COLORS["glass_border"])
        
        play_text = get_cached_text(self.font_small, "PLAY AGAIN", theme.COLORS["text_primary"])
        menu_text = get_cached_text(self.font_small, "MAIN MENU", theme.COLORS["text_primary"])
        
        play_text_rect = play_text.get_rect(center=play_again_rect.center)
        menu_text_rect = menu_text.get_rect(center=main_menu_rect.center)
        
        card.blit(play_text, play_text_rect)
        card.blit(menu_text, menu_text_rect)
        
        prompt_text = get_cached_text(self.font_tiny, "PRESS SPACE TO PLAY AGAIN", theme.COLORS["text_muted"])
        prompt_rect = prompt_text.get_rect(center=(card_w // 2, card_h - 25))
        card.blit(prompt_text, prompt_rect)
        
        self.screen.blit(card, (card_x, card_y))
        
        return play_again_rect, main_menu_rect, card_x, card_y
    
    def draw_flash_overlay(self):
        if self.flash_alpha > 0:
            flash = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            flash.set_alpha(self.flash_alpha)
            flash.fill(self.flash_color)
            self.screen.blit(flash, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 8)
    
    def draw(self, game_state, paused=False):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        self.draw_hangman(game_state["lives"], game_state["max_lives"])
        self.draw_category_badge(game_state.get("category"))
        self.draw_word_display(game_state["display"])
        self.draw_guessed_letters(game_state["guessed"])
        self.draw_buttons(game_state["guessed"])
        self.draw_lives(game_state["lives"], game_state["max_lives"])
        self.draw_score_panel(game_state["score"], game_state["streak"], 
                              game_state["hint_cost"], game_state["can_afford_hint"])
        self.draw_message_popup()
        self.draw_floating_texts()
        self.draw_particles()
        self.draw_menu_button()
        self.draw_hint_button(game_state)
        self.draw_flash_overlay()
        
        if paused:
            self.draw_pause_menu()
        
        self.shake_offset_x = random.randint(-4, 4) if self.shake_timer > 0 else 0
        self.shake_offset_y = random.randint(-3, 3) if self.shake_timer > 0 else 0
        self.shake_timer = max(0, self.shake_timer - 1)
        
        pygame.display.flip()
        self.clock.tick(s.FPS)
    
    def handle_events(self, paused=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                return ("resize", event.w, event.h)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "esc"
                if event.key == pygame.K_F11:
                    return "fullscreen"
                if not paused and event.unicode.isalpha():
                    return event.unicode.upper()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.sound_manager.play("click")
                
                if paused:
                    if self.pause_hover:
                        return f"pause_{self.pause_hover}"
                else:
                    if self.hovered_button:
                        self.pressed_button = self.hovered_button
                        self.press_timer = 5
                        return self.hovered_button
                    if self.menu_button and self.menu_button.collidepoint(event.pos):
                        return "menu"
                    if self.hint_button and self.hint_button.collidepoint(event.pos):
                        return "hint"
        return None
    
    def show_message(self, msg, is_error=True):
        self.message = msg
        self.message_timer = 40
        self.message_color = theme.COLORS["incorrect"] if is_error else theme.COLORS["correct"]
        self.message_surface = None
        
        if is_error:
            self.shake_timer = 8
            self.flash_alpha = 40
            self.flash_color = theme.COLORS["incorrect"]
            self.sound_manager.play("wrong")
        else:
            self.flash_alpha = 30
            self.flash_color = theme.COLORS["correct"]
            self.sound_manager.play("correct")
    
    def on_correct_guess(self, points, word_x, word_y):
        self.add_floating_text(f"+{points}", word_x, word_y - 40, True)
        self.add_particles(word_x, word_y, theme.COLORS["correct"])
        
    def on_wrong_guess(self, letter_x, letter_y):
        self.add_floating_text("MISS", letter_x, letter_y - 30, False)
        self.add_particles(letter_x, letter_y, theme.COLORS["incorrect"])