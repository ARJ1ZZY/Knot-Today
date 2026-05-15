# renderer.py - Retro 8-Bit Style with Fixed Button Layout
import pygame
import theme
import settings as s
import random
import math
from utils import get_cached_text, clear_image_cache
from sound_manager import SoundManager

# 8-bit pixel font sizes
PIXEL_FONT_SIZES = {
    "tiny": 14,
    "small": 18,
    "medium": 24,
    "large": 36,
    "huge": 48
}

class HangmanAnimation:
    def __init__(self):
        self.current_part = 0
        self.animation_progress = 0
        self.animation_speed = 3.0
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
            return min(1.0, self.animation_progress)
        elif part_number <= self.completed_parts:
            return 1.0
        return 0
    
    def reset(self):
        self.current_part = 0
        self.animation_progress = 0
        self.is_animating = False
        self.completed_parts = 0

class FloatingText:
    def __init__(self, text, x, y, color, lifetime=30):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.lifetime -= 1
        self.y -= 1
        return self.lifetime > 0
    
    def get_alpha(self):
        return int(255 * (self.lifetime / self.max_lifetime))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3, -1)
        self.lifetime = 20
        self.size = random.randint(2, 3)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.size > 0:
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))

class PygameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        
        self._init_fonts()
        self._init_surfaces()
        self._init_text_cache()
        
        self.buttons = {}
        self.menu_button = None
        self.hint_button = None
        self.hovered_button = None
        self.hover_timer = 0
        self.last_hovered_button = None
        self.pressed_button = None
        self.press_timer = 0
        
        self.message = ""
        self.message_timer = 0
        self.message_color = theme.COLORS["error"]
        self.message_surface = None
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_timer = 0
        
        self.flash_alpha = 0
        self.flash_color = (0, 0, 0)
        
        self.card_animation = 0
        self.hangman_float = 0
        self.float_phase = 0
        
        self.button_hover_scale = {}
        
        self.score_display = 0
        self.prev_score = 0
        self.score_surface = None
        self.streak_surface = None
        self.prev_streak = 0
        
        self.hangman_animation = HangmanAnimation()
        self.current_mistakes = 0
        
        self.pause_buttons = {}
        self.pause_hover = None
        
        self.floating_texts = []
        self.particles = []
        
        self.update_layout()
        
    def _init_fonts(self):
        self.font_huge = pygame.font.Font(None, PIXEL_FONT_SIZES["huge"])
        self.font_large = pygame.font.Font(None, PIXEL_FONT_SIZES["large"])
        self.font_medium = pygame.font.Font(None, PIXEL_FONT_SIZES["medium"])
        self.font_small = pygame.font.Font(None, PIXEL_FONT_SIZES["small"])
        self.font_tiny = pygame.font.Font(None, PIXEL_FONT_SIZES["tiny"])
        
    def _init_surfaces(self):
        self.background = None
        self.update_background()
        
    def _init_text_cache(self):
        self.lives_label = get_cached_text(self.font_small, "LIVES", theme.COLORS["text_secondary"])
        self.score_label = get_cached_text(self.font_tiny, "SCORE", theme.COLORS["text_secondary"])
        self.menu_text = get_cached_text(self.font_tiny, "MENU", theme.COLORS["text_primary"])
        self.hint_text = get_cached_text(self.font_tiny, "HINT", theme.COLORS["text_primary"])
        self.hint_text_disabled = get_cached_text(self.font_tiny, "HINT", theme.COLORS["text_muted"])
        self.resume_text = get_cached_text(self.font_small, "RESUME", theme.COLORS["text_primary"])
        self.exit_text = get_cached_text(self.font_small, "EXIT", theme.COLORS["text_primary"])
        self.paused_title = get_cached_text(self.font_large, "PAUSED", theme.COLORS["accent_primary"])
        
    def update_background(self):
        self.background = self._create_8bit_background(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
    
    def _create_8bit_background(self, width, height):
        bg = pygame.Surface((width, height))
        bg.fill(theme.COLORS["bg_primary"])
        
        grid_size = 32
        for x in range(0, width, grid_size):
            for y in range(0, height, grid_size):
                if (x // grid_size + y // grid_size) % 2 == 0:
                    rect = pygame.Rect(x, y, grid_size, grid_size)
                    pygame.draw.rect(bg, theme.COLORS["bg_secondary"], rect)
        
        for y in range(0, height, 4):
            pygame.draw.line(bg, (10, 10, 15, 30), (0, y), (width, y))
        
        return bg.convert()
        
    def update_layout(self):
        self.update_background()
        self._create_keyboard_buttons()
        self._init_fonts()
        self._init_text_cache()
        self.button_hover_scale = {letter: 0 for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        
    def _draw_pixel_rect(self, rect, color, border_color=None, border_width=2):
        pygame.draw.rect(self.screen, color, rect)
        if border_color:
            pygame.draw.rect(self.screen, border_color, rect, border_width)
            inner_rect = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, (60, 60, 70), inner_rect, 1)
        
    def _create_keyboard_buttons(self):
        button_width = 48
        button_height = 48
        margin = 6
        
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]
        
        max_row_width = len(rows[0]) * (button_width + margin) - margin
        start_x = (s.SCREEN_WIDTH - max_row_width) // 2
        base_y = s.SCREEN_HEIGHT - (len(rows) * (button_height + margin)) - 20
        
        for row_idx, row in enumerate(rows):
            row_width = len(row) * (button_width + margin) - margin
            row_start_x = start_x + (max_row_width - row_width) // 2
            
            if row_idx == 1:
                row_start_x += 16
            elif row_idx == 2:
                row_start_x += 32
            
            for col_idx, letter in enumerate(row):
                x = row_start_x + col_idx * (button_width + margin)
                y = base_y + row_idx * (button_height + margin)
                self.buttons[letter] = pygame.Rect(x, y, button_width, button_height)
                
    def _create_pause_buttons(self):
        button_w = 160
        button_h = 48
        start_y = s.SCREEN_HEIGHT // 2 - button_h
        
        self.pause_buttons = {
            "resume": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y, button_w, button_h),
            "mute": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + button_h + 15, button_w, button_h),
            "exit": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + 2 * (button_h + 15), button_w, button_h)
        }
    
    def add_floating_text(self, text, x, y, is_positive=True):
        color = theme.COLORS["success"] if is_positive else theme.COLORS["error"]
        self.floating_texts.append(FloatingText(text, x, y, color, 30))
    
    def add_particles(self, x, y, color):
        for _ in range(6):
            self.particles.append(Particle(x, y, color))
    
    def on_correct_guess(self, points, word_x, word_y):
        if points > 0:
            self.add_floating_text(f"+{points}", word_x, word_y - 40, True)
        self.add_particles(word_x, word_y, theme.COLORS["success"])
        self.sound_manager.play_sfx("correct")
        
    def on_wrong_guess(self, letter_x, letter_y):
        self.add_floating_text("MISS", letter_x, letter_y - 30, False)
        self.add_particles(letter_x, letter_y, theme.COLORS["error"])
        self.sound_manager.play_sfx("incorrect")
    
    def _draw_pixel_hangman(self, mistakes):
        """Draw retro 8-bit hangman figure"""
        base_x = int(s.SCREEN_WIDTH * 0.18)
        base_y = int(s.SCREEN_HEIGHT * 0.30)
        
        gallows_color = theme.COLORS["text_secondary"]
        
        platform_rect = pygame.Rect(base_x - 20, base_y + 160, 100, 6)
        pygame.draw.rect(self.screen, gallows_color, platform_rect)
        
        pole_rect = pygame.Rect(base_x + 40, base_y - 20, 6, 180)
        pygame.draw.rect(self.screen, gallows_color, pole_rect)
        
        beam_rect = pygame.Rect(base_x + 40, base_y - 20, 70, 6)
        pygame.draw.rect(self.screen, gallows_color, beam_rect)
        
        rope_x = base_x + 105
        rope_rect = pygame.Rect(rope_x - 3, base_y - 14, 6, 30)
        pygame.draw.rect(self.screen, theme.COLORS["text_muted"], rope_rect)
        
        head_x = rope_x
        head_y = base_y + 20
        
        if mistakes >= 1:
            head_rect = pygame.Rect(head_x - 12, head_y - 12, 24, 24)
            pygame.draw.rect(self.screen, theme.COLORS["accent_primary"], head_rect)
            pygame.draw.rect(self.screen, theme.COLORS["border_dark"], head_rect, 2)
            pygame.draw.rect(self.screen, theme.COLORS["text_primary"], (head_x - 7, head_y - 5, 4, 4))
            pygame.draw.rect(self.screen, theme.COLORS["text_primary"], (head_x + 3, head_y - 5, 4, 4))
        
        if mistakes >= 2:
            body_rect = pygame.Rect(head_x - 5, head_y + 14, 10, 40)
            pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], body_rect)
        
        if mistakes >= 3:
            arm_rect = pygame.Rect(head_x - 20, head_y + 20, 18, 6)
            pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], arm_rect)
        
        if mistakes >= 4:
            arm_rect = pygame.Rect(head_x + 2, head_y + 20, 18, 6)
            pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], arm_rect)
        
        if mistakes >= 5:
            leg_rect = pygame.Rect(head_x - 12, head_y + 50, 12, 6)
            pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], leg_rect)
        
        if mistakes >= 6:
            leg_rect = pygame.Rect(head_x, head_y + 50, 12, 6)
            pygame.draw.rect(self.screen, theme.COLORS["accent_secondary"], leg_rect)
        
        return head_x, head_y
    
    def draw_hangman(self, lives, max_lives):
        mistakes = max_lives - lives
        
        if mistakes > self.current_mistakes:
            self.hangman_animation.start_new_part(mistakes)
        self.current_mistakes = mistakes
        
        dt = self.clock.get_time() / 1000.0
        self.hangman_animation.update(dt)
        
        self._draw_pixel_hangman(mistakes)
                           
    def draw_word_display(self, display_word):
        letters = display_word.split()
        letter_spacing = int(s.SCREEN_WIDTH * 0.045)
        total_width = len(letters) * letter_spacing
        start_x = (s.SCREEN_WIDTH - total_width) // 2 + letter_spacing // 2
        
        for i, letter in enumerate(letters):
            x = start_x + i * letter_spacing + self.shake_offset_x
            y = int(s.SCREEN_HEIGHT * 0.48) + self.shake_offset_y
            
            if letter != "_":
                text = get_cached_text(self.font_large, letter, theme.COLORS["accent_primary"])
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
                
                bar_rect = pygame.Rect(x - 15, y + 20, 30, 3)
                pygame.draw.rect(self.screen, theme.COLORS["accent_primary"], bar_rect)
            else:
                text = get_cached_text(self.font_large, "_", theme.COLORS["text_muted"])
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
                
                bar_rect = pygame.Rect(x - 15, y + 20, 30, 2)
                pygame.draw.rect(self.screen, theme.COLORS["text_muted"], bar_rect)
                               
    def draw_guessed_letters(self, guessed):
        if not guessed:
            return
        
        text_str = " ".join(guessed)
        text = get_cached_text(self.font_small, text_str, theme.COLORS["text_secondary"])
        text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.58)))
        
        padding = 15
        bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - 6, 
                              text_rect.width + padding * 2, text_rect.height + 12)
        pygame.draw.rect(self.screen, theme.COLORS["surface_dark"], bg_rect)
        pygame.draw.rect(self.screen, theme.COLORS["border_light"], bg_rect, 2)
        self.screen.blit(text, text_rect)
        
    def draw_buttons(self, guessed):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = None
        
        for letter, rect in self.buttons.items():
            if letter in guessed:
                color = theme.COLORS["key_disabled"]
                text_color = theme.COLORS["key_text_disabled"]
                self._draw_pixel_rect(rect, color, theme.COLORS["border_dark"], 1)
                text = get_cached_text(self.font_small, letter, text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
            else:
                is_hover = rect.collidepoint(mouse_pos)
                if is_hover:
                    color = theme.COLORS["key_hover"]
                    self.hovered_button = letter
                    if self.last_hovered_button != letter:
                        self.sound_manager.play_sfx("hover")
                        self.last_hovered_button = letter
                else:
                    color = theme.COLORS["key_normal"]
                    if self.last_hovered_button == letter:
                        self.last_hovered_button = None
                    
                self._draw_pixel_rect(rect, color, theme.COLORS["border_light"], 2)
                text_color = theme.COLORS["accent_primary"] if is_hover else theme.COLORS["key_text"]
                text = get_cached_text(self.font_small, letter, text_color)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
            
    def draw_lives(self, lives, max_lives):
        x = int(s.SCREEN_WIDTH * 0.03)
        y = int(s.SCREEN_HEIGHT * 0.04)
        
        self.screen.blit(self.lives_label, (x, y - 20))
        
        spacing = 25
        for i in range(max_lives):
            cx = x + i * spacing + 10
            cy = y + 10
            color = theme.COLORS["accent_primary"] if i < lives else theme.COLORS["text_muted"]
            
            heart_rect = pygame.Rect(cx - 6, cy - 5, 12, 10)
            pygame.draw.rect(self.screen, color, heart_rect)
            pygame.draw.rect(self.screen, theme.COLORS["border_dark"], heart_rect, 1)
            
    def draw_score_panel(self, score, streak, hint_cost, can_afford):
        panel_w = 180
        panel_h = 110
        panel_x = s.SCREEN_WIDTH - panel_w - 20
        panel_y = 20
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, theme.COLORS["surface_dark"], panel_rect)
        pygame.draw.rect(self.screen, theme.COLORS["border_light"], panel_rect, 2)
        
        score_label_rect = self.score_label.get_rect(center=(panel_x + panel_w // 2, panel_y + 18))
        self.screen.blit(self.score_label, score_label_rect)
        
        if score != self.prev_score:
            self.score_surface = get_cached_text(self.font_medium, str(score), theme.COLORS["warning"])
            self.prev_score = score
        if self.score_surface:
            score_rect = self.score_surface.get_rect(center=(panel_x + panel_w // 2, panel_y + 48))
            self.screen.blit(self.score_surface, score_rect)
        
        if streak > 1:
            if streak != self.prev_streak:
                self.streak_surface = get_cached_text(self.font_small, f"x{streak} STREAK", theme.COLORS["accent_primary"])
                self.prev_streak = streak
            if self.streak_surface:
                streak_rect = self.streak_surface.get_rect(center=(panel_x + panel_w // 2, panel_y + 75))
                self.screen.blit(self.streak_surface, streak_rect)
        
        hint_color = theme.COLORS["text_primary"] if can_afford else theme.COLORS["text_muted"]
        hint_label = get_cached_text(self.font_tiny, f"HINT:{hint_cost}", hint_color)
        hint_rect = hint_label.get_rect(center=(panel_x + panel_w // 2, panel_y + 95))
        self.screen.blit(hint_label, hint_rect)
    
    def draw_menu_button(self):
        button_w = 70
        button_h = 35
        self.menu_button = pygame.Rect(
            s.SCREEN_WIDTH - button_w - 15,
            145,
            button_w, button_h
        )
        is_hover = self.menu_button.collidepoint(pygame.mouse.get_pos())
        color = theme.COLORS["key_hover"] if is_hover else theme.COLORS["key_normal"]
        
        if is_hover and self.last_hovered_button != "menu":
            self.sound_manager.play_sfx("hover")
            self.last_hovered_button = "menu"
        elif not is_hover and self.last_hovered_button == "menu":
            self.last_hovered_button = None
        
        self._draw_pixel_rect(self.menu_button, color, theme.COLORS["border_light"], 2)
        text_rect = self.menu_text.get_rect(center=self.menu_button.center)
        self.screen.blit(self.menu_text, text_rect)
        
    def draw_hint_button(self, game_state):
        if game_state["game_over"]:
            return
            
        button_w = 70
        button_h = 35
        self.hint_button = pygame.Rect(
            s.SCREEN_WIDTH - button_w - 15,
            190,
            button_w, button_h
        )
        is_hover = self.hint_button.collidepoint(pygame.mouse.get_pos())
        can_afford = game_state["can_afford_hint"]
        
        if is_hover and can_afford and self.last_hovered_button != "hint":
            self.sound_manager.play_sfx("hover")
            self.last_hovered_button = "hint"
        elif (not is_hover or not can_afford) and self.last_hovered_button == "hint":
            self.last_hovered_button = None
        
        if not can_afford:
            color = theme.COLORS["key_disabled"]
            text = self.hint_text_disabled
        elif is_hover:
            color = theme.COLORS["accent_hover"]
            text = self.hint_text
        else:
            color = theme.COLORS["accent_primary"]
            text = self.hint_text
            
        self._draw_pixel_rect(self.hint_button, color, theme.COLORS["border_light"], 2)
        text_rect = text.get_rect(center=self.hint_button.center)
        self.screen.blit(text, text_rect)
        
    def draw_pause_menu(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(theme.COLORS["bg_primary"])
        self.screen.blit(overlay, (0, 0))
        
        self._create_pause_buttons()
        mouse_pos = pygame.mouse.get_pos()
        self.pause_hover = None
        
        title_rect = self.paused_title.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 3))
        self.screen.blit(self.paused_title, title_rect)
        
        mute_text_str = self.sound_manager.get_mute_text()
        mute_text = get_cached_text(self.font_small, mute_text_str, theme.COLORS["text_primary"])
        
        button_texts = {
            "resume": self.resume_text,
            "mute": mute_text,
            "exit": self.exit_text
        }
        
        for name, rect in self.pause_buttons.items():
            is_hover = rect.collidepoint(mouse_pos)
            if is_hover:
                self.pause_hover = name
                color = theme.COLORS["accent_hover"]
                if self.last_hovered_button != name:
                    self.sound_manager.play_sfx("hover")
                    self.last_hovered_button = name
            else:
                color = theme.COLORS["key_normal"]
                if self.last_hovered_button == name:
                    self.last_hovered_button = None
            
            self._draw_pixel_rect(rect, color, theme.COLORS["border_light"], 2)
            
            text_rect = button_texts[name].get_rect(center=rect.center)
            self.screen.blit(button_texts[name], text_rect)
    
    def draw_end_screen(self, won, secret_word, final_score, is_high_score=False):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(theme.COLORS["bg_primary"])
        self.screen.blit(overlay, (0, 0))
        
        card_w = 600
        card_h = 420
        card_x = (s.SCREEN_WIDTH - card_w) // 2
        card_y = (s.SCREEN_HEIGHT - card_h) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(self.screen, theme.COLORS["surface_dark"], card_rect)
        pygame.draw.rect(self.screen, theme.COLORS["border_light"], card_rect, 3)
        
        if won:
            title = "VICTORY!"
            title_color = theme.COLORS["success"]
        else:
            title = "GAME OVER"
            title_color = theme.COLORS["error"]
            
        title_text = get_cached_text(self.font_huge, title, title_color)
        title_rect = title_text.get_rect(center=(card_x + card_w // 2, card_y + 60))
        self.screen.blit(title_text, title_rect)
        
        word_label = get_cached_text(self.font_small, "THE WORD WAS:", theme.COLORS["text_secondary"])
        word_label_rect = word_label.get_rect(center=(card_x + card_w // 2, card_y + 130))
        self.screen.blit(word_label, word_label_rect)
        
        letter_width = 46
        letter_height = 46
        letter_spacing = 8
        
        total_width = len(secret_word) * (letter_width + letter_spacing) - letter_spacing
        start_x = card_x + (card_w - total_width) // 2
        start_y = card_y + 165
        
        for i, letter in enumerate(secret_word):
            button_rect = pygame.Rect(start_x + i * (letter_width + letter_spacing), start_y, letter_width, letter_height)
            
            pygame.draw.rect(self.screen, theme.COLORS["key_normal"], button_rect)
            pygame.draw.rect(self.screen, theme.COLORS["border_light"], button_rect, 2)
            inner_rect = button_rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, (60, 60, 70), inner_rect, 1)
            
            letter_text = get_cached_text(self.font_small, letter, theme.COLORS["accent_primary"])
            letter_rect = letter_text.get_rect(center=button_rect.center)
            self.screen.blit(letter_text, letter_rect)
        
        score_text = get_cached_text(self.font_medium, f"SCORE: {final_score}", theme.COLORS["text_primary"])
        score_rect = score_text.get_rect(center=(card_x + card_w // 2, start_y + letter_height + 35))
        self.screen.blit(score_text, score_rect)
        
        if is_high_score:
            high_text = get_cached_text(self.font_small, "NEW HIGH SCORE!", theme.COLORS["warning"])
            high_rect = high_text.get_rect(center=(card_x + card_w // 2, start_y + letter_height + 70))
            self.screen.blit(high_text, high_rect)
        
        button_width = 160
        button_height = 45
        button_spacing = 30
        button_y = card_y + card_h - 80
        
        play_again_rect = pygame.Rect(card_x + card_w // 2 - button_width - button_spacing // 2, button_y, button_width, button_height)
        main_menu_rect = pygame.Rect(card_x + card_w // 2 + button_spacing // 2, button_y, button_width, button_height)
        
        self._draw_pixel_rect(play_again_rect, theme.COLORS["accent_primary"], theme.COLORS["border_light"], 2)
        self._draw_pixel_rect(main_menu_rect, theme.COLORS["key_normal"], theme.COLORS["border_light"], 2)
        
        play_text = get_cached_text(self.font_small, "PLAY AGAIN", theme.COLORS["text_primary"])
        menu_text = get_cached_text(self.font_small, "MAIN MENU", theme.COLORS["text_primary"])
        
        play_text_rect = play_text.get_rect(center=play_again_rect.center)
        menu_text_rect = menu_text.get_rect(center=main_menu_rect.center)
        
        self.screen.blit(play_text, play_text_rect)
        self.screen.blit(menu_text, menu_text_rect)
        
        prompt_text = get_cached_text(self.font_tiny, "SPACE  |  ESC", theme.COLORS["text_muted"])
        prompt_rect = prompt_text.get_rect(center=(card_x + card_w // 2, card_y + card_h - 25))
        self.screen.blit(prompt_text, prompt_rect)
        
        return play_again_rect, main_menu_rect, card_x, card_y
        
    def draw_flash_overlay(self):
        if self.flash_alpha > 0:
            flash = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            flash.set_alpha(self.flash_alpha)
            flash.fill(self.flash_color)
            self.screen.blit(flash, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 8)
    
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
    
    def draw_message_popup(self):
        if self.message and self.message_timer > 0:
            alpha = min(255, self.message_timer * 10)
            if self.message_surface is None or self.message_surface.get_alpha() != alpha:
                text = get_cached_text(self.font_medium, self.message, self.message_color)
                self.message_surface = text.copy()
                self.message_surface.set_alpha(alpha)
            
            text_rect = self.message_surface.get_rect(center=(s.SCREEN_WIDTH // 2 + self.shake_offset_x, 
                                              int(s.SCREEN_HEIGHT * 0.72) + self.shake_offset_y))
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, theme.COLORS["surface_dark"], bg_rect)
            pygame.draw.rect(self.screen, self.message_color, bg_rect, 2)
            self.screen.blit(self.message_surface, text_rect)
            self.message_timer -= 1
        else:
            self.message_surface = None
            
    def draw(self, game_state, paused=False):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        
        self.draw_hangman(game_state["lives"], game_state["max_lives"])
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
        
        if not game_state["game_over"]:
            self.draw_hint_button(game_state)
        
        self.draw_flash_overlay()
        
        if paused:
            self.draw_pause_menu()
            
        self.shake_offset_x = random.randint(-3, 3) if self.shake_timer > 0 else 0
        self.shake_offset_y = random.randint(-2, 2) if self.shake_timer > 0 else 0
        self.shake_timer = max(0, self.shake_timer - 1)
            
        pygame.display.flip()
        self.clock.tick(s.FPS)
        
    def show_message(self, msg, is_error=True):
        self.message = msg
        self.message_timer = 35
        self.message_color = theme.COLORS["error"] if is_error else theme.COLORS["success"]
        self.message_surface = None
        
        if is_error:
            self.shake_timer = 6
            self.flash_alpha = 40
            self.flash_color = theme.COLORS["error"]
        else:
            self.flash_alpha = 30
            self.flash_color = theme.COLORS["success"]