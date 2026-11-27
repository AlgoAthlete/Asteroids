import pygame # type: ignore
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ASTEROID_MIN_RADIUS
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
import sys
from shot import Shot
import json
import os

HIGHSCORE_FILE = "highscores.json"

def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        # Standardlista om ingen fil finns än
        return [("AAA", 100), ("BBB", 50), ("CCC", 20)]
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return [("AAA", 100), ("BBB", 50), ("CCC", 20)]

def save_highscores(scores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(scores, f)

def get_player_initials(screen, font, score):
    initials = ""
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "???"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(initials) > 0:
                    return initials
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalnum():
                    initials += event.unicode.upper()

        # Rita inmatningsskärmen
        screen.fill("black")
        title_surf = font.render("NEW HIGH SCORE!", True, "yellow")
        score_surf = font.render(f"Score: {score}", True, "white")
        prompt_surf = font.render(f"Enter Initials: {initials}_", True, "green")
        hint_surf = font.render("Press ENTER when done", True, "gray")

        screen.blit(title_surf, (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 80))
        screen.blit(score_surf, (SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT / 2 - 40))
        screen.blit(prompt_surf, (SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT / 2 + 10))
        screen.blit(hint_surf, (SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 + 50))

        pygame.display.flip()
        clock.tick(30)

def draw_highscores(screen, font, highscores, x, y):
    title = font.render("HIGH SCORES:", True, "gold")
    screen.blit(title, (x, y))
    for i, (name, sc) in enumerate(highscores):
        row = font.render(f"{i + 1}. {name} - {sc}", True, "white")
        screen.blit(row, (x, y + 25 * (i + 1)))

def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    lives = 3
    AsteroidField.containers = (updatable)
    Asteroid.containers = (asteroids, updatable, drawable)
    Player.containers = (updatable,drawable)
    Shot.containers = (shots,updatable,drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    field = AsteroidField()
    pygame.font.init()
    font = pygame.font.SysFont("monospace", 24)
    game_over_font = pygame.font.SysFont("monospace", 64, bold=True)
    score = 0
    highscores = load_highscores()
    
    while True:
        log_state()
        screen.fill("black") 
        field.score = score
        updatable.update(dt)
        for asteroid in asteroids:
             if player.collides_with(asteroid):
                lives -= 1
                asteroid.kill()

                if lives <= 0:
                    log_event("player_hit")
                    
                    # 1. Kolla om vi tog oss in på topp 3 (om listan har färre än 3 eller om score slår 3:an)
                    if len(highscores) < 3 or score > highscores[-1][1]:
                        name = get_player_initials(screen, font, score)
                        highscores.append([name, score])
                        # Sortera med högst poäng först
                        highscores.sort(key=lambda item: item[1], reverse=True)
                        # Behåll endast topp 3
                        highscores = highscores[:3]
                        save_highscores(highscores)

                    # 2. Rensa skärmen och visa Game Over + topplistan
                    screen.fill("black")
                    game_over_surface = game_over_font.render("GAME OVER", True, "red")
                    rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
                    screen.blit(game_over_surface, rect)
                    
                    # Rita den uppdaterade topplistan i mitten
                    draw_highscores(screen, font, highscores, SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2)
                    
                    pygame.display.flip()
                    pygame.time.delay(4000)
                    sys.exit()
                else: 
                    print(f"Liv kvar: {lives}")
                    player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    break
             for shot in shots: 
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    if asteroid.radius > ASTEROID_MIN_RADIUS * 2:
                        score += 20
                    elif asteroid.radius > ASTEROID_MIN_RADIUS:
                        score += 50
                    else: 
                        score += 100
                    asteroid.split()       
        
        for i in drawable:
             i.draw(screen)

        lives_text = "❤️" * lives
        lives_surface = font.render(f"Lives: {lives_text}", True, "red")
        screen.blit(lives_surface, (10, 20))
        draw_highscores(screen, font, highscores, 10, SCREEN_HEIGHT - 120)
        score_surface = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surface, (SCREEN_WIDTH - 200, 10))
        pygame.display.flip()
        dt=clock.tick(60) / 1000
        for event in pygame.event.get(): 
              if event.type == pygame.QUIT:
                   return
        
        
if __name__ == "__main__":


    
    main()
