import math
import random
from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH
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

    Attributes
    ----------
    containers : ClassVar[tuple[pygame.sprite.Group, ...]]
        Sprite groups to which instances of this class are automatically added.
    """

    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.rotation: float = random.uniform(0, 360)
        self.rot_speed: float = random.uniform(-45.0, 45.0)

        # Generate unique jagged procedural perimeter offsets
        num_vertices = random.randint(9, 13)
        self.offsets: list[tuple[float, float]] = []  # (base_angle_rad, radius_multiplier)
        for i in range(num_vertices):
            base_angle = (2 * math.pi / num_vertices) * i
            # Jitter angle slightly and vary radius between 0.75 and 1.2
            angle_jitter = random.uniform(-0.15, 0.15)
            rad_scale = random.uniform(0.75, 1.25)
            self.offsets.append((base_angle + angle_jitter, rad_scale))

        # Generate 1 or 2 small crater details inside the rock
        self.craters: list[tuple[float, float, float]] = []  # (angle_offset, dist_fraction, crater_radius)
        if self.radius > ASTEROID_MIN_RADIUS:
            for _ in range(random.randint(1, 2)):
                self.craters.append((
                    random.uniform(0, 2 * math.pi),
                    random.uniform(0.2, 0.55),
                    random.uniform(self.radius * 0.12, self.radius * 0.22),
                ))

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
        """Render the textured rock polygon and craters on the screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        pts = self.get_polygon_points()
        if len(pts) >= 3:
            # Dark charcoal rock body fill
            pygame.draw.polygon(screen, (35, 38, 44), pts)
            # Bright white jagged contour
            pygame.draw.polygon(screen, "white", pts, LINE_WIDTH)

        # Draw craters
        rot_rad = math.radians(self.rotation)
        for c_angle, dist_frac, c_rad in self.craters:
            total_angle = c_angle + rot_rad
            cx = self.position.x + math.cos(total_angle) * (self.radius * dist_frac)
            cy = self.position.y + math.sin(total_angle) * (self.radius * dist_frac)
            pygame.draw.circle(screen, (22, 24, 28), (int(cx), int(cy)), int(c_rad))
            pygame.draw.circle(screen, (90, 95, 110), (int(cx), int(cy)), int(c_rad), 2)

    def update(self, dt: float) -> None:
        """Update the asteroid's position along velocity and tumble its rotation.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.position += self.velocity * dt
        self.rotation += self.rot_speed * dt

        # Screen wrap-around for asteroids
        pad = self.radius * 1.5
        if self.position.x < -pad:
            self.position.x = SCREEN_WIDTH + pad
        elif self.position.x > SCREEN_WIDTH + pad:
            self.position.x = -pad

        if self.position.y < -pad:
            self.position.y = SCREEN_HEIGHT + pad
        elif self.position.y > SCREEN_HEIGHT + pad:
            self.position.y = -pad

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
