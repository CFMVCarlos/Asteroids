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
    is_homing : bool
        Whether this shot curves towards the closest asteroid.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    asteroid_target_group : ClassVar[pygame.sprite.Group | None]
        Optional reference to active asteroid group for homing tracking.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]
    asteroid_target_group: ClassVar[pygame.sprite.Group | None] = None

    def __init__(self, x: float, y: float, is_homing: bool = False) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.is_homing = is_homing

    def draw(self, screen: pygame.Surface) -> None:
        """Render the laser projectile on the screen with glow if homing.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        if self.is_homing:
            pygame.draw.circle(
                screen, (40, 180, 255), self.position, self.radius + 2, 1
            )
            pygame.draw.circle(screen, (150, 230, 255), self.position, self.radius)
        else:
            pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        """Update the projectile position, tracking towards target if homing.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        if self.is_homing and Shot.asteroid_target_group:
            # Find nearest asteroid
            nearest_dist = float("inf")
            target_pos: pygame.Vector2 | None = None
            for asteroid in Shot.asteroid_target_group:
                dist = self.position.distance_to(asteroid.position)
                if dist < nearest_dist:
                    nearest_dist = dist
                    target_pos = asteroid.position

            if target_pos is not None and nearest_dist < 450:
                desired_dir = (target_pos - self.position).normalize()
                curr_speed = self.velocity.length()
                if curr_speed > 0:
                    curr_dir = self.velocity.normalize()
                    # Steer gently towards target
                    steered = curr_dir.lerp(desired_dir, min(1.0, dt * 7.0)).normalize()
                    self.velocity = steered * curr_speed

        self.position += self.velocity * dt
