import pygame
import sys
from game_logic import HangmanGame
from renderer import PygameRenderer
from utils import get_random_word, load_word_bank
import settings as s

def show_category_menu(renderer):
    bank = load_word_bank()
    categories = list(bank.keys())
    
    font = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_MEDIUM)
    small_font = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_SMALL)
    
    buttons = []
    start_y = 200
    
    for i, cat in enumerate(categories):
        rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, start_y + i * 60, 200, 45)
        buttons.append((rect, cat))
    
    random_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, start_y + len(categories) * 60, 200, 45)
    
    while True:
        renderer.screen.fill(theme.COLORS["bg_dark"])
        
        title = renderer.font_large.render("KNOT-TODAY", True, theme.COLORS["accent"])
        title_rect = title.get_rect(center=(s.SCREEN_WIDTH // 2, 80))
        renderer.screen.blit(title, title_rect)
        
        subtitle = renderer.font_medium.render("Select Category", True, theme.COLORS["text_primary"])
        subtitle_rect = subtitle.get_rect(center=(s.SCREEN_WIDTH // 2, 140))
        renderer.screen.blit(subtitle, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for rect, cat in buttons:
            color = theme.COLORS["button_hover"] if rect.collidepoint(mouse_pos) else theme.COLORS["button"]
            pygame.draw.rect(renderer.screen, color, rect, border_radius=8)
            pygame.draw.rect(renderer.screen, theme.COLORS["accent"], rect, 2, border_radius=8)
            
            text = small_font.render(cat.replace('_', ' ').title(), True, theme.COLORS["button_text"])
            text_rect = text.get_rect(center=rect.center)
            renderer.screen.blit(text, text_rect)
        
        color = theme.COLORS["button_hover"] if random_rect.collidepoint(mouse_pos) else theme.COLORS["button"]
        pygame.draw.rect(renderer.screen, color, random_rect, border_radius=8)
        pygame.draw.rect(renderer.screen, theme.COLORS["accent"], random_rect, 2, border_radius=8)
        
        text = small_font.render("Random", True, theme.COLORS["button_text"])
        text_rect = text.get_rect(center=random_rect.center)
        renderer.screen.blit(text, text_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, cat in buttons:
                    if rect.collidepoint(mouse_pos):
                        return cat
                if random_rect.collidepoint(mouse_pos):
                    return None

def main():
    screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
    pygame.display.set_caption("Knot-Today")
    
    renderer = PygameRenderer(screen)
    clock = pygame.time.Clock()
    
    running = True
    
    while running:
        category = show_category_menu(renderer)
        if category is None and not pygame.get_init():
            break
        
        secret = get_random_word(category)
        game = HangmanGame(secret)
        
        while not game.game_over:
            action = renderer.handle_events()
            
            if action == "quit":
                running = False
                break
            elif action and action.isalpha() and len(action) == 1:
                success, msg = game.guess(action)
                if not success:
                    renderer.show_message(msg)
            
            renderer.draw(game.get_status())
        
        if not running:
            break
        
        # Game over - wait for space
        waiting = True
        while waiting and running:
            action = renderer.handle_events()
            if action == "quit":
                running = False
                waiting = False
            elif action == "space":
                waiting = False
            
            renderer.draw(game.get_status())
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import theme
    main()