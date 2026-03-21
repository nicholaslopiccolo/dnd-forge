# cli/views/personaggio.py
from rich.console import Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich import box

from models.player import Personaggio
from models.constants import AttributoEnum


def _attr_table(pg: Personaggio) -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    t.add_column("Attr", style="cyan", width=5)
    t.add_column("Val", justify="center", width=4)
    t.add_column("Mod", justify="center", width=5)
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
    t.add_column("Attr", style="dim", width=5)
    t.add_column("Bon", justify="right", width=4)
    t.add_column("", width=2)  # competenza flag

    for abilita in pg.abilita:
        bonus = abilita.bonus(pg.bonus_competenza)
        t.add_row(
            abilita.nome.label,
            abilita.nome.attributo.value[:3].upper(),
            f"{bonus:+}",
            "[green]✓[/green]" if abilita.competente else "",
        )
    return t


def pg_panel(pg: Personaggio) -> Panel:
    classi_str = " / ".join(
        f"{c.livello}° {c.nome.value}" for c in pg.classi.values()
    )

    header = (
        f"[bold]Livello:[/bold] {pg.livello}  "
        f"[bold]Classe:[/bold] {classi_str}  "
        f"[bold]EXP:[/bold] {pg.exp}  "
        f"[bold]Comp.:[/bold] +{pg.bonus_competenza}  "
        f"[bold]HP:[/bold] {pg.hp}"
    )

    content = Group(
        header,
        "",
        Columns(
            [_attr_table(pg), _abilita_table(pg)],
            expand=False,
        ),
    )

    return Panel(
        content,
        title=f"📜 {pg.nome}",
        border_style="green",
        expand=False,
    )


def pg_row(pg: Personaggio) -> tuple:
    """Vista compatta per liste/tabelle."""
    classi_str = " / ".join(
        f"{c.livello}° {c.nome.value}" for c in pg.classi.values()
    )
    return (str(pg.id) if hasattr(pg, "id") else "—", pg.nome, classi_str, str(pg.livello), str(pg.exp))
