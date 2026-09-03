"""Asteroid game entity module."""

from __future__ import annotations

import random
from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH
from logger import log_event


class Asteroid(CircleShape):
    """Circular asteroid entity that floats in space and splits when hit.

    Parameters
    ----------
    x : float
        Initial horizontal position on the screen.
    y : float
        Initial vertical position on the screen.
    radius : float
        Radius of the asteroid.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the asteroid outline on the screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        """Update the asteroid's position along its current velocity vector.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.position += self.velocity * dt

    def split(self) -> None:
        """Split the asteroid into two smaller fragments, or destroy it if minimal."""
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        new_angle: float = random.uniform(20, 50)
        new_velocity_1: pygame.Vector2 = self.velocity.rotate(new_angle)
        new_velocity_2: pygame.Vector2 = self.velocity.rotate(-new_angle)
        new_radius: float = self.radius - ASTEROID_MIN_RADIUS
        new_asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid_1.velocity = new_velocity_1 * 1.2
        new_asteroid_2.velocity = new_velocity_2 * 1.2
