"""
Persistenza JSON per i personaggi.
Ogni PG viene salvato in saves/{id}.json relativo alla cwd dell'applicazione.
"""
from __future__ import annotations

import json
from pathlib import Path

from models.player import Personaggio
from storage.serializer import from_dict, to_dict

_SAVES_DIR = Path("saves")


def _saves_dir() -> Path:
    _SAVES_DIR.mkdir(exist_ok=True)
    return _SAVES_DIR


def _next_id() -> int:
    existing = [int(p.stem) for p in _saves_dir().glob("*.json") if p.stem.isdigit()]
    return max(existing, default=0) + 1


def save(pg: Personaggio) -> Personaggio:
    """Persiste il PG su disco. Assegna un ID se non ne ha ancora uno."""
    if pg.id == 0:
        pg.id = _next_id()
    path = _saves_dir() / f"{pg.id}.json"
    path.write_text(json.dumps(to_dict(pg), ensure_ascii=False, indent=2), encoding="utf-8")
    return pg


def load(pg_id: int) -> Personaggio:
    """Carica un PG dal disco tramite ID."""
    path = _saves_dir() / f"{pg_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Personaggio con ID {pg_id} non trovato.")
    return from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_all() -> list[Personaggio]:
    """Restituisce tutti i PG salvati, ordinati per ID."""
    return [
        from_dict(json.loads(p.read_text(encoding="utf-8")))
        for p in sorted(_saves_dir().glob("*.json"), key=lambda p: int(p.stem))
        if p.stem.isdigit()
    ]


def delete(pg_id: int) -> None:
    path = _saves_dir() / f"{pg_id}.json"
    if path.exists():
        path.unlink()
