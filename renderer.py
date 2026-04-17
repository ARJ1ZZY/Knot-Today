import pygame
import theme
import settings as s

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

    def _create_keyboard_buttons(self):
        buttons = {}
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rows = [letters[0:10], letters[10:20], letters[20:]]
        start_y = s.SCREEN_HEIGHT - 200
        
        for row_idx, row_letters in enumerate(rows):
            row_count = len(row_letters)
            row_width = row_count * s.BUTTON_WIDTH + (row_count - 1) * s.BUTTON_MARGIN
            row_start_x = (s.SCREEN_WIDTH - row_width) // 2
            y = start_y + row_idx * (s.BUTTON_HEIGHT + s.BUTTON_MARGIN)
            
            for col, letter in enumerate(row_letters):
                x = row_start_x + col * (s.BUTTON_WIDTH + s.BUTTON_MARGIN)
                buttons[letter] = pygame.Rect(x, y, s.BUTTON_WIDTH, s.BUTTON_HEIGHT)
        
        return buttons

    def draw_hangman(self, lives, max_lives):
        base_x = s.SCREEN_WIDTH // 2 - 40
        base_y = 120
        
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
        text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, 300))
        self.screen.blit(text, text_rect)

    def draw_guessed_letters(self, guessed):
        text = self.font_small.render(f"Guessed: {' '.join(guessed) if guessed else 'None'}", True, theme.COLORS["text_dim"])
        text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, 350))
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
        y_offset = s.SCREEN_HEIGHT // 2 - 40
        
        for line in lines:
            text = self.font_large.render(line, True, color)
            text_rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
        
        prompt = self.font_medium.render("Press SPACE to play again", True, theme.COLORS["text_primary"])
        prompt_rect = prompt.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(prompt, prompt_rect)

    def draw(self, game_state):
        self.screen.fill(theme.COLORS["bg_dark"])
        
        # Red flash overlay for incorrect guesses
        if pygame.time.get_ticks() <= self.flash_end_time:
            flash_surface = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            flash_surface.set_alpha(100)
            flash_surface.fill(theme.COLORS["error"])
            self.screen.blit(flash_surface, (0, 0))
        
        self.draw_lives(game_state["lives"], game_state["max_lives"])
        self.draw_hangman(game_state["lives"], game_state["max_lives"])
        self.draw_word_display(game_state["display"])
        self.draw_guessed_letters(game_state["guessed"])
        self.draw_buttons(game_state["guessed"])
        self.draw_message()
        
        if game_state["game_over"]:
            self.draw_game_over(game_state["won"], game_state["secret"])
        
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
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_SPACE:
                    return "space"
                if event.unicode.isalpha():
                    return event.unicode.upper()
        
        return None

    def show_message(self, msg):
        self.message = msg