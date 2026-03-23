from commands import command, console
from InquirerPy import inquirer
from models.constants import ClassiEnum, RazzaEnum, AttributoEnum, AbilitaEnum
from models.player import Personaggio, Attributo
from models.classi.base import Classe as ClasseModel
from rich.panel import Panel
from rich.table import Table
from rich import box
from views.personaggio import pg_panel, pg_row
import storage.repository as repo
from utils.llm import genera_descrizione

ASI_LIVELLI = {4, 8, 12, 16, 19}

_active_pg: Personaggio | None = None

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]


def get_active_pg() -> Personaggio | None:
    return _active_pg


def set_active_pg(pg: Personaggio | None) -> None:
    global _active_pg
    _active_pg = pg


def _require_active_pg() -> Personaggio | None:
    """Returns the active PG or prints an error and returns None."""
    if _active_pg is None:
        console.print("[red]Nessun personaggio attivo. Usa /pg list per selezionarne uno.[/red]")
    return _active_pg


async def _chiedi_nome() -> str:
    return await inquirer.text(
        message="Nome del personaggio:",
        validate=lambda x: len(x.strip()) > 0,
        invalid_message="Il nome non può essere vuoto."
    ).execute_async()


async def _chiedi_classe() -> ClassiEnum:
    return await inquirer.select(
        message="Scegli la classe iniziale:",
        choices=[{"name": c.value, "value": c} for c in ClassiEnum],
    ).execute_async()


async def _chiedi_razza() -> RazzaEnum:
    return await inquirer.select(
        message="Scegli la razza:",
        choices=[{"name": r.value, "value": r} for r in RazzaEnum],
    ).execute_async()


async def _attributi_standard() -> dict[AttributoEnum, Attributo]:
    console.print("\n[dim]Assegna i valori dello standard array a ciascun attributo.[/dim]")
    disponibili = list(STANDARD_ARRAY)
    attributi = {}

    for attr in AttributoEnum:
        scelta = await inquirer.select(
            message=f"Valore per [cyan]{attr.value.upper()}[/cyan] (disponibili: {disponibili}):",
            choices=[{"name": str(v), "value": v} for v in disponibili],
        ).execute_async()
        attributi[attr] = Attributo(nome=attr.value, valore=scelta)
        disponibili.remove(scelta)

    return attributi


async def _attributi_manuali() -> dict[AttributoEnum, Attributo]:
    console.print("\n[dim]Inserisci un valore tra 1 e 20 per ciascun attributo.[/dim]")
    attributi = {}

    for attr in AttributoEnum:
        valore = await inquirer.number(
            message=f"{attr.value.upper()}:",
            min_allowed=1,
            max_allowed=20,
            default=10,
        ).execute_async()
        attributi[attr] = Attributo(nome=attr.value, valore=int(valore))

    return attributi


async def _chiedi_attributi() -> dict[AttributoEnum, Attributo]:
    metodo = await inquirer.select(
        message="Come vuoi assegnare gli attributi?",
        choices=[
            {"name": "Manuale (inserisci i valori)", "value": "manuale"},
            {"name": "Standard array (15,14,13,12,10,8)", "value": "standard"},
        ]
    ).execute_async()

    if metodo == "standard":
        return await _attributi_standard()
    return await _attributi_manuali()


async def _chiedi_competenze(num_competenze: int) -> set[AbilitaEnum]:
    console.print(f"\n[dim]Scegli {num_competenze} abilità con competenza.[/dim]")
    scelte = await inquirer.checkbox(
        message=f"Seleziona {num_competenze} abilità (spazio per selezionare):",
        choices=[
            {"name": f"{a.label} [{a.attributo.value[:3].upper()}]", "value": a}
            for a in AbilitaEnum
        ],
        validate=lambda x: len(x) == num_competenze,
        invalid_message=f"Devi selezionare esattamente {num_competenze} abilità.",
    ).execute_async()
    return set(scelte)


def _mostra_lista_personaggi(personaggi: list[Personaggio]):
    table = Table(title="Personaggi salvati", box=box.ROUNDED)
    for col in ("ID", "Nome", "Razza", "Classe", "Livello", "EXP"):
        table.add_column(col)
    for p in personaggi:
        table.add_row(*pg_row(p))
    console.print(table)


