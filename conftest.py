"""Put src/ on sys.path so tests import modules the same way the installed package does (core, analyzers, ...).

Importing them as `src.core` as well loads each module twice, and enum members from the two copies never compare equal.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
