# main.py
import pygame
import sys
import math
from game_logic import HangmanGame
from renderer import PygameRenderer
from game_state import GameState, StateManager
from utils import get_random_word, get_categories, load_high_score, save_high_score, ease_out_cubic, clamp, clear_image_cache, get_cached_text, create_warm_background
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
    font_tiny = get_font(s.FONT_SIZE_TINY)
    
    buttons = []
    button_w = int(s.SCREEN_WIDTH * 0.25)
    button_h = int(s.SCREEN_HEIGHT * 0.07)
    start_y = int(s.SCREEN_HEIGHT * 0.32)
    spacing = int(s.SCREEN_HEIGHT * 0.085)
    
    for i, cat in enumerate(categories):
        rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + i * spacing, button_w, button_h)
        buttons.append((rect, cat))
        
    random_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + len(categories) * spacing + 15, button_w, button_h)
    
    clock = pygame.time.Clock()
    hover_progress = {cat: 0 for cat in categories}
    hover_progress["random"] = 0
    
    bg = create_warm_background(s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
    
    float_phase = 0
    
    while True:
        screen.blit(bg, (0, 0))
        
        float_phase += 0.008
        
        title_text = get_cached_text(font_huge, "KNOT-TODAY", theme.COLORS["accent_primary"])
        title_rect = title_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.1) + int(math.sin(float_phase) * 3)))
        screen.blit(title_text, title_rect)
        
        high_score_text = get_cached_text(font_medium, f"HIGH SCORE: {high_score}", theme.COLORS["warning"])
        high_score_rect = high_score_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.2)))
        screen.blit(high_score_text, high_score_rect)
        
        subtitle_text = get_cached_text(font_small, "SELECT CATEGORY", theme.COLORS["text_secondary"])
        subtitle_rect = subtitle_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.27)))
        screen.blit(subtitle_text, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for rect, cat in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            hover_progress[cat] += 0.12 if is_hover else -0.12
            hover_progress[cat] = clamp(hover_progress[cat], 0, 1)
            
            t = ease_out_cubic(hover_progress[cat])
            color = theme.COLORS["glass_light"] if t > 0.5 else theme.COLORS["glass_warm"]
            border = theme.COLORS["accent_primary"] if t > 0.3 else theme.COLORS["glass_border"]
            
            scale = 1.0 + t * 0.03
            scaled_w = int(rect.width * scale)
            scaled_h = int(rect.height * scale)
            scaled_rect = pygame.Rect(rect.centerx - scaled_w//2, rect.centery - scaled_h//2, scaled_w, scaled_h)
            
            from utils import draw_glass_rect
            draw_glass_rect(screen, scaled_rect, color, 14, border_width=2, border_color=border)
            
            display_name = cat.replace('_', ' ').title()
            text = get_cached_text(font_small, display_name, theme.COLORS["text_primary"])
            text_rect = text.get_rect(center=scaled_rect.center)
            screen.blit(text, text_rect)
            
        is_hover = random_rect.collidepoint(mouse_pos)
        hover_progress["random"] += 0.12 if is_hover else -0.12
        hover_progress["random"] = clamp(hover_progress["random"], 0, 1)
        
        t = ease_out_cubic(hover_progress["random"])
        color = theme.COLORS["glass_light"] if t > 0.5 else theme.COLORS["glass_warm"]
        border = theme.COLORS["accent_secondary"] if t > 0.3 else theme.COLORS["glass_border"]
        
        scale = 1.0 + t * 0.03
        scaled_w = int(random_rect.width * scale)
        scaled_h = int(random_rect.height * scale)
        scaled_rect = pygame.Rect(random_rect.centerx - scaled_w//2, random_rect.centery - scaled_h//2, scaled_w, scaled_h)
        
        draw_glass_rect(screen, scaled_rect, color, 14, border_width=2, border_color=border)
        
        text = get_cached_text(font_small, "RANDOM", theme.COLORS["text_primary"])
        text_rect = text.get_rect(center=scaled_rect.center)
        screen.blit(text, text_rect)
        
        controls_text = get_cached_text(font_tiny, "ESC: EXIT  |  F11: FULLSCREEN", theme.COLORS["text_muted"])
        controls_rect = controls_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT - 30))
        screen.blit(controls_text, controls_rect)
        
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
    s.SCREEN_WIDTH = width
    s.SCREEN_HEIGHT = height
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    s.update_font_sizes()
    _font_cache.clear()
    clear_image_cache()
    return screen

def main():
    pygame.display.set_caption("KNOT-TODAY")
    
    screen = pygame.display.set_mode((s.BASE_WIDTH, s.BASE_HEIGHT), pygame.RESIZABLE)
    
    state_manager = StateManager()
    renderer = PygameRenderer(screen)
    running = True
    paused = False
    
    high_score = load_high_score()
    game = None
    current_category = None
    
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
                secret, current_category = get_random_word()
            else:
                secret, current_category = get_random_word(result)
            
            game = HangmanGame(secret, current_category)
            state_manager.change_state(GameState.GAMEPLAY)
            paused = False
            renderer.hangman_animation.reset()
            renderer.floating_texts.clear()
            renderer.particles.clear()
            
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
                            renderer.sound_manager.play("hint")
                            success, guess_msg, points, positions = game.guess(hint_letter)
                            if success:
                                renderer.show_message(guess_msg, is_error=False)
                                center_x = s.SCREEN_WIDTH // 2
                                center_y = int(s.SCREEN_HEIGHT * 0.54)
                                renderer.on_correct_guess(points, center_x, center_y)
                            else:
                                renderer.show_message(guess_msg, is_error=True)
                        else:
                            renderer.show_message(msg, is_error=True)
                    else:
                        renderer.show_message(f"NEED {game.hint_cost} POINTS", is_error=True)
                elif action and action.isalpha() and len(action) == 1:
                    if action not in game.guessed_letters:
                        success, msg, points, positions = game.guess(action)
                        renderer.show_message(msg, is_error=not success)
                        if success:
                            if positions:
                                center_x = s.SCREEN_WIDTH // 2
                                center_y = int(s.SCREEN_HEIGHT * 0.54)
                                renderer.on_correct_guess(points, center_x, center_y)
                        else:
                            if action in renderer.buttons:
                                btn_rect = renderer.buttons[action]
                                renderer.on_wrong_guess(btn_rect.centerx, btn_rect.centery)
            
            if not paused and game:
                if game.game_over:
                    if game.won and game.score > high_score:
                        high_score = game.score
                        save_high_score(high_score)
                    if game.won:
                        renderer.sound_manager.play("win")
                    else:
                        renderer.sound_manager.play("lose")
                    
                    waiting = True
                    while waiting and running:
                        play_again_rect, main_menu_rect, card_x, card_y = renderer.draw_end_screen(
                            game.won, game.secret, game.score, game.score >= high_score and game.won
                        )
                        
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                waiting = False
                            elif event.type == pygame.VIDEORESIZE:
                                screen = handle_resize(event.w, event.h)
                                renderer.screen = screen
                                renderer.update_layout()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    state_manager.change_state(GameState.MAIN_MENU)
                                    waiting = False
                                elif event.key == pygame.K_SPACE:
                                    secret, current_category = get_random_word(current_category) if current_category else get_random_word()
                                    game = HangmanGame(secret, current_category)
                                    renderer.hangman_animation.reset()
                                    renderer.floating_texts.clear()
                                    renderer.particles.clear()
                                    waiting = False
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                mouse_x, mouse_y = event.pos
                                adj_x = mouse_x - card_x
                                adj_y = mouse_y - card_y
                                if play_again_rect.collidepoint(adj_x, adj_y):
                                    secret, current_category = get_random_word(current_category) if current_category else get_random_word()
                                    game = HangmanGame(secret, current_category)
                                    renderer.hangman_animation.reset()
                                    renderer.floating_texts.clear()
                                    renderer.particles.clear()
                                    waiting = False
                                elif main_menu_rect.collidepoint(adj_x, adj_y):
                                    state_manager.change_state(GameState.MAIN_MENU)
                                    waiting = False
                        
                        pygame.display.flip()
                        renderer.clock.tick(s.FPS)
            
            if game and not game.game_over:
                renderer.draw(game.get_status(), paused)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()