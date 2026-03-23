# cli/views/personaggio.py
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich import box

from models.player import Personaggio


def _make_grid(*renderables) -> Table:
    grid = Table.grid(padding=(0, 2))
    for _ in renderables:
        grid.add_column()
    grid.add_row(*renderables)
    return grid

def _attr_table(pg: Personaggio) -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    t.add_column("Attr", style="cyan", width=5)
    t.add_column("Val", justify="right", width=4)
    t.add_column("Mod", justify="right", width=4)
    t.add_column("TS", justify="center", width=3)
    for attr_enum, attributo in pg.attributi.items():
        t.add_row(
            attr_enum.value[:3].upper(),
            str(attributo.valore),
            f"{attributo.modificatore:+}",
            "[green]✓[/green]" if attributo.ts else "[dim]—[/dim]",
        )
    return t

def _abilita_table(pg: Personaggio) -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
    t.add_column("Abilità", width=24)

    for abilita in pg.abilita:
        bonus = abilita.bonus(pg.bonus_competenza)
        t.add_row(
            f"{abilita.nome.label} ({abilita.attributo.nome[:3].upper()})",
            f"{bonus:+}",
            "[green]✓[/green]" if abilita.competente else "",
        )
    return t


def _descrizione_panel(pg: Personaggio) -> Panel:
    return Panel(
        pg.descrizione or "[dim]Nessuna descrizione disponibile.[/dim]",
        title="📖 Descrizione",
        border_style="yellow",
        expand=True,
    )


def _info_panel(pg: Personaggio) -> Table:
    classi = pg.classi_str
    razza = pg.razza.value if pg.razza else "—"
    rows = [
        (f"🏹 [bold cyan]{classi}[/bold cyan]"),
        (f"🧙 [bold]{razza}[/bold]"),
        (f"📈 [bold yellow]{pg.livello}[/bold yellow]"),
        (f"✨ [cyan]{pg.exp}[/cyan]"),
        (f"🎯 [bold green]+{pg.bonus_competenza}[/bold green]"),
        (f"💖 [bold red]{pg.hp}[/bold red]"),
    ]
    t = Table(box=box.SIMPLE, padding=(0, 1))
    t.add_column("Info")  # ← larghezza fissa per l'emoji
    for value in rows:
        t.add_row(value)
    return t




def pg_panel(pg: Personaggio) -> Panel:
    """Costruisce il pannello Rich completo per la visualizzazione del PG."""
    right = Group(
        _make_grid(_attr_table(pg), _info_panel(pg)),
        _abilita_table(pg),
    )
    return Panel(
        _make_grid(_descrizione_panel(pg), right),
        title=f"📜 {pg.nome} [dim](ID {pg.id})[/dim]",
        border_style="green",
        width=140,
        expand=False,
    )


def pg_row(pg: Personaggio) -> tuple:
    """Restituisce una tupla di stringhe per la riga nella tabella lista PG."""
    razza_str = pg.razza.value if pg.razza else "—"
    return (str(pg.id), pg.nome, razza_str, pg.classi_str, str(pg.livello), str(pg.exp))
