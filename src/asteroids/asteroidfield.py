"""Asteroid field spawner module."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import ClassVar

import pygame

from .asteroid import Asteroid
from .constants import (
    ASTEROID_KINDS,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPAWN_RATE_SECONDS,
    MAX_ACTIVE_ASTEROIDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPECIAL_ASTEROID_CHANCE,
)

Edge = tuple[pygame.Vector2, Callable[[float], pygame.Vector2]]


class AsteroidField(pygame.sprite.Sprite):
    """Spawns asteroids procedurally along the screen boundaries.

    Parameters
    ----------
    asteroids_group : pygame.sprite.Group | None
        Reference to the active asteroids group to enforce the spawn cap.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    edges : ClassVar[list[Edge]]
        List of boundary spawn vectors and position mapping functions.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    edges: ClassVar[list[Edge]] = [
        (
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ),
        (
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ),
        (
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ),
        (
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ),
    ]

    def __init__(self, asteroids_group: pygame.sprite.Group | None = None) -> None:
        pygame.sprite.Sprite.__init__(self, *self.containers)
        self.spawn_timer: float = 0.0
        self.asteroids_group: pygame.sprite.Group | None = asteroids_group

    def spawn(
        self,
        radius: float,
        position: pygame.Vector2,
        velocity: pygame.Vector2,
        is_special: bool = False,
    ) -> None:
        """Instantiate and initialize an asteroid at a designated location.

        Parameters
        ----------
        radius : float
            Radius of the spawned asteroid.
        position : pygame.Vector2
            Initial 2D spawn coordinates.
        velocity : pygame.Vector2
            Initial 2D velocity vector.
        is_special : bool
            Whether this big asteroid is an illuminated 5-hit powerup bearer.
        """
        asteroid = Asteroid(position.x, position.y, radius, is_special=is_special)
        asteroid.velocity = velocity

    def update(self, dt: float) -> None:
        """Accumulate elapsed time and spawn asteroids at periodic intervals if below cap.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_SPAWN_RATE_SECONDS:
            self.spawn_timer = 0.0

            # Only spawn new wave asteroids if current count is below cap
            if (
                self.asteroids_group is not None
                and len(self.asteroids_group) >= MAX_ACTIVE_ASTEROIDS
            ):
                return

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed: float = float(random.randint(40, 100))
            velocity: pygame.Vector2 = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position: pygame.Vector2 = edge[1](random.uniform(0, 1))
            kind: int = random.randint(1, ASTEROID_KINDS)

            # Only biggest asteroids (kind == ASTEROID_KINDS) can be special (15% chance)
            is_special = (kind == ASTEROID_KINDS) and (
                random.random() < SPECIAL_ASTEROID_CHANCE
            )
            self.spawn(
                ASTEROID_MIN_RADIUS * kind, position, velocity, is_special=is_special
            )
