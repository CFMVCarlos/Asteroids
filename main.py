"""Main entrypoint and controller for the Asteroids game."""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import PLAYER_MAX_LIVES, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from powerup import PowerUp
from repository import HighScoreRepository
from shot import Shot


class Game:
    """Main game controller and loop."""

    def __init__(self) -> None:
        """Initialize the game state, Pygame, and groups."""
        pygame.init()

        # Set game window icon and title before/at display creation
        icon_path = Path(__file__).parent / "assets" / "icon.png"
        if icon_path.exists():
            try:
                icon_surf = pygame.image.load(str(icon_path))
                pygame.display.set_icon(icon_surf)
            except pygame.error:
                log_event("icon_load_failed")

        pygame.display.set_caption("Asteroids - Space Combat", "Asteroids")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        self.badge_font = pygame.font.SysFont(None, 24, bold=True)

        self.repo = HighScoreRepository()

        self.state = "MENU"  # MENU, PLAYING, GAMEOVER
        self.score = 0
        self.lives = PLAYER_MAX_LIVES
        self.player_name = "Player"
        self.name_editing = True
        self.score_saved = False
        self.cursor_timer = 0.0
        self.emp_flash_timer = 0.0
        self.high_scores = self.repo.get_top_scores(5)
        self.init_game_objects()

    def init_game_objects(self) -> None:
        """Set up fresh game groups and entities for a new run."""
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.shots, self.updatable, self.drawable)
        PowerUp.containers = (self.powerups, self.updatable, self.drawable)

        # Wire asteroid tracking into Shot for homing missiles
        Shot.asteroid_target_group = self.asteroids

        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.asteroid_field = AsteroidField(asteroids_group=self.asteroids)
        self.score = 0
        self.lives = PLAYER_MAX_LIVES
        self.score_saved = False
        self.emp_flash_timer = 0.0

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: str | tuple[int, int, int] | pygame.Color,
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

    def trigger_emp_bomb(self) -> None:
        """Detonate screen-clearing EMP bomb."""
        self.emp_flash_timer = 0.25
        # Damage / destroy all asteroids currently in play
        asteroids_to_nuke = list(self.asteroids)
        for asteroid in asteroids_to_nuke:
            was_special = asteroid.is_special
            split_or_destroyed = asteroid.split()
            if split_or_destroyed:
                multiplier = 2 if self.player.score_multiplier_timer > 0.0 else 1
                self.score += (50 if was_special else 10) * multiplier
                if was_special:
                    PowerUp(asteroid.position.x, asteroid.position.y)

    def run(self) -> None:
        """Execute the main game loop."""
        dt: float = 0.0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.state in ("PLAYING", "PAUSED"):
                        # Toggle pause
                        self.state = "PAUSED" if self.state == "PLAYING" else "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING":
                            # In-game ESC pauses rather than abruptly quitting
                            self.state = "PAUSED"
                        elif self.state == "PAUSED":
                            self.quit()
                        else:
                            self.quit()
                    elif self.state == "PAUSED":
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            self.state = "PLAYING"
                    elif self.state == "MENU":
                        if event.key == pygame.K_RETURN:
                            # Start game with current pilot name
                            self.state = "PLAYING"
                            self.init_game_objects()
                        elif event.key == pygame.K_BACKSPACE:
                            if len(self.player_name) > 0:
                                self.player_name = self.player_name[:-1]
                        elif event.unicode:
                            char = event.unicode.upper()
                            # Allow alphanumeric, space, dash, underscore up to 18 characters
                            if (char.isalnum() or char in " -_") and len(
                                self.player_name
                            ) < 18:
                                self.player_name += char

                    elif self.state == "GAMEOVER" and event.key in (
                        pygame.K_RETURN,
                        pygame.K_r,
                    ):
                        # Replay game with saved pilot name
                        self.state = "PLAYING"
                        self.init_game_objects()

            self.screen.fill("black")

            dt = self.clock.tick(60) / 1000
            self.cursor_timer += dt

            if self.state == "MENU":
                self._run_menu()
            elif self.state == "PLAYING":
                self._run_playing(dt)
            elif self.state == "PAUSED":
                self._run_paused()
            elif self.state == "GAMEOVER":
                self._run_gameover()

            pygame.display.flip()

    def _run_menu(self) -> None:
        """Render the main menu with dedicated pilot name input."""
        self.draw_text(
            "ASTEROIDS",
            self.large_font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.16,
            center=True,
        )

        # Pilot Name Input Box
        box_y = SCREEN_HEIGHT * 0.28
        self.draw_text(
            "PILOT CALLSIGN (Type name, press ENTER to launch):",
            self.badge_font,
            (255, 215, 0),
            SCREEN_WIDTH / 2,
            box_y,
            center=True,
        )

        box_rect = pygame.Rect(0, 0, 380, 46)
        box_rect.center = (int(SCREEN_WIDTH / 2), int(box_y + 40))
        pygame.draw.rect(self.screen, (25, 30, 45), box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (0, 240, 160), box_rect, width=2, border_radius=8)

        # Render stable text (no jitter / horizontal shifting)
        text_surf = self.font.render(self.player_name, True, "white")
        text_rect = text_surf.get_rect(center=box_rect.center)
        self.screen.blit(text_surf, text_rect)

        # Only blink a cursor prompt if name is empty
        if not self.player_name and int(self.cursor_timer * 3) % 2 == 0:
            cursor_surf = self.font.render("_", True, (0, 240, 160))
            cursor_rect = cursor_surf.get_rect(center=box_rect.center)
            self.screen.blit(cursor_surf, cursor_rect)

        self.draw_text(
            "Press ENTER to Start Game  |  ESC to Quit",
            self.font,
            "gray",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.44,
            center=True,
        )

        self.draw_scoreboard(SCREEN_HEIGHT * 0.52)

    def draw_scoreboard(self, start_y: float) -> None:
        """Render top pilots scoreboard.

        Parameters
        ----------
        start_y : float
            Vertical starting coordinate for the scoreboard section.
        """
        self.draw_text(
            "TOP PILOTS SCOREBOARD",
            self.font,
            (255, 215, 0),
            SCREEN_WIDTH / 2,
            start_y,
            center=True,
        )
        y_offset = start_y + 15
        for i, score_record in enumerate(self.high_scores):
            y_offset += 34
            player_tag = score_record["player_name"].ljust(18)
            score_tag = str(score_record["score"]).rjust(6)
            self.draw_text(
                f"{i + 1}.  {player_tag}   {score_tag} PTS",
                self.font,
                "white" if i == 0 else "gray",
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
                pygame.draw.circle(
                    self.screen,
                    color,
                    (int(hx - size * 0.5), int(hy)),
                    int(size * 0.5),
                )
                pygame.draw.circle(
                    self.screen,
                    color,
                    (int(hx + size * 0.5), int(hy)),
                    int(size * 0.5),
                )
                triangle_pts = [
                    (hx - size * 1.0, hy + size * 0.1),
                    (hx + size * 1.0, hy + size * 0.1),
                    (hx, hy + size * 1.2),
                ]
                pygame.draw.polygon(self.screen, color, triangle_pts)
            else:
                # Lost / empty heart (dim outline)
                empty_color = (60, 65, 80)
                pygame.draw.circle(
                    self.screen,
                    empty_color,
                    (int(hx - size * 0.5), int(hy)),
                    int(size * 0.5),
                    2,
                )
                pygame.draw.circle(
                    self.screen,
                    empty_color,
                    (int(hx + size * 0.5), int(hy)),
                    int(size * 0.5),
                    2,
                )
                triangle_pts = [
                    (hx - size * 1.0, hy + size * 0.1),
                    (hx + size * 1.0, hy + size * 0.1),
                    (hx, hy + size * 1.2),
                ]
                pygame.draw.polygon(self.screen, empty_color, triangle_pts, 2)

    def _run_playing(self, dt: float) -> None:
        """Update and render the active game state."""
        log_state()

        # Handle time dilation slow-motion buff
        sim_dt = dt * 0.5 if self.player.slow_time_timer > 0.0 else dt

        # Update entities (Player runs on normal dt, world obstacles obey sim_dt)
        self.player.update(dt)
        for entity in self.updatable:
            if entity != self.player:
                entity.update(sim_dt)

        # Handle Magnet skill (attract power-ups towards player)
        if self.player.magnet_timer > 0.0:
            for powerup in self.powerups:
                diff = self.player.position - powerup.position
                dist = diff.length()
                if 0 < dist < 450:
                    attract_speed = 320.0
                    powerup.velocity = diff.normalize() * attract_speed

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
                    self.score_saved = False
                    # Auto-save score with chosen pilot name
                    name_to_save = self.player_name.strip() or "Player"
                    self.repo.save_score(self.score, name_to_save)
                    self.high_scores = self.repo.get_top_scores(5)
                    self.score_saved = True
                    self.state = "GAMEOVER"
                    break

            for shot in self.shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    shot.kill()
                    was_special = asteroid.is_special
                    split_or_destroyed = asteroid.split()
                    multiplier = 2 if self.player.score_multiplier_timer > 0.0 else 1
                    if split_or_destroyed:
                        self.score += (50 if was_special else 10) * multiplier
                        if was_special:
                            # Drop a random power-up collectible
                            PowerUp(asteroid.position.x, asteroid.position.y)
                    else:
                        # Non-fatal hit on special asteroid (progress HP)
                        self.score += 5 * multiplier

        # Check player collision with powerups
        for powerup in self.powerups:
            if self.player.collides_with(powerup):
                log_event("powerup_collected")
                if powerup.kind == "EMP_BOMB":
                    self.trigger_emp_bomb()
                else:
                    self.player.activate_powerup(powerup.kind)
                powerup.kill()

        # EMP screen shockwave effect
        if self.emp_flash_timer > 0.0:
            self.emp_flash_timer -= dt
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((255, 80, 80))
            flash_surf.set_alpha(int(150 * (self.emp_flash_timer / 0.25)))
            self.screen.blit(flash_surf, (0, 0))

        for draw in self.drawable:
            draw.draw(self.screen)

        # HUD: Score and Lives
        multiplier_tag = (
            " (2X PTS!)" if self.player.score_multiplier_timer > 0.0 else ""
        )
        self.draw_text(
            f"Score: {self.score}{multiplier_tag}", self.font, "white", 20, 20
        )
        self.draw_hearts(SCREEN_WIDTH - 140, 26, size=11.0)

        # HUD: Active Skill Countdown Badges
        badge_x = 20
        badge_y = 60
        active_badges: list[tuple[str, tuple[int, int, int]]] = []

        if self.player.triple_shot_timer > 0.0:
            active_badges.append(
                (f"TRIPLE SHOT {self.player.triple_shot_timer:.1f}s", (0, 240, 160))
            )
        if self.player.rapid_fire_timer > 0.0:
            active_badges.append(
                (f"RAPID FIRE {self.player.rapid_fire_timer:.1f}s", (255, 200, 40))
            )
        if self.player.invincible_skill_timer > 0.0:
            active_badges.append(
                (
                    f"INVINCIBLE {self.player.invincible_skill_timer:.1f}s",
                    (220, 80, 255),
                )
            )
        if self.player.homing_missiles_timer > 0.0:
            active_badges.append(
                (
                    f"HOMING MISSILES {self.player.homing_missiles_timer:.1f}s",
                    (80, 200, 255),
                )
            )
        if self.player.slow_time_timer > 0.0:
            active_badges.append(
                (f"SLOW TIME {self.player.slow_time_timer:.1f}s", (120, 240, 255))
            )
        if self.player.score_multiplier_timer > 0.0:
            active_badges.append(
                (f"2X SCORE {self.player.score_multiplier_timer:.1f}s", (255, 220, 90))
            )
        if self.player.magnet_timer > 0.0:
            active_badges.append(
                (f"MAGNET {self.player.magnet_timer:.1f}s", (255, 120, 200))
            )

        # Hyperspace Leap HUD badge
        if self.player.hyperspace_cooldown > 0.0:
            active_badges.append(
                (f"HYPERSPACE {self.player.hyperspace_cooldown:.1f}s", (140, 145, 160))
            )
        else:
            active_badges.append(("HYPERSPACE READY [S]", (100, 220, 255)))

        for text, color in active_badges:
            badge_surf = self.badge_font.render(text, True, color)
            bg_rect = badge_surf.get_rect(topleft=(badge_x, badge_y))
            pill_rect = bg_rect.inflate(14, 6)
            pygame.draw.rect(self.screen, (20, 25, 35), pill_rect, border_radius=6)
            pygame.draw.rect(self.screen, color, pill_rect, 1, border_radius=6)
            self.screen.blit(badge_surf, bg_rect)
            badge_y += 32

    def _run_paused(self) -> None:
        """Render frozen game state overlaid with pause menu."""
        # Draw all game entities in their frozen states
        for draw in self.drawable:
            draw.draw(self.screen)

        # HUD: Score and Lives
        multiplier_tag = (
            " (2X PTS!)" if self.player.score_multiplier_timer > 0.0 else ""
        )
        self.draw_text(
            f"Score: {self.score}{multiplier_tag}", self.font, "white", 20, 20
        )
        self.draw_hearts(SCREEN_WIDTH - 140, 26, size=11.0)

        # Translucent dark backdrop tint
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dim_surf.fill((0, 0, 0))
        dim_surf.set_alpha(150)
        self.screen.blit(dim_surf, (0, 0))

        # Pause modal banner
        modal_rect = pygame.Rect(0, 0, 520, 220)
        modal_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2))
        pygame.draw.rect(self.screen, (20, 25, 40), modal_rect, border_radius=12)
        pygame.draw.rect(
            self.screen, (0, 240, 160), modal_rect, width=2, border_radius=12
        )

        self.draw_text(
            "GAME PAUSED",
            self.large_font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 50,
            center=True,
        )
        self.draw_text(
            "Press 'P', 'SPACE', or 'ENTER' to Resume",
            self.font,
            (0, 240, 160),
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 10,
            center=True,
        )
        self.draw_text(
            "Press 'ESC' to Quit",
            self.font,
            "gray",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 55,
            center=True,
        )

    def _run_gameover(self) -> None:
        """Render the game over screen with full leaderboard."""
        self.draw_text(
            "GAME OVER",
            self.large_font,
            "red",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.12,
            center=True,
        )
        self.draw_text(
            f"Final Score: {self.score}   |   Pilot: {self.player_name}",
            self.font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.22,
            center=True,
        )

        self.draw_text(
            "Score recorded to Leaderboard!",
            self.badge_font,
            (100, 255, 120),
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.28,
            center=True,
        )

        # Leaderboard in center/lower screen
        self.draw_scoreboard(SCREEN_HEIGHT * 0.35)

        self.draw_text(
            "Press 'ENTER' or 'R' to Play Again  |  ESC to Quit",
            self.font,
            "white",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT * 0.88,
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
