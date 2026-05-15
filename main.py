# main.py
import pygame
import sys
import math
from game_logic import HangmanGame
from renderer import PygameRenderer
from utils import get_random_word, get_categories, load_high_score, save_high_score, ease_out_cubic, clamp, clear_image_cache, get_cached_text
import settings as s
import theme

_font_cache = {}

def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]

def draw_main_menu(screen, high_score, renderer):
    categories = get_categories()
    
    font_huge = get_font(s.FONT_SIZE_HUGE)
    font_medium = get_font(s.FONT_SIZE_MEDIUM)
    font_small = get_font(s.FONT_SIZE_SMALL)
    font_tiny = get_font(s.FONT_SIZE_TINY)
    
    buttons = []
    button_w = int(s.SCREEN_WIDTH * 0.22)
    button_h = int(s.SCREEN_HEIGHT * 0.07)
    start_y = int(s.SCREEN_HEIGHT * 0.38)
    spacing = int(s.SCREEN_HEIGHT * 0.09)
    
    for i, cat in enumerate(categories):
        rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + i * spacing, button_w, button_h)
        buttons.append((rect, cat))
        
    random_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - button_w//2, start_y + len(categories) * spacing + 15, button_w, button_h)
    
    clock = pygame.time.Clock()
    hover_progress = {cat: 0 for cat in categories}
    hover_progress["random"] = 0
    
    # Original background
    bg = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
    bg.fill(theme.COLORS["bg_primary"])
    
    grid_size = 64
    for x in range(0, s.SCREEN_WIDTH, grid_size):
        for y in range(0, s.SCREEN_HEIGHT, grid_size):
            if (x // grid_size + y // grid_size) % 2 == 0:
                pygame.draw.rect(bg, theme.COLORS["bg_secondary"], (x, y, grid_size, grid_size))
    
    float_phase = 0
    last_hovered_button = None
    
    while True:
        screen.blit(bg, (0, 0))
        
        float_phase += 0.008
        
        title_text = get_cached_text(font_huge, "KNOT-TODAY", theme.COLORS["accent_primary"])
        title_rect = title_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.15) + int(math.sin(float_phase) * 2)))
        outline_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for ox, oy in outline_offsets:
            outline_text = get_cached_text(font_huge, "KNOT-TODAY", theme.COLORS["border_dark"])
            outline_rect = outline_text.get_rect(center=(title_rect.centerx + ox, title_rect.centery + oy))
            screen.blit(outline_text, outline_rect)
        screen.blit(title_text, title_rect)
        
        high_score_text = get_cached_text(font_medium, f"HIGH SCORE: {high_score}", theme.COLORS["warning"])
        high_score_rect = high_score_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.26)))
        screen.blit(high_score_text, high_score_rect)
        
        subtitle_text = get_cached_text(font_small, "SELECT CATEGORY", theme.COLORS["text_secondary"])
        subtitle_rect = subtitle_text.get_rect(center=(s.SCREEN_WIDTH // 2, int(s.SCREEN_HEIGHT * 0.33)))
        screen.blit(subtitle_text, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for rect, cat in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            hover_progress[cat] += 0.12 if is_hover else -0.12
            hover_progress[cat] = clamp(hover_progress[cat], 0, 1)
            
            t = ease_out_cubic(hover_progress[cat])
            color = theme.COLORS["accent_hover"] if t > 0.5 else theme.COLORS["key_normal"]
            border = theme.COLORS["accent_primary"] if t > 0.3 else theme.COLORS["border_light"]
            
            if is_hover and last_hovered_button != cat:
                renderer.sound_manager.play_sfx("hover")
                last_hovered_button = cat
            elif not is_hover and last_hovered_button == cat:
                last_hovered_button = None
            
            scale = 1.0 + t * 0.02
            scaled_w = int(rect.width * scale)
            scaled_h = int(rect.height * scale)
            scaled_rect = pygame.Rect(rect.centerx - scaled_w//2, rect.centery - scaled_h//2, scaled_w, scaled_h)
            
            pygame.draw.rect(screen, color, scaled_rect)
            pygame.draw.rect(screen, border, scaled_rect, 2)
            
            display_name = cat.replace('_', ' ').title()
            text = get_cached_text(font_small, display_name, theme.COLORS["text_primary"])
            text_rect = text.get_rect(center=scaled_rect.center)
            screen.blit(text, text_rect)
            
        is_hover = random_rect.collidepoint(mouse_pos)
        hover_progress["random"] += 0.12 if is_hover else -0.12
        hover_progress["random"] = clamp(hover_progress["random"], 0, 1)
        
        t = ease_out_cubic(hover_progress["random"])
        color = theme.COLORS["accent_hover"] if t > 0.5 else theme.COLORS["key_normal"]
        border = theme.COLORS["accent_secondary"] if t > 0.3 else theme.COLORS["border_light"]
        
        if is_hover and last_hovered_button != "random":
            renderer.sound_manager.play_sfx("hover")
            last_hovered_button = "random"
        elif not is_hover and last_hovered_button == "random":
            last_hovered_button = None
        
        scale = 1.0 + t * 0.02
        scaled_w = int(random_rect.width * scale)
        scaled_h = int(random_rect.height * scale)
        scaled_rect = pygame.Rect(random_rect.centerx - scaled_w//2, random_rect.centery - scaled_h//2, scaled_w, scaled_h)
        
        pygame.draw.rect(screen, color, scaled_rect)
        pygame.draw.rect(screen, border, scaled_rect, 2)
        
        text = get_cached_text(font_small, "RANDOM", theme.COLORS["text_primary"])
        text_rect = text.get_rect(center=scaled_rect.center)
        screen.blit(text, text_rect)
        
        controls_text = get_cached_text(font_tiny, "ESC:EXIT  |  F11:FULLSCREEN", theme.COLORS["text_muted"])
        controls_rect = controls_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT - 25))
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
                        renderer.sound_manager.play_sfx("hover")
                        return cat, cat
                if random_rect.collidepoint(mouse_pos):
                    renderer.sound_manager.play_sfx("hover")
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

def show_end_screen(renderer, game, high_score, current_category):
    secret_word = game.secret_word
    is_high_score = game.won and game.score >= high_score
    waiting = True
    
    renderer.sound_manager.stop_music()
    
    if game.won:
        renderer.sound_manager.play_sfx("win")
    else:
        renderer.sound_manager.play_sfx("lose")
    
    while waiting:
        play_again_rect, main_menu_rect, card_x, card_y = renderer.draw_end_screen(
            game.won, secret_word, game.score, is_high_score
        )
        pygame.display.flip()
        renderer.clock.tick(s.FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.VIDEORESIZE:
                new_screen = handle_resize(event.w, event.h)
                renderer.screen = new_screen
                renderer.update_layout()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    renderer.sound_manager.play_sfx("hover")
                    return "menu"
                if event.key == pygame.K_SPACE:
                    renderer.sound_manager.play_sfx("hover")
                    return "play_again"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if play_again_rect.collidepoint(mouse_x, mouse_y):
                    renderer.sound_manager.play_sfx("hover")
                    return "play_again"
                if main_menu_rect.collidepoint(mouse_x, mouse_y):
                    renderer.sound_manager.play_sfx("hover")
                    return "menu"
    
    return "menu"

def main():
    pygame.display.set_caption("KNOT-TODAY - 8-BIT EDITION")
    
    screen = pygame.display.set_mode((s.BASE_WIDTH, s.BASE_HEIGHT), pygame.RESIZABLE)
    
    renderer = PygameRenderer(screen)
    high_score = load_high_score()
    
    renderer.sound_manager.play_music("soundtrack", loop=True)
    
    game = None
    current_category = None
    running = True
    
    while running:
        if game is None:
            result, mode = draw_main_menu(screen, high_score, renderer)
            
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
            renderer.hangman_animation.reset()
            renderer.floating_texts.clear()
            renderer.particles.clear()
            
            renderer.sound_manager.play_music("soundtrack", loop=True)
        
        while game is not None and not game.game_over and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game = None
                elif event.type == pygame.VIDEORESIZE:
                    screen = handle_resize(event.w, event.h)
                    renderer.screen = screen
                    renderer.update_layout()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game = None
                    elif event.key == pygame.K_F11:
                        screen = toggle_fullscreen()
                        renderer.screen = screen
                        renderer.update_layout()
                    elif event.unicode.isalpha():
                        letter = event.unicode.upper()
                        if letter not in game.guessed_letters:
                            success, msg, points, _ = game.guess(letter, is_hint_guess=False)
                            renderer.show_message(msg, is_error=not success)
                            if success and points > 0:
                                center_x = s.SCREEN_WIDTH // 2
                                center_y = int(s.SCREEN_HEIGHT * 0.48)
                                renderer.on_correct_guess(points, center_x, center_y)
                            elif not success:
                                if letter in renderer.buttons:
                                    btn_rect = renderer.buttons[letter]
                                    renderer.on_wrong_guess(btn_rect.centerx, btn_rect.centery)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for letter, rect in renderer.buttons.items():
                        if rect.collidepoint(event.pos) and letter not in game.guessed_letters:
                            success, msg, points, _ = game.guess(letter, is_hint_guess=False)
                            renderer.show_message(msg, is_error=not success)
                            if success and points > 0:
                                center_x = s.SCREEN_WIDTH // 2
                                center_y = int(s.SCREEN_HEIGHT * 0.48)
                                renderer.on_correct_guess(points, center_x, center_y)
                            elif not success:
                                renderer.on_wrong_guess(rect.centerx, rect.centery)
                            break
                    
                    hint_button_rect = pygame.Rect(
                        s.SCREEN_WIDTH - 85, 190, 70, 35
                    )
                    if hint_button_rect.collidepoint(event.pos):
                        if game.can_afford_hint():
                            renderer.sound_manager.play_sfx("hint")
                            hint_letter, msg = game.use_hint()
                            if hint_letter:
                                renderer.show_message(msg, is_error=False)
                                success, guess_msg, points, _ = game.guess(hint_letter, is_hint_guess=True)
                                if success:
                                    renderer.show_message(f"REVEALED: {hint_letter}", is_error=False)
                                else:
                                    renderer.show_message(guess_msg, is_error=True)
                            else:
                                renderer.show_message(msg, is_error=True)
                        else:
                            renderer.show_message(f"NEED {game.hint_cost} PTS", is_error=True)
                    
                    menu_button_rect = pygame.Rect(
                        s.SCREEN_WIDTH - 85, 145, 70, 35
                    )
                    if menu_button_rect.collidepoint(event.pos):
                        renderer.sound_manager.play_sfx("hover")
                        game = None
                        break
            
            if game and game.game_over:
                if game.won and game.score > high_score:
                    high_score = game.score
                    save_high_score(high_score)
                break
            
            if game and not game.game_over:
                renderer.draw(game.get_status(), paused=False)
        
        if game is not None and game.game_over and running:
            choice = show_end_screen(renderer, game, high_score, current_category)
            
            if choice == "play_again":
                if current_category:
                    secret, current_category = get_random_word(current_category)
                else:
                    secret, current_category = get_random_word()
                game = HangmanGame(secret, current_category)
                renderer.hangman_animation.reset()
                renderer.floating_texts.clear()
                renderer.particles.clear()
                renderer.sound_manager.play_music("soundtrack", loop=True)
                continue
            elif choice == "menu":
                game = None
                renderer.sound_manager.play_music("soundtrack", loop=True)
                continue
            elif choice == "quit":
                running = False
                break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()