"""Base circular sprite module for Asteroids game entities."""

from __future__ import annotations

from typing import ClassVar

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class representing a circular 2D game entity.

    Parameters
    ----------
    x : float
        Initial horizontal position on the screen.
    y : float
        Initial vertical position on the screen.
    radius : float
        Radius of the circular hitbox and rendering shape.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: float, y: float, radius: float) -> None:
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)
        self.radius: float = radius

    def draw(self, screen: pygame.Surface) -> None:
        """Render the circular sprite on the game screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """

    def update(self, dt: float) -> None:
        """Update entity position and state based on elapsed time.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """

    def collides_with(self, other: CircleShape) -> bool:
        """Check whether this circular entity collides with another circular entity.

        Parameters
        ----------
        other : CircleShape
            The other circular entity to test for collision.

        Returns
        -------
        bool
            True if the distance between centers is less than or equal to the sum
            of their radii, False otherwise.
        """
        distance = self.position.distance_to(other.position)
        return distance <= self.radius + other.radius
