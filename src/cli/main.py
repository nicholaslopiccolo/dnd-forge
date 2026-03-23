import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

# Importa i moduli per registrare i comandi nel registry
import commands.exit
import commands.help
import commands.pg

from commands import dispatch, console, _REGISTRY
from commands.pg import get_active_pg


def _make_prompt() -> str:
    pg = get_active_pg()
    if pg is None:
        return "🎲 > "
    classe_str = " / ".join(f"{c.nome.value} {c.livello}" for c in pg.classi.values())
    return f"🎲 [{pg.nome} · {classe_str}] > "


async def main():
    completer = WordCompleter(list(_REGISTRY.keys()), sentence=True)

    session = PromptSession(
        history=FileHistory(".dnd_history"),
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
    )

    console.print("[bold magenta]⚔️  DnD CLI[/bold magenta] — [dim]/help per i comandi[/dim]\n")

    while True:
        try:
            raw = await session.prompt_async(_make_prompt)
        except (EOFError, KeyboardInterrupt, SystemExit):
            console.print("\n[dim]Che la fortuna vi arrida, avventurieri.[/dim]")
            break

        if raw.strip():
            await dispatch(raw)


asyncio.run(main())
