"""Power-up collectible entity module for Asteroids."""

from __future__ import annotations

import math
import random
from typing import ClassVar, Literal

import pygame

from .circleshape import CircleShape
from .constants import (
    LINE_WIDTH,
    POWERUP_LIFETIME_SECONDS,
    POWERUP_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

PowerUpType = Literal[
    "TRIPLE_SHOT",
    "RAPID_FIRE",
    "INVINCIBILITY",
    "EMP_BOMB",
    "HOMING_MISSILES",
    "SLOW_TIME",
    "SCORE_MULTIPLIER",
    "MAGNET",
]

ALL_POWERUP_TYPES: list[PowerUpType] = [
    "TRIPLE_SHOT",
    "RAPID_FIRE",
    "INVINCIBILITY",
    "EMP_BOMB",
    "HOMING_MISSILES",
    "SLOW_TIME",
    "SCORE_MULTIPLIER",
    "MAGNET",
]


class PowerUp(CircleShape):
    """Floating collectible skill dropped by special asteroids.

    Parameters
    ----------
    x : float
        Initial horizontal position on the screen.
    y : float
        Initial vertical position on the screen.
    kind : PowerUpType | None
        The specific skill grant awarded when collected.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: float, y: float, kind: PowerUpType | None = None) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        if kind is None:
            self.kind: PowerUpType = random.choice(ALL_POWERUP_TYPES)
        else:
            self.kind = kind

        # Subtle drift velocity
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * random.uniform(15, 35)

        self.lifetime = POWERUP_LIFETIME_SECONDS
        self.max_lifetime = POWERUP_LIFETIME_SECONDS
        self.pulse_timer = 0.0

    def update(self, dt: float) -> None:
        """Update floating position, pulsating animation, and lifetime decay.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.position += self.velocity * dt
        self.pulse_timer += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        # Screen wrap-around like the player so power-ups stay in play during lifetime
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    def draw(self, screen: pygame.Surface) -> None:
        """Render glowing pulsating orb with unique icon and color badge.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        # Fade or blink when expiring in last 3 seconds
        if self.lifetime < 3.0 and int(self.pulse_timer * 8) % 2 == 1:
            return

        pulse = (math.sin(self.pulse_timer * 6.0) + 1.0) * 0.5
        glow_rad = int(self.radius + 3 + pulse * 4)

        if self.kind == "TRIPLE_SHOT":
            core_color = (0, 240, 160)
            glow_color = (0, 120, 80)
            label = "3X"
        elif self.kind == "RAPID_FIRE":
            core_color = (255, 200, 40)
            glow_color = (140, 100, 20)
            label = "RF"
        elif self.kind == "INVINCIBILITY":
            core_color = (220, 80, 255)
            glow_color = (110, 40, 140)
            label = "★"
        elif self.kind == "EMP_BOMB":
            core_color = (255, 60, 60)
            glow_color = (160, 20, 20)
            label = "EMP"
        elif self.kind == "HOMING_MISSILES":
            core_color = (80, 200, 255)
            glow_color = (20, 90, 150)
            label = "HM"
        elif self.kind == "SLOW_TIME":
            core_color = (120, 240, 255)
            glow_color = (30, 110, 140)
            label = "SLOW"
        elif self.kind == "SCORE_MULTIPLIER":
            core_color = (255, 220, 90)
            glow_color = (160, 130, 20)
            label = "2X"
        elif self.kind == "MAGNET":
            core_color = (255, 120, 200)
            glow_color = (140, 40, 90)
            label = "MAG"
        else:
            core_color = (255, 255, 255)
            glow_color = (100, 100, 100)
            label = "?"

        # Outer energy halo
        pygame.draw.circle(
            screen,
            glow_color,
            (int(self.position.x), int(self.position.y)),
            glow_rad,
            2,
        )
        # Inner dark backdrop
        pygame.draw.circle(
            screen,
            (15, 18, 25),
            (int(self.position.x), int(self.position.y)),
            int(self.radius),
        )
        # Bright perimeter border
        pygame.draw.circle(
            screen,
            core_color,
            (int(self.position.x), int(self.position.y)),
            int(self.radius),
            LINE_WIDTH - 1,
        )

        # Center indicator glyph
        font = pygame.font.SysFont(None, 18, bold=True)
        text_surf = font.render(label, True, core_color)
        text_rect = text_surf.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )
        screen.blit(text_surf, text_rect)
