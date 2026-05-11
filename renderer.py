from email.mime import text
from turtle import width

import pygame
import theme
import settings as s
from game_state import GameState

class PygameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_SMALL)
        self.buttons = self._create_keyboard_buttons()
        self.hovered_button = None
        self.message = ""
        self.message_end_time = 0
        self.flash_end_time = 0
        self.ui_buttons = []

    def _create_keyboard_buttons(self):
        buttons = {}
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rows = [letters[0:10], letters[10:20], letters[20:]]

        width, height = self.screen.get_size()

        button_width = width // 20        # scales with screen width
        button_height = height // 15      # scales with screen height
        margin = button_width // 5        

        start_y = height - 200

        for row_idx, row_letters in enumerate(rows):
            row_count = len(row_letters)
            row_width = row_count * button_width + (row_count - 1) * margin
            row_start_x = (width - row_width) // 2
            y = start_y + row_idx * (button_height + margin)

            for col, letter in enumerate(row_letters):
                x = row_start_x + col * (button_width + margin)

                # Explicit use of center=
                rect = pygame.Rect(0, 0, button_width, button_height)
                rect = rect.copy()  # ensure we have a rect object
                rect.center = (x + button_width // 2, y + button_height // 2)

                buttons[letter] = rect

        return buttons

    def draw(self):
        # Recalculate buttons every frame so they adapt to screen size
        self.buttons = self._create_keyboard_buttons()

        # ... rest of your draw code
        for letter, rect in self.buttons.items():
            pygame.draw.rect(self.screen, theme.COLORS["accent"], rect, 2)
            text = self.font_small.render(letter, True, theme.COLORS["text_primary"])
            text_rect = text.get_rect(center=rect.center)  # explicit center use
            self.screen.blit(text, text_rect)

        # draw other UI elements (word display, wrong guesses, etc.)
        pygame.display.flip()

    def draw_hangman(self, lives, max_lives):
        width, height = self.screen.get_size()
        base_x = width // 2 - 40
        base_y = height // 6
        
        if lives == 1:
            color = theme.COLORS["error"]
        elif lives == 2:
            color = theme.COLORS["orange"]
        elif lives == 3:
            color = theme.COLORS["yellow"]
        else:
            color = theme.COLORS["text_primary"]
        
        # Gallows
        pygame.draw.line(self.screen, color, (base_x, base_y + 150), (base_x + 80, base_y + 150), 4)
        pygame.draw.line(self.screen, color, (base_x + 20, base_y), (base_x + 20, base_y + 150), 4)
        pygame.draw.line(self.screen, color, (base_x + 20, base_y), (base_x + 80, base_y), 4)
        pygame.draw.line(self.screen, color, (base_x + 80, base_y), (base_x + 80, base_y + 30), 4)
        
        mistakes = max_lives - lives
        
        if mistakes >= 1:  # Head
            pygame.draw.circle(self.screen, color, (base_x + 80, base_y + 45), 15, 3)
        if mistakes >= 2:  # Body
            pygame.draw.line(self.screen, color, (base_x + 80, base_y + 60), (base_x + 80, base_y + 100), 3)
        if mistakes >= 3:  # Left arm
            pygame.draw.line(self.screen, color, (base_x + 80, base_y + 70), (base_x + 60, base_y + 85), 3)
        if mistakes >= 4:  # Right arm
            pygame.draw.line(self.screen, color, (base_x + 80, base_y + 70), (base_x + 100, base_y + 85), 3)
        if mistakes >= 5:  # Left leg
            pygame.draw.line(self.screen, color, (base_x + 80, base_y + 100), (base_x + 60, base_y + 130), 3)
        if mistakes >= 6:  # Right leg
            pygame.draw.line(self.screen, color, (base_x + 80, base_y + 100), (base_x + 100, base_y + 130), 3)

    def draw_word_display(self, display_word):
        text = self.font_large.render(display_word, True, theme.COLORS["accent"])
        width, height = self.screen.get_size()
        text_rect = text.get_rect(center=(width // 2, height // 2))
        self.screen.blit(text, text_rect)

    def draw_guessed_letters(self, guessed):
        text = self.font_small.render(f"Guessed: {' '.join(guessed) if guessed else 'None'}", True, theme.COLORS["text_dim"])
        width, height = self.screen.get_size()
        text_rect = text.get_rect(center=(width // 2, height // 2 + height // 10))
        self.screen.blit(text, text_rect)

    def draw_buttons(self, guessed):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_button = None
        
        for letter, rect in self.buttons.items():
            if letter in guessed:
                color = theme.COLORS["bg_medium"]
                text_color = theme.COLORS["text_dim"]
            elif rect.collidepoint(mouse_pos):
                color = theme.COLORS["button_hover"]
                text_color = theme.COLORS["accent"]
                self.hovered_button = letter
            else:
                color = theme.COLORS["button"]
                text_color = theme.COLORS["button_text"]
            
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, theme.COLORS["text_dim"], rect, 2, border_radius=5)
            
            text = self.font_small.render(letter, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    # Rendering/drawing the lives display on screen
    def draw_lives(self, lives, max_lives):
        if lives == 1:
            color = theme.COLORS["error"]
        elif lives == 2:
            color = theme.COLORS["orange"]
        elif lives == 3:
            color = theme.COLORS["yellow"]
        else:
            color = theme.COLORS["text_primary"]
        text = self.font_medium.render(f"Lives: {lives}/{max_lives}", True, color)
        text_rect = text.get_rect(topleft=(20, 20))
        self.screen.blit(text, text_rect)

    def draw_message(self):
        if self.message and pygame.time.get_ticks() <= self.message_end_time:
            text = self.font_medium.render(self.message, True, theme.COLORS["error"])
            text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, 560))
            self.screen.blit(text, text_rect)
        elif pygame.time.get_ticks() > self.message_end_time:
            self.message = ""

    def show_message(self, msg):
        self.message = msg
        self.message_end_time = pygame.time.get_ticks() + 1500
        self.flash_end_time = pygame.time.get_ticks() + 500

    def draw_game_over(self, won, secret):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(theme.COLORS["bg_dark"])
        self.screen.blit(overlay, (0, 0))
        
        if won:
            msg = "YOU WIN!"
            color = theme.COLORS["success"]
        else:
            msg = f"GAME OVER\nWord: {secret}"
            color = theme.COLORS["error"]
        
        lines = msg.split('\n')
        y_offset = s.SCREEN_HEIGHT // 2 - 150  # move message higher

        for line in lines:
            text = self.font_large.render(line, True, color)
            text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50

        # Reserve space for buttons (assume they are around mid-screen + 50)
        button_area_y = s.SCREEN_HEIGHT // 2 + 50

        prompt = self.font_medium.render("Press SPACE to play again", True, theme.COLORS["text_primary"])
        prompt_rect = prompt.get_rect(center=(s.SCREEN_WIDTH // 2, button_area_y // 2 + 80))
        self.screen.blit(prompt, prompt_rect)

    def draw(self, game_state, current_state=None, timer=0, high_score=0):
        self.screen.fill(theme.COLORS["bg_dark"])
        
        # Red flash overlay for incorrect guesses
        if pygame.time.get_ticks() <= self.flash_end_time:
            flash_surface = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            flash_surface.set_alpha(100)
            flash_surface.fill(theme.COLORS["error"])
            self.screen.blit(flash_surface, (0, 0))
        
        if game_state:
            self.draw_lives(game_state["lives"], game_state["max_lives"])
            self.draw_hangman(game_state["lives"], game_state["max_lives"])
            self.draw_word_display(game_state["display"])
            self.draw_guessed_letters(game_state["guessed"])
            self.draw_buttons(game_state["guessed"])
            self.draw_message()
            
            if game_state["game_over"]:
                self.draw_game_over(game_state["won"], game_state["secret"])
        
        # Draw timer and high score
        self.draw_timer(timer)
        self.draw_high_score(high_score)
        
        # Draw state-specific UI
        self.ui_buttons = []
        if current_state == GameState.GAMEPLAY.value:
            self.add_pause_button()
            self.add_hint_button()
        elif current_state == GameState.PAUSED.value:
            self.add_pause_menu_buttons()
        elif current_state == GameState.GAME_OVER.value:
            self.add_game_over_buttons()
        
        pygame.display.flip()
        self.clock.tick(s.FPS)

    def handle_events(self):
        self.message = ""
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.hovered_button:
                    return self.hovered_button
                for action, rect in self.ui_buttons:
                    if rect.collidepoint(event.pos):
                        # Missing statement in the button click handler
                        return action
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_SPACE:
                    return "space"
                if event.key == pygame.K_p:
                    return "pause"
                if event.key == pygame.K_h:
                    return "hint"
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_m:
                    return "main_menu"
                if event.unicode.isalpha():
                    return event.unicode.upper()
        
        return None

    def draw_timer(self, timer):
        timer_text = f"Time: {timer:.1f}s"
        text = self.font_small.render(timer_text, True, theme.COLORS["text_primary"])
        width, height = self.screen.get_size()
        self.screen.blit(text, (width // 2 - text.get_width() // 2, height // 50))
    
    def draw_high_score(self, high_score):
        if high_score > 0:
            hs_text = f"High Score: {high_score:.1f}s"
            text = self.font_small.render(hs_text, True, theme.COLORS["text_primary"])
            self.screen.blit(text, (s.SCREEN_WIDTH - text.get_width() - 10, 10))
    
    def add_pause_button(self):
        width, height = self.screen.get_size()
        rect = pygame.Rect(width - 100, 10, 80, 30)
        self.ui_buttons.append(("pause", rect))
        color = theme.COLORS["button_hover"] if rect.collidepoint(pygame.mouse.get_pos()) else theme.COLORS["button"]
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        text = self.font_small.render("Pause", True, theme.COLORS["button_text"])
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def add_hint_button(self):
        width, height = self.screen.get_size()
        rect = pygame.Rect(width - 100, height - 50, 80, 30)
        self.ui_buttons.append(("hint", rect))
        color = theme.COLORS["button_hover"] if rect.collidepoint(pygame.mouse.get_pos()) else theme.COLORS["button"]
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        text = self.font_small.render("Hint", True, theme.COLORS["button_text"])
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def add_pause_menu_buttons(self):
        # Darken background overlay
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        overlay.set_alpha(180)  # transparency (0 = fully transparent, 255 = fully opaque)
        overlay.fill((0, 0, 0))  # black overlay
        self.screen.blit(overlay, (0, 0))

        # PAUSED text
        pause_text = self.font_large.render("PAUSED", True, theme.COLORS["text_primary"])
        rect = pause_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(pause_text, rect)
        
        # buttons
        resume_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 - 50, 200, 45)
        restart_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2, 200, 45)
        menu_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 + 50, 200, 45)
        buttons = [("resume", resume_rect), ("restart", restart_rect), ("main_menu", menu_rect)]
        for action, rect in buttons:
            self.ui_buttons.append((action, rect))
            color = theme.COLORS["button_hover"] if rect.collidepoint(pygame.mouse.get_pos()) else theme.COLORS["button"]
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, theme.COLORS["accent"], rect, 2, border_radius=8)
            text = self.font_medium.render(action.replace('_', ' ').title(), True, theme.COLORS["button_text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def add_game_over_buttons(self):
        # buttons
        restart_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 + 50, 200, 45)
        menu_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 + 100, 200, 45)
        buttons = [("restart", restart_rect), ("main_menu", menu_rect)]
        for action, rect in buttons:
            self.ui_buttons.append((action, rect))
            color = theme.COLORS["button_hover"] if rect.collidepoint(pygame.mouse.get_pos()) else theme.COLORS["button"]
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, theme.COLORS["accent"], rect, 2, border_radius=8)
            text = self.font_medium.render(action.replace('_', ' ').title(), True, theme.COLORS["button_text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)