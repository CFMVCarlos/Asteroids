"""Top-level convenience runner for Asteroids."""

import sys
from pathlib import Path

# Add src to sys.path so running directly from repo root works seamlessly
src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from asteroids.main import main

if __name__ == "__main__":
    main()
