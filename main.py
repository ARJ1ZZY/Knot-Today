# main.py
import pygame
import sys
from game_logic import HangmanGame
from renderer import PygameRenderer
from game_state import GameState, StateManager
from utils import get_random_word, get_categories, load_high_score, save_high_score, ease_out_cubic, draw_glass_rect, clamp, clear_image_cache, get_cached_text
import settings as s
import theme

_font_cache = {}

def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]

def draw_main_menu(screen, high_score):
    categories = get_categories()
    
    font_huge = get_font(s.FONT_SIZE_HUGE)
    font_medium = get_font(s.FONT_SIZE_MEDIUM)
    font_small = get_font(s.FONT_SIZE_SMALL)
    
    buttons = []
    button_w = int(s.SCREEN_WIDTH * 0.25)
    button_h = int(s.SCREEN_HEIGHT * 0.065)
    start_y = int(s.SCREEN_HEIGHT * 0.32)
    spacing = int(s.SCREEN_HEIGHT * 0.085)
    
    for i, cat in enumerate(categories):
        rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + i * spacing, button_w, button_h)
        buttons.append((rect, cat))
        
    random_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + len(categories) * spacing + 20, button_w, button_h)
    
    clock = pygame.time.Clock()
    hover_progress = {cat: 0 for cat in categories}
    hover_progress["random"] = 0
    
    from utils import create_nebula_background
    bg = create_nebula_background(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
    
    title_text = get_cached_text(font_huge, "KNOT-TODAY", theme.COLORS["cyan_glow"])
    subtitle_text = get_cached_text(font_small, "Select Category", theme.COLORS["text_secondary"])
    
    while True:
        screen.blit(bg, (0, 0))
        
        title_rect = title_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.1)))
        screen.blit(title_text, title_rect)
        
        high_score_text = get_cached_text(font_medium, f"High Score: {high_score}", theme.COLORS["warning"])
        high_score_rect = high_score_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.2)))
        screen.blit(high_score_text, high_score_rect)
        
        subtitle_rect = subtitle_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.27)))
        screen.blit(subtitle_text, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for rect, cat in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            hover_progress[cat] += 0.12 if is_hover else -0.12
            hover_progress[cat] = clamp(hover_progress[cat], 0, 1)
            
            t = ease_out_cubic(hover_progress[cat])
            color = theme.COLORS["glass_light"] if t > 0.5 else theme.COLORS["glass_medium"]
            border = theme.COLORS["cyan_glow"] if t > 0.3 else theme.COLORS["glass_border"]
            
            scale = 1.0 + t * 0.03
            scaled_w = int(rect.width * scale)
            scaled_h = int(rect.height * scale)
            scaled_rect = pygame.Rect(rect.centerx - scaled_w//2, rect.centery - scaled_h//2, scaled_w, scaled_h)
            
            draw_glass_rect(screen, scaled_rect, color, 14, border_width=2, border_color=border)
            
            display_name = cat.replace('_', ' ').title()
            text = get_cached_text(font_small, display_name, theme.COLORS["text_primary"])
            text_rect = text.get_rect(center=scaled_rect.center)
            screen.blit(text, text_rect)
            
        is_hover = random_rect.collidepoint(mouse_pos)
        hover_progress["random"] += 0.12 if is_hover else -0.12
        hover_progress["random"] = clamp(hover_progress["random"], 0, 1)
        
        t = ease_out_cubic(hover_progress["random"])
        color = theme.COLORS["glass_light"] if t > 0.5 else theme.COLORS["glass_medium"]
        border = theme.COLORS["violet_glow"] if t > 0.3 else theme.COLORS["glass_border"]
        
        scale = 1.0 + t * 0.03
        scaled_w = int(random_rect.width * scale)
        scaled_h = int(random_rect.height * scale)
        scaled_rect = pygame.Rect(random_rect.centerx - scaled_w//2, random_rect.centery - scaled_h//2, scaled_w, scaled_h)
        
        draw_glass_rect(screen, scaled_rect, color, 14, border_width=2, border_color=border)
        
        text = get_cached_text(font_small, "Random", theme.COLORS["text_primary"])
        text_rect = text.get_rect(center=scaled_rect.center)
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(s.FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.VIDEORESIZE:
                return ("resize", event.w, event.h), None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                if event.key == pygame.K_F11:
                    return ("fullscreen",), None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, cat in buttons:
                    if rect.collidepoint(mouse_pos):
                        return cat, cat
                if random_rect.collidepoint(mouse_pos):
                    return None, "random"

def toggle_fullscreen():
    s.IS_FULLSCREEN = not s.IS_FULLSCREEN
    if s.IS_FULLSCREEN:
        info = pygame.display.Info()
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        s.SCREEN_WIDTH, s.SCREEN_HEIGHT = info.current_w, info.current_h
    else:
        screen = pygame.display.set_mode((s.BASE_WIDTH, s.BASE_HEIGHT), pygame.RESIZABLE)
        s.SCREEN_WIDTH, s.SCREEN_HEIGHT = s.BASE_WIDTH, s.BASE_HEIGHT
    
    s.update_font_sizes()
    _font_cache.clear()
    clear_image_cache()
    return screen

def handle_resize(width, height):
    """Handle window resize - update dimensions and clear caches"""
    s.SCREEN_WIDTH = width
    s.SCREEN_HEIGHT = height
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    s.update_font_sizes()
    _font_cache.clear()
    clear_image_cache()
    return screen

def main():
    screen = pygame.display.set_mode((s.BASE_WIDTH, s.BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Knot-Today · Midnight Nebula")
    
    state_manager = StateManager()
    renderer = PygameRenderer(screen)
    running = True
    paused = False
    
    high_score = load_high_score()
    game = None
    
    while running:
        if state_manager.get_state() == GameState.MAIN_MENU:
            result, mode = draw_main_menu(screen, high_score)
            
            if result is None and mode is None:
                break
            
            if isinstance(result, tuple) and result[0] == "resize":
                screen = handle_resize(result[1], result[2])
                renderer.screen = screen
                renderer.update_layout()
                continue
            elif isinstance(result, tuple) and result[0] == "fullscreen":
                screen = toggle_fullscreen()
                renderer.screen = screen
                renderer.update_layout()
                continue
                
            if mode == "random":
                secret, actual_category = get_random_word()
            else:
                result_word = get_random_word(result)
                if isinstance(result_word, tuple):
                    secret = result_word[0]
                else:
                    secret = result_word
            
            game = HangmanGame(secret)
            state_manager.change_state(GameState.GAMEPLAY)
            paused = False
            renderer.hangman_animation.reset()
            
        elif state_manager.get_state() == GameState.GAMEPLAY:
            action = renderer.handle_events(paused)
            
            if action == "quit":
                running = False
            elif isinstance(action, tuple) and action[0] == "resize":
                screen = handle_resize(action[1], action[2])
                renderer.screen = screen
                renderer.update_layout()
            elif action == "fullscreen":
                screen = toggle_fullscreen()
                renderer.screen = screen
                renderer.update_layout()
            elif action == "esc":
                state_manager.change_state(GameState.MAIN_MENU)
            elif action == "menu":
                paused = True
            elif action == "pause_resume":
                paused = False
            elif action == "pause_mute":
                renderer.sound_manager.toggle_mute()
            elif action == "pause_exit":
                state_manager.change_state(GameState.MAIN_MENU)
                paused = False
            elif not paused:
                if action == "hint":
                    if game.can_afford_hint():
                        hint_letter, msg = game.use_hint()
                        if hint_letter:
                            renderer.show_message(msg, is_error=False)
                            success, guess_msg, _ = game.guess(hint_letter)
                            if success:
                                renderer.show_message(guess_msg, is_error=False)
                            else:
                                renderer.show_message(guess_msg, is_error=True)
                        else:
                            renderer.show_message(msg, is_error=True)
                    else:
                        renderer.show_message(f"Need {game.hint_cost} points!", is_error=True)
                elif action and action.isalpha() and len(action) == 1:
                    if action not in game.guessed_letters:
                        success, msg, points = game.guess(action)
                        renderer.show_message(msg, is_error=not success)
            
            if not paused and game:
                if game.game_over:
                    if game.won and game.score > high_score:
                        high_score = game.score
                        save_high_score(high_score)
                    state_manager.change_state(GameState.GAME_OVER)
            
            if game:
                renderer.draw(game.get_status(), paused)
            else:
                renderer.draw({"lives": 6, "max_lives": 6, "guessed": [], "display": "", 
                              "game_over": False, "won": False, "score": 0, "streak": 0,
                              "hint_cost": 50, "can_afford_hint": True}, paused)
                
        elif state_manager.get_state() == GameState.GAME_OVER:
            waiting = True
            is_high_score = game.score >= high_score and game.won
            
            while waiting and running:
                action = renderer.handle_events()
                
                if action == "quit":
                    running = False
                    waiting = False
                elif isinstance(action, tuple) and action[0] == "resize":
                    screen = handle_resize(action[1], action[2])
                    renderer.screen = screen
                    renderer.update_layout()
                elif action == "fullscreen":
                    screen = toggle_fullscreen()
                    renderer.screen = screen
                    renderer.update_layout()
                elif action == "esc":
                    state_manager.change_state(GameState.MAIN_MENU)
                    waiting = False
                elif action == "space":
                    state_manager.change_state(GameState.MAIN_MENU)
                    waiting = False
                    
                game_status = game.get_status()
                game_status["is_high_score"] = is_high_score
                renderer.draw(game_status)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()