@command("/pg create", "Crea un nuovo personaggio in modo guidato")
async def pg_create(_args):
    nome = await _chiedi_nome()
    classe_iniziale = await _chiedi_classe()
    razza = await _chiedi_razza()
    attributi = await _chiedi_attributi()

    try:
        pg = Personaggio(
            nome=nome.strip(),
            classe_iniziale=classe_iniziale,
            razza=razza,
            attributi=attributi,
        )
    except Exception as e:
        console.print(f"[red]Errore nella creazione: {e}[/red]")
        return

    classe_obj = pg.classi[classe_iniziale]
    num_competenze = classe_obj.skills_choices_num or 2
    pg.competenze = await _chiedi_competenze(num_competenze)

    repo.save(pg)
    set_active_pg(pg)

    console.print(pg_panel(pg))
    console.print("[green]✓ Personaggio creato e impostato come attivo.[/green]")


@command("/pg list", "Mostra tutti i personaggi salvati e ne seleziona uno come attivo")
async def pg_list(_args):
    personaggi = repo.list_all()
    if not personaggi:
        console.print("[yellow]Nessun personaggio salvato. Usa /pg create per crearne uno.[/yellow]")
        return

    scelta = await inquirer.select(
        message="Seleziona un personaggio:",
        choices=[
            {
                "name": f"[{p.id}] {p.nome} — {' / '.join(f'{c.nome.value} {c.livello}' for c in p.classi.values())}",
                "value": p,
            }
            for p in personaggi
        ],
    ).execute_async()

    set_active_pg(scelta)
    console.print(pg_panel(scelta))
    console.print(f"[green]✓ Personaggio attivo: {scelta.nome}[/green]")


@command("/pg status", "Mostra la scheda del personaggio attivo")
async def pg_status(_args):
    pg = _require_active_pg()
    if pg:
        console.print(pg_panel(pg))


@command("/pg show", "Alias di /pg status")
async def pg_show(_args):
    await pg_status(_args)


@command("/pg save", "Salva il personaggio attivo su disco")
async def pg_save(_args):
    pg = _require_active_pg()
    if not pg:
        return
    repo.save(pg)
    console.print(f"[green]✓ {pg.nome} salvato (ID {pg.id}).[/green]")


@command("/pg delete", "Elimina il personaggio attivo")
async def pg_delete(_args):
    pg = _require_active_pg()
    if not pg:
        return
    confermato = await inquirer.confirm(
        message=f"Sei sicuro di voler eliminare '{pg.nome}'? Questa azione è irreversibile.",
        default=False,
    ).execute_async()
    if confermato:
        repo.delete(pg.id)
        set_active_pg(None)
        console.print(f"[yellow]Personaggio eliminato.[/yellow]")


@command("/pg rename", "Rinomina il personaggio attivo")
async def pg_rename(_args):
    pg = _require_active_pg()
    if not pg:
        return
    nuovo_nome = await inquirer.text(
        message=f"Nuovo nome (attuale: {pg.nome}):",
        validate=lambda x: len(x.strip()) > 0,
        invalid_message="Il nome non può essere vuoto.",
    ).execute_async()
    pg.nome = nuovo_nome.strip()
    repo.save(pg)
    console.print(f"[green]✓ Personaggio rinominato in '{pg.nome}'.[/green]")


def _attrs_disponibili(pg: Personaggio, escludi: AttributoEnum | None = None) -> list[dict]:
    return [
        {"name": f"{a.value.capitalize()} (attuale: {pg.attributi[a].valore})", "value": a}
        for a in AttributoEnum
        if pg.attributi[a].valore < 20 and a != escludi
    ]


async def _chiedi_asi(pg: Personaggio) -> None:
    """Gestisce l'Aumento di Caratteristica al livello ASI."""
    console.print(f"\n[bold yellow]✨ Livello {pg.livello}: Aumento di Caratteristica disponibile![/bold yellow]")
    modalita = await inquirer.select(
        message="Come vuoi applicare l'ASI?",
        choices=[
            {"name": "+2 a un singolo attributo", "value": "singolo"},
            {"name": "+1 a due attributi diversi", "value": "doppio"},
        ],
    ).execute_async()

    if modalita == "singolo":
        scelta = await inquirer.select(
            message="Scegli l'attributo (+2):",
            choices=_attrs_disponibili(pg),
        ).execute_async()
        pg.attributi[scelta].valore = min(pg.attributi[scelta].valore + 2, 20)
        console.print(f"[cyan]{scelta.value.capitalize()}[/cyan] → {pg.attributi[scelta].valore}")
    else:
        prima = await inquirer.select(
            message="Primo attributo (+1):",
            choices=_attrs_disponibili(pg),
        ).execute_async()
        pg.attributi[prima].valore = min(pg.attributi[prima].valore + 1, 20)

        seconda = await inquirer.select(
            message="Secondo attributo (+1):",
            choices=_attrs_disponibili(pg, escludi=prima),
        ).execute_async()
        pg.attributi[seconda].valore = min(pg.attributi[seconda].valore + 1, 20)
        console.print(
            f"[cyan]{prima.value.capitalize()}[/cyan] → {pg.attributi[prima].valore}  "
            f"[cyan]{seconda.value.capitalize()}[/cyan] → {pg.attributi[seconda].valore}"
        )


