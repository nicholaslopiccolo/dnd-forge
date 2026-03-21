import asyncio
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

# Importa i moduli per registrare i comandi nel registry
import commands.help
import commands.pg
# import commands.ps  ← aggiungi man mano

from commands import dispatch, _REGISTRY

console = Console()

async def main():
    # Autocompletamento Tab sui comandi registrati
    completer = WordCompleter(list(_REGISTRY.keys()), sentence=True)

    session = PromptSession(
        history=FileHistory(".dnd_history"),
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
    )

    console.print("[bold magenta]⚔️  DnD CLI[/bold magenta] — [dim]/help per i comandi[/dim]\n")

    with patch_stdout():
        while True:
            try:
                raw = await session.prompt_async("🎲 > ")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Che la fortuna vi arrida, avventurieri.[/dim]")
                break

            if raw.strip():
                await dispatch(raw)

asyncio.run(main())
