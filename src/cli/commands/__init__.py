from rich.console import Console
import sys
import colorama

console = Console(
    force_terminal=True,
    legacy_windows=False if sys.platform == "win32" else None,
)

_REGISTRY: dict[str, callable] = {}

def command(name: str, description: str = ""):
    def decorator(func):
        func._description = description or func.__doc__ or ""
        _REGISTRY[name.lower()] = func
        return func
    return decorator

async def dispatch(raw_input: str):
    parts = raw_input.strip().split()
    if not parts or not parts[0].startswith("/"):
        console.print("[red]Usa /help per vedere i comandi disponibili.[/red]")
        return

    for length in range(len(parts), 0, -1):
        key = " ".join(parts[:length]).lower()
        if key in _REGISTRY:
            await _REGISTRY[key](parts[length:])
            return

    console.print(f"[red]Comando '{' '.join(parts[:2])}' non trovato.[/red]")
