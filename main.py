"""Main entrypoint and controller for the Asteroids game."""

from __future__ import annotations

import sys

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import PLAYER_MAX_LIVES, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from repository import HighScoreRepository
from shot import Shot


class Game:
    """Main game controller and loop."""

    def __init__(self) -> None:
        """Initialize the game state, Pygame, and groups."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)

        self.repo = HighScoreRepository()

        self.state = "MENU"  # MENU, PLAYING, GAMEOVER
        self.score = 0
        self.lives = PLAYER_MAX_LIVES
        self.high_scores = self.repo.get_top_scores(3)
        self.init_game_objects()

    def init_game_objects(self) -> None:
        """Set up fresh game groups and entities for a new run."""
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.shots, self.updatable, self.drawable)

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroid_field = AsteroidField()
        self.score = 0
        self.lives = PLAYER_MAX_LIVES

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: str,
        x: float,
        y: float,
        center: bool = False,
    ) -> None:
        """Helper to draw text on the screen."""
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (int(x), int(y))
        else:
            rect.topleft = (int(x), int(y))
        self.screen.blit(surface, rect)

    def run(self) -> None:
        """Execute the main game loop."""
        dt: float = 0.0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    elif (
                        (self.state == "MENU" and event.key == pygame.K_SPACE)
                        or (self.state == "GAMEOVER" and event.key == pygame.K_r)
                    ):
                        self.state = "PLAYING"
                        self.init_game_objects()

            self.screen.fill("black")

            dt = self.clock.tick(60) / 1000

            if self.state == "MENU":
                self._run_menu()
            elif self.state == "PLAYING":
                self._run_playing(dt)
            elif self.state == "GAMEOVER":
                self._run_gameover()

            pygame.display.flip()

    def _run_menu(self) -> None:
        """Render the main menu."""
        self.draw_text(
            "ASTEROIDS",
            self.large_font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 3,
            center=True,
        )
        self.draw_text(
            "Press SPACE to Start",
            self.font,
            "gray",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            center=True,
        )

        # Draw high scores
        y_offset = SCREEN_HEIGHT * 0.6
        self.draw_text(
            "Top Scores:", self.font, "white", SCREEN_WIDTH / 2, y_offset, center=True
        )
        for i, score_record in enumerate(self.high_scores):
            y_offset += 40
            self.draw_text(
                f"{i + 1}. {score_record['score']}",
                self.font,
                "gray",
                SCREEN_WIDTH / 2,
                y_offset,
                center=True,
            )

    def draw_hearts(self, x: float, y: float, size: float = 12.0) -> None:
        """Render remaining lives as heart icons in the top HUD.

        Parameters
        ----------
        x : float
            Starting horizontal anchor coordinate.
        y : float
            Vertical anchor coordinate.
        size : float
            Scale radius of each heart lobe.
        """
        for i in range(PLAYER_MAX_LIVES):
            hx = x + i * (size * 2.8)
            hy = y

            # Heart geometry formed by two circles and an inverted triangle
            if i < self.lives:
                # Active red heart
                color = (255, 50, 70)
                pygame.draw.circle(self.screen, color, (int(hx - size * 0.5), int(hy)), int(size * 0.5))
                pygame.draw.circle(self.screen, color, (int(hx + size * 0.5), int(hy)), int(size * 0.5))
                triangle_pts = [
                    (hx - size * 1.0, hy + size * 0.1),
                    (hx + size * 1.0, hy + size * 0.1),
                    (hx, hy + size * 1.2),
                ]
                pygame.draw.polygon(self.screen, color, triangle_pts)
            else:
                # Lost / empty heart (dim outline)
                empty_color = (60, 65, 80)
                pygame.draw.circle(self.screen, empty_color, (int(hx - size * 0.5), int(hy)), int(size * 0.5), 2)
                pygame.draw.circle(self.screen, empty_color, (int(hx + size * 0.5), int(hy)), int(size * 0.5), 2)
                triangle_pts = [
                    (hx - size * 1.0, hy + size * 0.1),
                    (hx + size * 1.0, hy + size * 0.1),
                    (hx, hy + size * 1.2),
                ]
                pygame.draw.polygon(self.screen, empty_color, triangle_pts, 2)

    def _run_playing(self, dt: float) -> None:
        """Update and render the active game state."""
        log_state()
        self.updatable.update(dt)

        # Cull out of bounds shots to prevent memory leaks
        for shot in self.shots:
            if (
                shot.position.x < -100
                or shot.position.x > SCREEN_WIDTH + 100
                or shot.position.y < -100
                or shot.position.y > SCREEN_HEIGHT + 100
            ):
                shot.kill()

        for asteroid in self.asteroids:
            # Cull asteroids way out of bounds
            if (
                asteroid.position.x < -500
                or asteroid.position.x > SCREEN_WIDTH + 500
                or asteroid.position.y < -500
                or asteroid.position.y > SCREEN_HEIGHT + 500
            ):
                asteroid.kill()
                continue

            # Collision check with player (with invulnerability & damage flash)
            if not self.player.is_invulnerable and asteroid.collides_with(self.player):
                log_event("player_hit")
                self.lives -= 1
                self.player.trigger_hit()

                # Split the colliding asteroid
                asteroid.split()

                if self.lives <= 0:
                    self.repo.save_score(self.score)
                    self.high_scores = self.repo.get_top_scores(3)
                    self.state = "GAMEOVER"
                    break

            for shot in self.shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()
                    self.score += 10

        for draw in self.drawable:
            draw.draw(self.screen)

        # HUD: Score and Lives
        self.draw_text(f"Score: {self.score}", self.font, "white", 20, 20)
        self.draw_hearts(SCREEN_WIDTH - 140, 26, size=11.0)

    def _run_gameover(self) -> None:
        """Render the game over screen."""
        self.draw_text(
            "GAME OVER",
            self.large_font,
            "red",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 3,
            center=True,
        )
        self.draw_text(
            f"Final Score: {self.score}",
            self.font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            center=True,
        )
        self.draw_text(
            "Press 'R' to Restart",
            self.font,
            "gray",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.6,
            center=True,
        )

    def quit(self) -> None:
        """Gracefully exit the game."""
        pygame.quit()
        sys.exit()


def main() -> None:
    """Launch the Asteroids game."""
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