async def _esegui_levelup(pg: Personaggio) -> None:
    """Executes a single interactive level-up step."""
    console.print(f"\n[bold yellow]⬆  Livello {pg.livello + 1}![/bold yellow]")

    classi_correnti = [
        {"name": f"{c.nome.value} (Liv. {c.livello})", "value": c.nome}
        for c in pg.classi.values()
    ]

    classe = None
    while classe is None:
        scelta = await inquirer.select(
            message="Scegli la classe per il level up:",
            choices=classi_correnti + [{"name": "Altra classe (Multiclasse)", "value": "multiclasse"}],
        ).execute_async()

        if scelta != "multiclasse":
            classe = scelta
            break

        classi_disponibili = [c for c in ClassiEnum if c not in pg.classi]
        if not classi_disponibili:
            console.print("[yellow]Tutte le classi sono già presenti.[/yellow]")
            continue

        nuova = await inquirer.select(
            message="Scegli la nuova classe da aggiungere:",
            choices=[{"name": c.value, "value": c} for c in classi_disponibili]
                + [{"name": "Annulla e torna indietro", "value": None}],
        ).execute_async()

        if nuova is not None:
            classe = nuova

    hp_prima = pg.hp
    pg.level_up(classe)
    hp_guadagnati = pg.hp - hp_prima
    if hp_guadagnati > 0:
        console.print(f"[dim]❤️  HP +{hp_guadagnati}[/dim]")

    if pg.livello in ASI_LIVELLI:
        await _chiedi_asi(pg)


@command("/pg xp", "Aggiunge EXP al personaggio attivo (es. /pg xp 300)")
async def pg_xp(args: list[str]):
    pg = _require_active_pg()
    if not pg:
        return

    if not args:
        console.print("[red]Specifica la quantità di EXP. Es: /pg xp 300[/red]")
        return

    try:
        amount = int(args[0])
    except ValueError:
        console.print(f"[red]'{args[0]}' non è un numero valido.[/red]")
        return

    if amount <= 0:
        console.print("[red]La quantità deve essere positiva.[/red]")
        return

    pg.add_exp(amount)
    console.print(f"[cyan]+{amount} EXP[/cyan] → totale {pg.exp}")

    pending = pg.pending_levelups()
    for _ in range(pending):
        await _esegui_levelup(pg)

    repo.save(pg)
    console.print(pg_panel(pg))


@command("/pg levelup", "Esegue il level-up manuale del personaggio attivo")
async def pg_levelup(_args):
    pg = _require_active_pg()
    if not pg:
        return
    if pg.livello >= 20:
        console.print("[yellow]Il personaggio è già al livello massimo (20).[/yellow]")
        return
    await _esegui_levelup(pg)
    repo.save(pg)
    console.print(pg_panel(pg))


@command("/pg describe", "Genera una descrizione narrativa AI del personaggio attivo")
async def pg_describe(_args):
    pg = _require_active_pg()
    if not pg:
        return

    flavor = await inquirer.text(
        message="Aggiungi un contesto (opzionale, invio per saltare):",
    ).execute_async()

    while True:
        console.print("[dim]Generazione in corso…[/dim]")
        try:
            testo = await genera_descrizione(pg, flavor)
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
            return

        console.print(Panel(
            testo,
            title=f"📖 Descrizione di {pg.nome}",
            border_style="magenta",
            expand=False,
        ))

        scelta = await inquirer.select(
            message="La descrizione va bene?",
            choices=[
                {"name": "Sì, salva la descrizione", "value": "salva"},
                {"name": "No, rigenera con un contesto diverso", "value": "rigenera"},
                {"name": "Esci senza salvare", "value": "esci"},
            ],
        ).execute_async()

        if scelta == "salva":
            pg.descrizione = testo
            repo.save(pg)
            console.print(f"[green]✓ Descrizione salvata per {pg.nome}.[/green]")
            return
        elif scelta == "esci":
            return
        else:
            flavor = await inquirer.text(
                message="Aggiungi un contesto per la rigenerazione (opzionale):",
            ).execute_async()
