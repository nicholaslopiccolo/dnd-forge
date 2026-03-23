from pathlib import Path

from .base import carica_classe

Barbaro = carica_classe(Path(__file__).parent / "configurazioni" / "barbaro.json")
