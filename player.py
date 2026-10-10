import random
from typing import ClassVar, TypedDict

import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_DRAG,
    PLAYER_INVULNERABLE_DURATION_SECONDS,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_TURN_SPEED,
    POWERUP_INVINCIBILITY_DURATION,
    POWERUP_RAPID_FIRE_DURATION,
    POWERUP_TRIPLE_SHOT_DURATION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from shot import Shot


class ExhaustParticle(TypedDict):
    """Particle metadata for booster rocket exhaust."""

    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    life: float
    max_life: float


class Player(CircleShape):
    """Controllable player rocket ship entity with inertia, lives, damage flash, and skill upgrades.

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
        self.is_boosting: bool = False
        self.flame_flicker: float = 0.0
        self.exhaust_particles: list[ExhaustParticle] = []
        self.invulnerable_timer: float = 0.0
        self.flash_timer: float = 0.0

        # Skill Buff Timers
        self.triple_shot_timer: float = 0.0
        self.rapid_fire_timer: float = 0.0
        self.invincible_skill_timer: float = 0.0

    def activate_powerup(self, kind: str) -> None:
        """Activate a skill buff for its designated duration."""
        if kind == "TRIPLE_SHOT":
            self.triple_shot_timer = POWERUP_TRIPLE_SHOT_DURATION
        elif kind == "RAPID_FIRE":
            self.rapid_fire_timer = POWERUP_RAPID_FIRE_DURATION
        elif kind == "INVINCIBILITY":
            self.invincible_skill_timer = POWERUP_INVINCIBILITY_DURATION

    def trigger_hit(self) -> None:
        """Trigger temporary invulnerability and flashing animation after taking damage."""
        self.invulnerable_timer = PLAYER_INVULNERABLE_DURATION_SECONDS
        self.flash_timer = 0.0

    @property
    def is_invulnerable(self) -> bool:
        """Check whether the ship is currently invulnerable from damage or star buff."""
        return self.invulnerable_timer > 0.0 or self.invincible_skill_timer > 0.0

    def get_rocket_points(self) -> dict[str, list[pygame.Vector2]]:
        """Compute coordinates for the fuselage, wings, cockpit, and engine bell.

        Returns
        -------
        dict[str, list[pygame.Vector2]]
            Geometry points for the body parts of the rocket ship.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)

        # Fuselage (sleek nosecone tapering into body)
        nose = self.position + forward * (self.radius * 1.35)
        shoulder_right = (
            self.position + forward * (self.radius * 0.1) + right * (self.radius * 0.45)
        )
        shoulder_left = (
            self.position + forward * (self.radius * 0.1) - right * (self.radius * 0.45)
        )
        base_right = (
            self.position - forward * (self.radius * 0.8) + right * (self.radius * 0.4)
        )
        base_left = (
            self.position - forward * (self.radius * 0.8) - right * (self.radius * 0.4)
        )
        fuselage = [nose, shoulder_right, base_right, base_left, shoulder_left]

        # Wings / Fins
        wing_tip_right = (
            self.position - forward * (self.radius * 0.9) + right * (self.radius * 1.15)
        )
        fin_right = [shoulder_right, wing_tip_right, base_right]

        wing_tip_left = (
            self.position - forward * (self.radius * 0.9) - right * (self.radius * 1.15)
        )
        fin_left = [shoulder_left, wing_tip_left, base_left]

        # Cockpit canopy
        canopy_tip = self.position + forward * (self.radius * 0.75)
        canopy_r = (
            self.position + forward * (self.radius * 0.1) + right * (self.radius * 0.2)
        )
        canopy_b = self.position - forward * (self.radius * 0.15)
        canopy_l = (
            self.position + forward * (self.radius * 0.1) - right * (self.radius * 0.2)
        )
        canopy = [canopy_tip, canopy_r, canopy_b, canopy_l]

        # Engine nozzle base
        nozzle_l = (
            self.position - forward * (self.radius * 0.8) - right * (self.radius * 0.22)
        )
        nozzle_r = (
            self.position - forward * (self.radius * 0.8) + right * (self.radius * 0.22)
        )
        nozzle_bl = (
            self.position
            - forward * (self.radius * 0.95)
            - right * (self.radius * 0.28)
        )
        nozzle_br = (
            self.position
            - forward * (self.radius * 0.95)
            + right * (self.radius * 0.28)
        )
        nozzle = [nozzle_l, nozzle_r, nozzle_br, nozzle_bl]

        return {
            "fuselage": fuselage,
            "fin_right": fin_right,
            "fin_left": fin_left,
            "canopy": canopy,
            "nozzle": nozzle,
        }

    def draw(self, screen: pygame.Surface) -> None:
        """Render the rocket ship, cockpit, fins, and animated thruster flame on screen.

        Parameters
        ----------
        screen : pygame.Surface
            Target Pygame surface to render the entity onto.
        """
        # When damaged and invulnerable, flash/blink at 10Hz
        if self.invulnerable_timer > 0.0 and int(self.flash_timer * 12) % 2 == 1:
            return

        # Render lingering exhaust smoke/spark particles
        for p in self.exhaust_particles:
            pos = p["pos"]
            alpha = max(0.0, min(1.0, p["life"] / p["max_life"]))
            rad = max(1, int(p["radius"] * alpha))
            color = (
                int(255 * alpha),
                int(random.randint(120, 200) * alpha),
                int(40 * alpha),
            )
            pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), rad)

        pts = self.get_rocket_points()

        # Draw Booster Fire when accelerating
        if self.is_boosting:
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
            engine_center = self.position - forward * (self.radius * 0.95)

            # Outer roaring flame (Orange / Red)
            flame_len = (self.radius * 1.2) + (random.random() * self.radius * 0.9)
            flame_tip = engine_center - forward * flame_len
            outer_flame = [
                engine_center - right * (self.radius * 0.35),
                engine_center + right * (self.radius * 0.35),
                flame_tip,
            ]
            pygame.draw.polygon(screen, (255, 100, 20), outer_flame)

            # Inner core plasma flame (Bright Yellow / Cyan-White)
            inner_len = flame_len * 0.55
            inner_tip = engine_center - forward * inner_len
            inner_flame = [
                engine_center - right * (self.radius * 0.18),
                engine_center + right * (self.radius * 0.18),
                inner_tip,
            ]
            pygame.draw.polygon(screen, (255, 240, 150), inner_flame)

        # Draw Wings / Fins
        pygame.draw.polygon(screen, (80, 110, 160), pts["fin_left"])
        pygame.draw.polygon(screen, "white", pts["fin_left"], LINE_WIDTH)
        pygame.draw.polygon(screen, (80, 110, 160), pts["fin_right"])
        pygame.draw.polygon(screen, "white", pts["fin_right"], LINE_WIDTH)

        # Draw Main Fuselage
        pygame.draw.polygon(screen, (25, 30, 45), pts["fuselage"])
        pygame.draw.polygon(screen, "white", pts["fuselage"], LINE_WIDTH)

        # Draw Engine Nozzle
        pygame.draw.polygon(screen, (140, 145, 160), pts["nozzle"])
        pygame.draw.polygon(screen, "white", pts["nozzle"], 2)

        # Draw Cockpit Canopy
        pygame.draw.polygon(screen, (60, 200, 255), pts["canopy"])
        pygame.draw.polygon(screen, (180, 240, 255), pts["canopy"], 2)

        # Draw Invincibility Shield Aura if active
        if self.invincible_skill_timer > 0.0:
            shield_radius = int(self.radius * 1.55)
            # Pulsing violet-gold celestial shield
            shield_alpha_pulse = int(self.flash_timer * 15) % 2
            color = (255, 215, 0) if shield_alpha_pulse == 0 else (220, 80, 255)
            pygame.draw.circle(
                screen,
                color,
                (int(self.position.x), int(self.position.y)),
                shield_radius,
                2,
            )
            # Inner resonant ring
            pygame.draw.circle(
                screen,
                (180, 100, 255),
                (int(self.position.x), int(self.position.y)),
                shield_radius - 4,
                1,
            )

    def rotate(self, dt: float) -> None:
        """Adjust the ship's rotation angle according to turn speed and elapsed time.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt: float) -> None:
        """Handle keyboard input, apply inertia sliding, spawn particles, and update position.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame update.
        """
        keys = pygame.key.get_pressed()

        # Rotation controls
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)

        # Propulsion thrust with inertia
        self.is_boosting = False
        forward = pygame.Vector2(0, 1).rotate(self.rotation)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.is_boosting = True
            # Accelerate in facing direction
            self.velocity += forward * (PLAYER_ACCELERATION * dt)
            if self.velocity.length() > PLAYER_MAX_SPEED:
                self.velocity.scale_to_length(PLAYER_MAX_SPEED)

            # Spawn exhaust particle
            engine_pos = self.position - forward * self.radius
            spread = pygame.Vector2(random.uniform(-15, 15), random.uniform(-15, 15))
            particle_vel = -forward * random.uniform(80, 160) + spread
            self.exhaust_particles.append(
                {
                    "pos": pygame.Vector2(engine_pos.x, engine_pos.y),
                    "vel": particle_vel,
                    "radius": random.uniform(3.0, 5.5),
                    "life": 0.25,
                    "max_life": 0.25,
                }
            )

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            # Retro-thrusters / gentle brake
            self.velocity -= forward * (PLAYER_ACCELERATION * 0.5 * dt)

        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.cooldown_timer -= dt

        # Update skill buff timers
        if self.triple_shot_timer > 0.0:
            self.triple_shot_timer = max(0.0, self.triple_shot_timer - dt)
        if self.rapid_fire_timer > 0.0:
            self.rapid_fire_timer = max(0.0, self.rapid_fire_timer - dt)
        if self.invincible_skill_timer > 0.0:
            self.invincible_skill_timer = max(0.0, self.invincible_skill_timer - dt)

        # Update invulnerability flash timers
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        self.flash_timer += dt

        # Apply ice-like drift / inertia & low drag
        # Exponential drag formula: vel * (drag ^ (dt * 60))
        drag_factor = PLAYER_DRAG ** (dt * 60.0)
        self.velocity *= drag_factor

        # Move by velocity
        self.position += self.velocity * dt

        # Screen wrap-around for classic arcade physics
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

        # Update and purge particles
        active_particles: list[ExhaustParticle] = []
        for p in self.exhaust_particles:
            life = p["life"] - dt
            if life > 0:
                p["life"] = life
                pos = p["pos"]
                vel = p["vel"]
                pos += vel * dt
                active_particles.append(p)
        self.exhaust_particles = active_particles

    def shoot(self) -> None:
        """Spawn laser projectiles moving forward (or triple-spread if buff active) if off cooldown."""
        if self.cooldown_timer > 0:
            return

        # Double attack speed (half cooldown) when RAPID_FIRE is active
        base_cooldown = (
            PLAYER_SHOOT_COOLDOWN_SECONDS * 0.5
            if self.rapid_fire_timer > 0.0
            else PLAYER_SHOOT_COOLDOWN_SECONDS
        )
        self.cooldown_timer = base_cooldown

        if self.triple_shot_timer > 0.0:
            # 3 shots: straight (0°), 45° to the right, and 45° to the left
            angles = [self.rotation, self.rotation + 45.0, self.rotation - 45.0]
            for angle in angles:
                shot = Shot(self.position.x, self.position.y)
                shot.velocity = pygame.Vector2(0, 1).rotate(angle) * PLAYER_SHOOT_SPEED
        else:
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = (
                pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            )
