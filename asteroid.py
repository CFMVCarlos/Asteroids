import math
import random
from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import (
    ASTEROID_LIFETIME_SECONDS,
    ASTEROID_MIN_RADIUS,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPECIAL_ASTEROID_HP,
)
from logger import log_event


class Asteroid(CircleShape):
    """Jagged rocky asteroid entity that tumbles and splits when hit.

    Parameters
    ----------
    x : float
        Initial horizontal position on the screen.
    y : float
        Initial vertical position on the screen.
    radius : float
        Radius of the asteroid bounding circle.
    is_special : bool
        Whether this is a rare 5-HP special asteroid that drops a power-up.

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(
        self, x: float, y: float, radius: float, is_special: bool = False
    ) -> None:
        super().__init__(x, y, radius)
        self.rotation: float = random.uniform(0, 360)
        self.rot_speed: float = random.uniform(-45.0, 45.0)
        self.is_special: bool = is_special
        self.hp: int = SPECIAL_ASTEROID_HP if is_special else 1
        self.max_hp: int = self.hp
        self.hit_flash_timer: float = 0.0
        self.age: float = 0.0

        # Generate unique jagged procedural perimeter offsets
        num_vertices = random.randint(9, 13)
        self.offsets: list[
            tuple[float, float]
        ] = []  # (base_angle_rad, radius_multiplier)
        for i in range(num_vertices):
            base_angle = (2 * math.pi / num_vertices) * i
            # Jitter angle slightly and vary radius between 0.75 and 1.2
            angle_jitter = random.uniform(-0.15, 0.15)
            rad_scale = random.uniform(0.75, 1.25)
            self.offsets.append((base_angle + angle_jitter, rad_scale))

        # Generate 1 or 2 small crater details inside the rock
        self.craters: list[
            tuple[float, float, float]
        ] = []  # (angle_offset, dist_fraction, crater_radius)
        if self.radius > ASTEROID_MIN_RADIUS:
            for _ in range(random.randint(1, 2)):
                self.craters.append(
                    (
                        random.uniform(0, 2 * math.pi),
                        random.uniform(0.2, 0.55),
                        random.uniform(self.radius * 0.12, self.radius * 0.22),
                    )
                )

    def get_polygon_points(self) -> list[pygame.Vector2]:
        """Compute world coordinates for the rotating jagged rock perimeter.

        Returns
        -------
        list[pygame.Vector2]
            Points forming the outer rocky polygon.
        """
        rot_rad = math.radians(self.rotation)
        pts: list[pygame.Vector2] = []
        for angle, scale in self.offsets:
            total_angle = angle + rot_rad
            px = self.position.x + math.cos(total_angle) * (self.radius * scale)
            py = self.position.y + math.sin(total_angle) * (self.radius * scale)
            pts.append(pygame.Vector2(px, py))
        return pts

    def draw(self, screen: pygame.Surface) -> None:
        """Render the textured rock polygon, craters, and special powerup glow on screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        pts = self.get_polygon_points()
        if len(pts) >= 3:
            # Special asteroid body styling
            if self.is_special:
                # Radiant violet/gold tint
                fill_color = (
                    (45, 30, 55) if self.hit_flash_timer <= 0 else (120, 60, 140)
                )
                outline_color = (
                    (255, 215, 0) if self.hit_flash_timer <= 0 else (255, 255, 255)
                )
                # Outer pulsating glow aura
                pygame.draw.polygon(screen, (180, 140, 20), pts, LINE_WIDTH + 4)
            else:
                fill_color = (35, 38, 44)
                outline_color = (255, 255, 255)

            # Dark rock body fill
            pygame.draw.polygon(screen, fill_color, pts)
            # Jagged contour
            pygame.draw.polygon(screen, outline_color, pts, LINE_WIDTH)

        # Draw craters
        rot_rad = math.radians(self.rotation)
        for c_angle, dist_frac, c_rad in self.craters:
            total_angle = c_angle + rot_rad
            cx = self.position.x + math.cos(total_angle) * (self.radius * dist_frac)
            cy = self.position.y + math.sin(total_angle) * (self.radius * dist_frac)
            crater_color = (30, 20, 40) if self.is_special else (22, 24, 28)
            rim_color = (200, 160, 40) if self.is_special else (90, 95, 110)
            pygame.draw.circle(screen, crater_color, (int(cx), int(cy)), int(c_rad))
            pygame.draw.circle(screen, rim_color, (int(cx), int(cy)), int(c_rad), 2)

        # Draw remaining HP pips if special
        if self.is_special and self.hp > 0:
            pip_size = 5.0
            total_width = self.max_hp * 14.0
            start_x = self.position.x - total_width / 2 + 7.0
            pip_y = self.position.y - self.radius - 12.0
            for i in range(self.max_hp):
                pip_x = start_x + i * 14.0
                pip_color = (255, 215, 0) if i < self.hp else (70, 70, 80)
                pygame.draw.circle(
                    screen, pip_color, (int(pip_x), int(pip_y)), int(pip_size)
                )

    def update(self, dt: float) -> None:
        """Update the asteroid's position along velocity and tumble its rotation.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.position += self.velocity * dt
        self.rotation += self.rot_speed * dt
        self.age += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        # Once TTL (30s) has elapsed, do not loop when going off-screen; destroy into void
        pad = self.radius * 1.5
        is_off_screen = (
            self.position.x < -pad
            or self.position.x > SCREEN_WIDTH + pad
            or self.position.y < -pad
            or self.position.y > SCREEN_HEIGHT + pad
        )

        if is_off_screen:
            if self.age >= ASTEROID_LIFETIME_SECONDS:
                self.kill()
                return

            # Otherwise loop/wrap around screen
            if self.position.x < -pad:
                self.position.x = SCREEN_WIDTH + pad
            elif self.position.x > SCREEN_WIDTH + pad:
                self.position.x = -pad

            if self.position.y < -pad:
                self.position.y = SCREEN_HEIGHT + pad
            elif self.position.y > SCREEN_HEIGHT + pad:
                self.position.y = -pad

    def split(self) -> bool:
        """Process hit damage. Return True if asteroid was completely destroyed, False if still alive.

        Special asteroids require 5 hits and disappear directly to nothing without splitting.
        Standard asteroids split into two smaller fragments until minimum radius.
        """
        if self.is_special:
            self.hp -= 1
            self.hit_flash_timer = 0.15
            if self.hp > 0:
                # Still has hit points remaining
                return False

            # 5th hit: destroy completely to nothing
            self.kill()
            log_event("special_asteroid_destroyed")
            return True

        # Standard asteroid behavior
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return True

        log_event("asteroid_split")
        new_angle: float = random.uniform(20, 50)
        new_velocity_1: pygame.Vector2 = self.velocity.rotate(new_angle)
        new_velocity_2: pygame.Vector2 = self.velocity.rotate(-new_angle)
        new_radius: float = self.radius - ASTEROID_MIN_RADIUS
        new_asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid_1.velocity = new_velocity_1 * 1.2
        new_asteroid_2.velocity = new_velocity_2 * 1.2
        return True
