# renderer.py
import pygame
import theme
import settings as s
import random
import math
from utils import draw_glass_rect, create_nebula_background, ease_out_cubic, clamp, get_cached_text, clear_image_cache
from sound_manager import SoundManager

class HangmanAnimation:
    def __init__(self):
        self.current_part = 0
        self.animation_progress = 0
        self.animation_speed = 2.5
        self.is_animating = False
        self.completed_parts = 0
    
    def start_new_part(self, target_parts):
        """Start animating only the NEW part - previous parts stay fully drawn"""
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
        """Return progress for a specific part (0-1)"""
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
        
        self.update_layout()
        
    def _init_fonts(self):
        """Initialize all fonts once at startup"""
        self.font_huge = pygame.font.Font(None, s.FONT_SIZE_HUGE)
        self.font_large = pygame.font.Font(None, s.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, s.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, s.FONT_SIZE_SMALL)
        self.font_tiny = pygame.font.Font(None, s.FONT_SIZE_TINY)
        
    def _init_surfaces(self):
        """Initialize all surfaces once"""
        self.background = None
        self.update_background()
        
    def _init_text_cache(self):
        """Pre-render static text surfaces"""
        self.lives_label = get_cached_text(self.font_small, "LIVES", theme.COLORS["text_secondary"])
        self.score_label = get_cached_text(self.font_tiny, "SCORE", theme.COLORS["text_secondary"])
        self.menu_text = get_cached_text(self.font_tiny, "MENU", theme.COLORS["text_primary"])
        self.hint_text = get_cached_text(self.font_tiny, "HINT", theme.COLORS["text_primary"])
        self.hint_text_disabled = get_cached_text(self.font_tiny, "HINT", theme.COLORS["text_muted"])
        self.resume_text = get_cached_text(self.font_small, "Resume", theme.COLORS["text_primary"])
        self.exit_text = get_cached_text(self.font_small, "Exit to Menu", theme.COLORS["text_primary"])
        self.paused_title = get_cached_text(self.font_large, "PAUSED", theme.COLORS["cyan_glow"])
        
    def update_background(self):
        """Update cached background for current dimensions"""
        self.background = create_nebula_background(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
        
    def update_layout(self):
        """Recalculate all UI element positions based on current window size"""
        self.update_background()
        self._create_keyboard_buttons()
        self._init_fonts()
        self._init_text_cache()
        self.button_hover_scale = {letter: 0 for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        
    def _create_keyboard_buttons(self):
        """Create keyboard buttons with dynamic relative positioning"""
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        
        button_spacing = s.BUTTON_HEIGHT + s.BUTTON_MARGIN
        total_height = 3 * button_spacing
        
        base_y = s.SCREEN_HEIGHT - total_height - int(s.SCREEN_HEIGHT * 0.04)
        
        for row_idx, row in enumerate(rows):
            total_width = len(row) * (s.BUTTON_WIDTH + s.BUTTON_MARGIN) - s.BUTTON_MARGIN
            start_x = (s.SCREEN_WIDTH - total_width) // 2
            
            if row_idx == 1:
                start_x += int(s.SCREEN_WIDTH * 0.02)
            elif row_idx == 2:
                start_x += int(s.SCREEN_WIDTH * 0.055)
            
            for col_idx, letter in enumerate(row):
                x = start_x + col_idx * (s.BUTTON_WIDTH + s.BUTTON_MARGIN)
                y = base_y + row_idx * button_spacing
                self.buttons[letter] = pygame.Rect(x, y, s.BUTTON_WIDTH, s.BUTTON_HEIGHT)
                
    def _create_pause_buttons(self):
        """Create pause menu buttons with dynamic positioning"""
        button_w = int(s.SCREEN_WIDTH * 0.15)
        button_h = int(s.SCREEN_HEIGHT * 0.06)
        start_y = s.SCREEN_HEIGHT // 2 - button_h
        
        self.pause_buttons = {
            "resume": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y, button_w, button_h),
            "mute": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + button_h + 15, button_w, button_h),
            "exit": pygame.Rect(s.SCREEN_WIDTH // 2 - button_w // 2, start_y + 2 * (button_h + 15), button_w, button_h)
        }
                
    def draw_hangman(self, lives, max_lives):
        base_x = int(s.SCREEN_WIDTH * 0.18)
        base_y = int(s.SCREEN_HEIGHT * 0.35)
        
        self.float_phase += 0.015
        self.hangman_float = math.sin(self.float_phase) * 2
        
        mistakes = max_lives - lives
        
        if mistakes > self.current_mistakes:
            self.hangman_animation.start_new_part(mistakes)
        self.current_mistakes = mistakes
        
        dt = self.clock.get_time() / 1000.0
        self.hangman_animation.update(dt)
        
        # Draw static parts (gallows) - always fully drawn
        platform_w = int(s.SCREEN_WIDTH * 0.16)
        platform = pygame.Rect(base_x - 30, base_y + 150 + self.hangman_float, platform_w, 8)
        pygame.draw.rect(self.screen, theme.COLORS["text_secondary"], platform, border_radius=4)
        
        pole_h = int(s.SCREEN_HEIGHT * 0.22)
        pole = pygame.Rect(base_x + 30, base_y - 30 + self.hangman_float, 8, pole_h)
        pygame.draw.rect(self.screen, theme.COLORS["text_secondary"], pole, border_radius=4)
        
        beam_w = int(s.SCREEN_WIDTH * 0.1)
        beam = pygame.Rect(base_x + 30, base_y - 30 + self.hangman_float, beam_w, 8)
        pygame.draw.rect(self.screen, theme.COLORS["text_secondary"], beam, border_radius=4)
        
        rope_x = base_x + 30 + beam_w - 8
        rope_y_end = base_y + 25 + self.hangman_float
        pygame.draw.line(self.screen, theme.COLORS["text_muted"], 
                        (rope_x, base_y - 22 + self.hangman_float), (rope_x, rope_y_end), 3)
        
        head_y = rope_y_end + 15
        
        # Draw each part with its individual animation progress
        # Part 1: Head
        if mistakes >= 1:
            progress = self.hangman_animation.get_draw_progress(1)
            if progress > 0:
                # Scale radius by progress for grow-in effect
                head_radius = int(20 * progress)
                inner_radius = int(16 * progress)
                if head_radius > 0:
                    pygame.draw.circle(self.screen, theme.COLORS["cyan_glow"], (rope_x, head_y), head_radius)
                    if inner_radius > 0:
                        pygame.draw.circle(self.screen, theme.COLORS["nebula_deep"], (rope_x, head_y), inner_radius)
                        pygame.draw.circle(self.screen, theme.COLORS["cyan_glow"], (rope_x, head_y), inner_radius, 2)
                
                if progress > 0.5:
                    eye_y = head_y - 5
                    pygame.draw.circle(self.screen, theme.COLORS["nebula_deep"], (rope_x - 7, eye_y), 4)
                    pygame.draw.circle(self.screen, theme.COLORS["nebula_deep"], (rope_x + 7, eye_y), 4)
        
        # Part 2: Body
        if mistakes >= 2:
            progress = self.hangman_animation.get_draw_progress(2)
            if progress > 0:
                body_end_y = head_y + 20 + int(55 * progress)
                pygame.draw.line(self.screen, theme.COLORS["cyan_glow"], 
                               (rope_x, head_y + 20), (rope_x, body_end_y), 7)
        
        # Part 3: Left arm
        if mistakes >= 3:
            progress = self.hangman_animation.get_draw_progress(3)
            if progress > 0:
                arm_end_x = rope_x - int(30 * progress)
                arm_end_y = head_y + 30 + int(15 * progress)
                pygame.draw.line(self.screen, theme.COLORS["cyan_glow"], 
                               (rope_x, head_y + 30), (arm_end_x, arm_end_y), 6)
        
        # Part 4: Right arm
        if mistakes >= 4:
            progress = self.hangman_animation.get_draw_progress(4)
            if progress > 0:
                arm_end_x = rope_x + int(30 * progress)
                arm_end_y = head_y + 30 + int(15 * progress)
                pygame.draw.line(self.screen, theme.COLORS["cyan_glow"], 
                               (rope_x, head_y + 30), (arm_end_x, arm_end_y), 6)
        
        # Part 5: Left leg
        if mistakes >= 5:
            progress = self.hangman_animation.get_draw_progress(5)
            if progress > 0:
                leg_end_x = rope_x - int(25 * progress)
                leg_end_y = head_y + 75 + int(35 * progress)
                pygame.draw.line(self.screen, theme.COLORS["cyan_glow"], 
                               (rope_x, head_y + 75), (leg_end_x, leg_end_y), 6)
        
        # Part 6: Right leg
        if mistakes >= 6:
            progress = self.hangman_animation.get_draw_progress(6)
            if progress > 0:
                leg_end_x = rope_x + int(25 * progress)
                leg_end_y = head_y + 75 + int(35 * progress)
                pygame.draw.line(self.screen, theme.COLORS["cyan_glow"], 
                               (rope_x, head_y + 75), (leg_end_x, leg_end_y), 6)
                           
    def draw_word_display(self, display_word):
        letters = display_word.split()
        letter_spacing = int(s.SCREEN_WIDTH * 0.05)
        total_width = len(letters) * letter_spacing
        start_x = (s.SCREEN_WIDTH - total_width) // 2 + letter_spacing // 2
        
        for i, letter in enumerate(letters):
            x = start_x + i * letter_spacing + self.shake_offset_x
            y = int(s.SCREEN_HEIGHT * 0.55) + self.shake_offset_y
            
            color = theme.COLORS["cyan_glow"] if letter != "_" else theme.COLORS["text_secondary"]
            text = get_cached_text(self.font_large, letter, color)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
            
            bar_w = int(letter_spacing * 0.8)
            bar = pygame.Rect(x - bar_w//2, y + 30, bar_w, 4 if letter != "_" else 3)
            if letter != "_":
                pygame.draw.rect(self.screen, theme.COLORS["cyan_glow"], bar, border_radius=2)
            else:
                pygame.draw.rect(self.screen, theme.COLORS["text_muted"], bar, border_radius=2)
                               
    def draw_guessed_letters(self, guessed):
        if not guessed:
            return
        text_str = "Guessed: " + " ".join(guessed)
        text = get_cached_text(self.font_small, text_str, theme.COLORS["text_secondary"])
        text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.68)))
        
        padding = 20
        bg = pygame.Rect(text_rect.x - padding, text_rect.y - 8, 
                        text_rect.width + padding * 2, text_rect.height + 16)
        draw_glass_rect(self.screen, bg, theme.COLORS["glass_medium"], 20, 
                       border_width=1, border_color=theme.COLORS["glass_border"])
        self.screen.blit(text, text_rect)
        
    def draw_buttons(self, guessed):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = None
        
        for letter, rect in self.buttons.items():
            if letter in guessed:
                continue
                
            is_hover = rect.collidepoint(mouse_pos)
            target = 1 if is_hover else 0
            if letter not in self.button_hover_scale:
                self.button_hover_scale[letter] = 0
            self.button_hover_scale[letter] += (target - self.button_hover_scale[letter]) * 0.15
            
            scale = 1.0 + ease_out_cubic(self.button_hover_scale[letter]) * 0.05
            scaled_rect = rect.inflate(rect.width * (scale - 1), rect.height * (scale - 1))
            scaled_rect.center = rect.center
            
            if is_hover:
                color = theme.COLORS["glass_light"]
                border = theme.COLORS["cyan_glow"]
                self.hovered_button = letter
            else:
                color = theme.COLORS["glass_medium"]
                border = theme.COLORS["glass_border"]
                
            draw_glass_rect(self.screen, scaled_rect, color, s.BUTTON_RADIUS,
                           border_width=2, border_color=border)
            
            text_color = theme.COLORS["cyan_glow"] if is_hover else theme.COLORS["text_primary"]
            text = get_cached_text(self.font_small, letter, text_color)
            text_rect = text.get_rect(center=scaled_rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_lives(self, lives, max_lives):
        x = int(s.SCREEN_WIDTH * 0.03)
        y = int(s.SCREEN_HEIGHT * 0.04)
        
        self.screen.blit(self.lives_label, (x, y - 20))
        
        spacing = int(s.SCREEN_WIDTH * 0.035)
        for i in range(max_lives):
            cx = x + i * spacing + 14
            cy = y + 20
            color = theme.COLORS["error"] if i < lives else theme.COLORS["text_muted"]
            
            size = int(s.SCREEN_WIDTH * 0.011)
            points = [(cx, cy - size), (cx + size, cy - size//2), (cx + size//2, cy + size//2),
                     (cx, cy + size), (cx - size//2, cy + size//2), (cx - size, cy - size//2)]
            pygame.draw.polygon(self.screen, color, points)
            
    def draw_score_panel(self, score, streak, hint_cost, can_afford):
        panel_w = int(s.SCREEN_WIDTH * 0.15)
        panel_h = int(s.SCREEN_HEIGHT * 0.14)
        panel_x = s.SCREEN_WIDTH - panel_w - int(s.SCREEN_WIDTH * 0.02)
        panel_y = int(s.SCREEN_HEIGHT * 0.03)
        
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_glass_rect(self.screen, panel, theme.COLORS["glass_medium"], 15,
                       border_width=2, border_color=theme.COLORS["glass_border"])
        
        score_label_rect = self.score_label.get_rect(center=(panel_x + panel_w//2, panel_y + 18))
        self.screen.blit(self.score_label, score_label_rect)
        
        # Only re-render score when it changes
        if score != self.prev_score:
            self.score_surface = get_cached_text(self.font_medium, str(score), theme.COLORS["warning"])
            self.prev_score = score
        if self.score_surface:
            score_rect = self.score_surface.get_rect(center=(panel_x + panel_w//2, panel_y + 48))
            self.screen.blit(self.score_surface, score_rect)
        
        if streak > 1:
            if streak != self.prev_streak:
                self.streak_surface = get_cached_text(self.font_small, f"Streak: x{streak}", theme.COLORS["violet_glow"])
                self.prev_streak = streak
            if self.streak_surface:
                streak_rect = self.streak_surface.get_rect(center=(panel_x + panel_w//2, panel_y + 78))
                self.screen.blit(self.streak_surface, streak_rect)
            
        hint_color = theme.COLORS["text_primary"] if can_afford else theme.COLORS["text_muted"]
        hint_label = get_cached_text(self.font_tiny, f"Hint: {hint_cost} pts", hint_color)
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
            draw_glass_rect(self.screen, bg, theme.COLORS["glass_light"], 25,
                           border_width=1, border_color=(*self.message_color, alpha // 2))
            self.screen.blit(self.message_surface, text_rect)
            self.message_timer -= 1
            
    def draw_menu_button(self):
        button_w = int(s.SCREEN_WIDTH * 0.08)
        button_h = int(s.SCREEN_HEIGHT * 0.05)
        self.menu_button = pygame.Rect(
            s.SCREEN_WIDTH - button_w - int(s.SCREEN_WIDTH * 0.02),
            int(s.SCREEN_HEIGHT * 0.19),
            button_w, button_h
        )
        is_hover = self.menu_button.collidepoint(pygame.mouse.get_pos())
        color = theme.COLORS["glass_light"] if is_hover else theme.COLORS["glass_medium"]
        border = theme.COLORS["cyan_glow"] if is_hover else theme.COLORS["glass_border"]
        
        draw_glass_rect(self.screen, self.menu_button, color, 10, border_width=2, border_color=border)
        text_rect = self.menu_text.get_rect(center=self.menu_button.center)
        self.screen.blit(self.menu_text, text_rect)
        
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
            text = self.hint_text_disabled
        elif is_hover:
            color = theme.COLORS["glass_light"]
            border = theme.COLORS["violet_glow"]
            text = self.hint_text
        else:
            color = theme.COLORS["glass_medium"]
            border = theme.COLORS["glass_border"]
            text = self.hint_text
            
        draw_glass_rect(self.screen, self.hint_button, color, 10, border_width=2, border_color=border)
        text_rect = text.get_rect(center=self.hint_button.center)
        self.screen.blit(text, text_rect)
        
    def draw_pause_menu(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(theme.COLORS["nebula_deep"])
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
                color = theme.COLORS["glass_light"]
                border = theme.COLORS["cyan_glow"]
            else:
                color = theme.COLORS["glass_medium"]
                border = theme.COLORS["glass_border"]
            
            draw_glass_rect(self.screen, rect, color, 12, border_width=2, border_color=border)
            
            text_rect = button_texts[name].get_rect(center=rect.center)
            self.screen.blit(button_texts[name], text_rect)
        
    def draw_game_over(self, won, secret, final_score, is_high_score=False):
        self.card_animation = min(1, self.card_animation + 0.04)
        t = ease_out_cubic(self.card_animation)
        
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(int(200 * t))
        overlay.fill(theme.COLORS["nebula_deep"])
        self.screen.blit(overlay, (0, 0))
        
        card_w = int(s.SCREEN_WIDTH * 0.45)
        card_h = int(s.SCREEN_HEIGHT * 0.4)
        card_x = (s.SCREEN_WIDTH - card_w * t) // 2
        card_y = (s.SCREEN_HEIGHT - card_h * t) // 2
        
        if t > 0.01:
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            draw_glass_rect(card, pygame.Rect(0, 0, card_w, card_h), theme.COLORS["glass_medium"], 25,
                           border_width=3, border_color=theme.COLORS["glass_border"])
            
            if won:
                title = "VICTORY!"
                title_color = theme.COLORS["success"]
            else:
                title = "DEFEAT"
                title_color = theme.COLORS["error"]
                
            title_text = get_cached_text(self.font_huge, title, title_color)
            title_rect = title_text.get_rect(center=(card_w // 2, 80))
            card.blit(title_text, title_rect)
            
            score_text = get_cached_text(self.font_medium, f"Final Score: {final_score}", theme.COLORS["text_primary"])
            score_rect = score_text.get_rect(center=(card_w // 2, 150))
            card.blit(score_text, score_rect)
            
            if is_high_score:
                high_text = get_cached_text(self.font_small, "NEW HIGH SCORE!", theme.COLORS["warning"])
                high_rect = high_text.get_rect(center=(card_w // 2, 190))
                card.blit(high_text, high_rect)
            
            if not won:
                word_text = get_cached_text(self.font_medium, f"Word: {secret}", theme.COLORS["text_secondary"])
                word_rect = word_text.get_rect(center=(card_w // 2, 230 if not is_high_score else 250))
                card.blit(word_text, word_rect)
                
            prompt = get_cached_text(self.font_small, "SPACE to continue  •  ESC for menu", theme.COLORS["text_muted"])
            prompt_rect = prompt.get_rect(center=(card_w // 2, card_h - 50))
            card.blit(prompt, prompt_rect)
            
            scaled = pygame.transform.scale(card, (int(card_w * t), int(card_h * t)))
            self.screen.blit(scaled, (card_x, card_y))
            
    def draw_flash_overlay(self):
        if self.flash_alpha > 0:
            flash = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            flash.set_alpha(self.flash_alpha)
            flash.fill(self.flash_color)
            self.screen.blit(flash, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 6)
            
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
        self.draw_menu_button()
        self.draw_hint_button(game_state)
        self.draw_flash_overlay()
        
        if paused:
            self.draw_pause_menu()
        
        if game_state["game_over"]:
            self.draw_game_over(game_state["won"], game_state["secret"], 
                               game_state["score"], game_state.get("is_high_score", False))
        else:
            self.card_animation = 0
            
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
                if event.key == pygame.K_SPACE:
                    return "space"
                if event.key == pygame.K_F11:
                    return "fullscreen"
                # H KEY REMOVED - only letter keys return the letter
                if not paused and event.unicode.isalpha():
                    return event.unicode.upper()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.sound_manager.play("click")
                
                if paused:
                    if self.pause_hover:
                        return f"pause_{self.pause_hover}"
                else:
                    if self.hovered_button:
                        return self.hovered_button
                    if self.menu_button and self.menu_button.collidepoint(event.pos):
                        return "menu"
                    if self.hint_button and self.hint_button.collidepoint(event.pos):
                        return "hint"
        return None
        
    def show_message(self, msg, is_error=True):
        self.message = msg
        self.message_timer = 40
        self.message_color = theme.COLORS["error"] if is_error else theme.COLORS["success"]
        self.message_surface = None
        
        if is_error:
            self.shake_timer = 8
            self.flash_alpha = 30
            self.flash_color = theme.COLORS["error"]
            self.sound_manager.play("wrong")
        else:
            self.flash_alpha = 20
            self.flash_color = theme.COLORS["success"]
            self.sound_manager.play("correct")