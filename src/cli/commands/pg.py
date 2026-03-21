from commands import command, console
from InquirerPy import inquirer
from models.constants import ClassiEnum, AttributoEnum, AbilitaEnum
from models.player import Personaggio, Attributo
from rich.table import Table
from rich import box
from views.personaggio import pg_panel, pg_row

_personaggi: dict[int, Personaggio] = {}
_next_id = 1

@command("/pg create", "Crea un nuovo personaggio in modo guidato")
async def pg_create(_args):
    global _next_id

    # --- Nome ---
    nome = await inquirer.text(
        message="Nome del personaggio:",
        validate=lambda x: len(x.strip()) > 0,
        invalid_message="Il nome non può essere vuoto."
    ).execute_async()

    # --- Classe iniziale ---
    classe_iniziale = await inquirer.select(
        message="Scegli la classe iniziale:",
        choices=[{"name": c.value, "value": c} for c in ClassiEnum],
    ).execute_async()

    # --- Attributi: metodo di assegnazione ---
    metodo = await inquirer.select(
        message="Come vuoi assegnare gli attributi?",
        choices=[
            {"name": "Manuale (inserisci i valori)", "value": "manuale"},
            {"name": "Standard array (15,14,13,12,10,8)", "value": "standard"},
        ]
    ).execute_async()

    attributi = {}
    std_array = [15, 14, 13, 12, 10, 8]

    if metodo == "standard":
        console.print("\n[dim]Assegna i valori dello standard array a ciascun attributo.[/dim]")
        disponibili = std_array.copy()

        for attr in AttributoEnum:
            scelta = await inquirer.select(
                message=f"Valore per [cyan]{attr.value.upper()}[/cyan] (disponibili: {disponibili}):",
                choices=[{"name": str(v), "value": v} for v in disponibili],
            ).execute_async()
            attributi[attr] = Attributo(nome=attr.value, valore=scelta)
            disponibili.remove(scelta)
    else:
        console.print("\n[dim]Inserisci un valore tra 1 e 20 per ciascun attributo.[/dim]")
        for attr in AttributoEnum:
            valore = await inquirer.number(
                message=f"{attr.value.upper()}:",
                min_allowed=1,
                max_allowed=20,
                default=10,
            ).execute_async()
            attributi[attr] = Attributo(nome=attr.value, valore=int(valore))

    # --- Crea il personaggio (triggera __post_init__ e level_up) ---
    try:
        pg = Personaggio(
            nome=nome.strip(),
            classe_iniziale=classe_iniziale,
            attributi=attributi,
        )
    except Exception as e:
        console.print(f"[red]Errore nella creazione: {e}[/red]")
        return

    # --- Competenze abilità ---
    # Recupera le abilità disponibili dalla classe
    classe_obj = pg.classi[classe_iniziale]
    num_competenze = getattr(classe_obj, "num_competenze", 2)  # fallback a 2

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

    pg.competenze = set(scelte)

    # --- Salva ---
    _personaggi[_next_id] = pg
    _next_id += 1

    # --- Riepilogo ---

    # Vista dettagliata
    console.print(pg_panel(pg))

    # Vista lista
    table = Table(title="Personaggi", box=box.ROUNDED)
    for col in ("ID", "Nome", "Classe", "Livello", "EXP"):
        table.add_column(col)
    for p in _personaggi.values():
        table.add_row(*pg_row(p))
    console.print(table)

    console.print(f"[green]✓ Personaggio creato con successo![/green]")
