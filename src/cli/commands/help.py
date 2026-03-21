from commands import command, console, _REGISTRY
from rich.table import Table

@command("/help", "Mostra tutti i comandi disponibili")
async def cmd_help(_args):
    table = Table(title="Comandi DnD CLI", border_style="magenta")
    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Descrizione", style="white")
    for name, func in sorted(_REGISTRY.items()):
        table.add_row(name, func._description)
    console.print(table)
