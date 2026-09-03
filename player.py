"""Player entity module for user-controlled spacecraft."""

from __future__ import annotations

from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
)
from shot import Shot


class Player(CircleShape):
    """Controllable player ship entity.

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
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation: float = 0.0
        self.cooldown_timer: float = 0.0

    def triangle(self) -> list[pygame.Vector2]:
        """Compute vertex coordinates forming the triangular ship geometry.

        Returns
        -------
        list[pygame.Vector2]
            List containing the three 2D vertex positions (front, back-left, back-right).
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * (self.radius / 1.5)
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        """Render the triangular ship on the game screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def rotate(self, dt: float) -> None:
        """Adjust the ship's rotation angle according to turn speed and elapsed time.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        """Handle keyboard input, apply movement/rotation, and decrement shoot cooldown.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.cooldown_timer -= dt

    def move(self, dt: float) -> None:
        """Translate the ship forward or backward along its facing vector.

        Parameters
        ----------
        dt : float
            Delta time in seconds. Positive values move forward; negative move backward.
        """
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self) -> None:
        """Spawn a laser projectile moving in the ship's facing direction if off cooldown."""
        if self.cooldown_timer > 0:
            return
        self.cooldown_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
