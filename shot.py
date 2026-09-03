"""Laser projectile module for Asteroids."""

from __future__ import annotations

from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, SHOT_RADIUS


class Shot(CircleShape):
    """Laser projectile shot by the player ship.

    Parameters
    ----------
    x : float
        Initial horizontal position on the screen.
    y : float
        Initial vertical position on the screen.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the laser projectile as a small circle on the screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        """Update the projectile position according to its velocity vector.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.position += self.velocity * dt
