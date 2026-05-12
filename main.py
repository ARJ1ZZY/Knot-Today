import pygame
import sys
from game_logic import HangmanGame
from renderer import PygameRenderer
from utils import get_random_word, load_word_bank
from game_state import StateManager, GameState
from sound_manager import SoundManager
import settings as s
import time

def show_category_menu(renderer):
    bank = load_word_bank()
    categories = list(bank.keys())
    
    font = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_MEDIUM)
    small_font = pygame.font.Font(s.FONT_NAME, s.FONT_SIZE_SMALL)
    
    buttons = []
    start_y = 200
    
    # Get the current window size dynamically
    width, height = renderer.screen.get_size()

    for i, cat in enumerate(categories):
        rect = pygame.Rect(width // 2 - 100, start_y + i * 60, 200, 45)
        buttons.append((rect, cat))
    
    random_rect = pygame.Rect(width // 2 - 100, start_y + len(categories) * 60, 200, 45)
    
    while True:
        renderer.screen.fill(theme.COLORS["bg_dark"])

        width, height = renderer.screen.get_size()
        
        title = renderer.font_large.render("KNOT-TODAY", True, theme.COLORS["accent"])
        title_rect = title.get_rect(center=(width // 2, 80))
        renderer.screen.blit(title, title_rect)
        
        subtitle = renderer.font_medium.render("Select A Theme", True, theme.COLORS["text_primary"])
        subtitle_rect = subtitle.get_rect(center=(width // 2, 140))
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
    pygame.init()
    screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.RESIZABLE)
    print(screen.get_size())
    pygame.display.set_caption("Knot-Today")
    
    renderer = PygameRenderer(screen)
    clock = pygame.time.Clock()
    state_manager = StateManager()
    sound_manager = SoundManager()
    
    running = True
    game = None
    start_time = 0
    paused_time = 0
    pause_start = 0
    high_score = 0  # Load from file if exists
    game_over_sound_played = False
    
    while running:
        if state_manager.get_state() == GameState.MAIN_MENU:
            category = show_category_menu(renderer)
            if category is not None:
                secret = get_random_word(category)
                game = HangmanGame(secret)
                start_time = time.time()
                paused_time = 0
                game_over_sound_played = False
                state_manager.change_state(GameState.GAMEPLAY)
            else:
                running = False
        
        elif state_manager.get_state() == GameState.GAMEPLAY:
            if game and not game.game_over:
                action = renderer.handle_events()
                
                if action == "quit":
                    running = False
                elif action == "pause":
                    pause_start = time.time()
                    state_manager.change_state(GameState.PAUSED)
                elif action == "hint":
                    # Implement hint logic
                    success, msg = game.hint()
                    sound_manager.play("correct" if success else "wrong")
                    renderer.show_message(msg)
                elif action and action.isalpha() and len(action) == 1:
                    success, msg = game.guess(action)
                    sound_manager.play("correct" if success else "wrong")
                    renderer.show_message(msg)
                
                renderer.draw(game.get_status(), state_manager.get_state().value, time.time() - start_time - paused_time, high_score)
            else:
                state_manager.change_state(GameState.GAME_OVER)
        
        elif state_manager.get_state() == GameState.PAUSED:
            action = renderer.handle_events()
            if action == "quit":
                running = False
            elif action == "resume":
                paused_time += time.time() - pause_start
                state_manager.change_state(GameState.GAMEPLAY)
            elif action == "restart":
                if game:
                    game.reset()
                    start_time = time.time()
                    paused_time = 0
                    game_over_sound_played = False
                    state_manager.change_state(GameState.GAMEPLAY)
            elif action == "main_menu":
                state_manager.change_state(GameState.MAIN_MENU)
            
            renderer.draw(game.get_status() if game else None, state_manager.get_state().value, time.time() - start_time - paused_time, high_score)
        
        elif state_manager.get_state() == GameState.GAME_OVER:
            if not game_over_sound_played:
                if game and game.won:
                    elapsed = time.time() - start_time - paused_time
                    if elapsed < high_score or high_score == 0:
                        high_score = elapsed
                    sound_manager.play("win")
                else:
                    sound_manager.play("lose")
                game_over_sound_played = True
            
            action = renderer.handle_events()
            if action == "quit":
                running = False
            elif action == "restart":
                if game:
                    game.reset()
                    start_time = time.time()
                    paused_time = 0
                    game_over_sound_played = False
                    state_manager.change_state(GameState.GAMEPLAY)
            elif action == "main_menu":
                state_manager.change_state(GameState.MAIN_MENU)
            
            renderer.draw(game.get_status(), state_manager.get_state().value, time.time() - start_time - paused_time, high_score)
        
        clock.tick(s.FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import theme
    main()