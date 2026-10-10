"""Game configuration constants for Asteroids.

This module defines screen dimensions, rendering parameters, player movement
and shooting attributes, and asteroid generation metrics.
"""

SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
PLAYER_RADIUS: float = 20.0
LINE_WIDTH: int = 4
PLAYER_TURN_SPEED: float = 300.0
PLAYER_SPEED: float = 200.0
PLAYER_ACCELERATION: float = 400.0
PLAYER_DRAG: float = 0.985
PLAYER_MAX_SPEED: float = 450.0
ASTEROID_MIN_RADIUS: float = 20.0
ASTEROID_KINDS: int = 3
ASTEROID_SPAWN_RATE_SECONDS: float = 0.8
ASTEROID_MAX_RADIUS: float = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
SHOT_RADIUS: float = 5.0
PLAYER_SHOOT_SPEED: float = 500.0
PLAYER_SHOOT_COOLDOWN_SECONDS: float = 0.3
