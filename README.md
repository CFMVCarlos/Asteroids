<div align="center">

# 🚀 Asteroids (Pygame)

An arcade space combat game built with Python 3.13+ and Pygame, featuring vector-based movement, procedural asteroid spawning, weapon physics, and dynamic collision dynamics.

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/pygame-2.6.1-green.svg?logo=python&logoColor=white)](https://www.pygame.org/)
[![Package Manager: uv](https://img.shields.io/badge/packaging-uv-purple.svg?logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Type Checked](https://img.shields.io/badge/types-basedpyright%20%7C%20ty-blueviolet.svg)](https://github.com/DetachHead/basedpyright)

---

</div>

## 🌌 Overview

**Asteroids** is a modernized recreation of the classic arcade shooter. Pilot your ship through a hazardous asteroid field in deep space, utilize responsive thrusters and rotation mechanics to evade collisions, and blast incoming asteroids into fragmented pieces with high-speed lasers.

---

## ✨ Features

- **🚀 Vector-Based Ship Controls:** Smooth rotational turning and forward/backward directional propulsion.
- **🔫 Projectile Firing Mechanics:** Laser blaster with weapon cooldown timers and projectile physics.
- **☄️ Dynamic Asteroid Splitting:** Larger asteroids fracture into two smaller, higher-velocity pieces upon laser impact until fully obliterated.
- **🎲 Edge-Spawning Asteroid Field:** Procedural generation of varied asteroid sizes across all four screen boundaries.
- **💥 Precise Collision System:** Circle-distance based collision engine for both player-asteroid and projectile-asteroid interactions.
- **📈 Telemetry & Event Logging:** Real-time event and game state logging to `.jsonl` files for replay analysis and debugging.
- **⚡ Modern Python Toolchain:** Managed with [`uv`](https://github.com/astral-sh/uv) and verified with static typing and linters (`ruff`, `pydoclint`, `ty`, `basedpyright`).

---

## 🎮 Controls

| Action | Key | Description |
| :--- | :---: | :--- |
| **Rotate Left** | <kbd>A</kbd> | Turn ship counter-clockwise |
| **Rotate Right** | <kbd>D</kbd> | Turn ship clockwise |
| **Thrust Forward** | <kbd>W</kbd> | Accelerate in the facing direction |
| **Reverse Thrust** | <kbd>S</kbd> | Move backwards |
| **Fire Blaster** | <kbd>Space</kbd> | Shoot high-speed laser projectile |
| **Quit Game** | <kbd>Esc</kbd> / Close Window | Exit the game |

---

## 📦 Project Structure

```text
Asteroids/
├── asteroid.py          # Asteroid entity & split mechanics
├── asteroidfield.py     # Procedural edge-spawner & difficulty scaling
├── circleshape.py       # Base 2D sprite class with circle collision logic
├── constants.py         # Screen dimensions, radii, speeds, and timings
├── logger.py            # Event & state JSONL telemetry recorder
├── main.py              # Pygame initialization & core game loop
├── player.py            # Player triangle model, input handling & shooting
├── shot.py              # Laser projectile entity
├── pyproject.toml       # Project metadata, dependencies & tool configs
└── uv.lock              # Deterministic lockfile
```

---

## 🛠️ Getting Started

### Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) *(recommended)* or standard `pip`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CFMVCarlos/Asteroids.git
   cd Asteroids
   ```

2. **Install dependencies:**
   
   Using **`uv`** (fastest):
   ```bash
   uv sync
   ```

   *Or using standard virtual environment and pip:*
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

---

## 🚀 Running the Game

Launch the game using `uv`:

```bash
uv run python main.py
```

*Or within an activated virtual environment:*

```bash
python main.py
```

---

## 🧪 Code Quality & Development

The repository enforces strict code quality, linting, docstrings, and static type checking:

```bash
# Format and lint check
uv run ruff format
uv run ruff check --fix

# Docstring verification
uv run pydoclint .

# Static type checking
uv run ty check
uv run basedpyright
```

---

## 👤 Author

- **Carlos Valente** – [GitHub (@CFMVCarlos)](https://github.com/CFMVCarlos)
- Built as part of the [Boot.dev](https://www.boot.dev) Python / Game Development curriculum.
