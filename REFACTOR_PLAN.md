# Piano di Refactoring — dnd-forge `src/cli`

> **Destinatario:** agente automatico di refactoring  
> **Principio guida:** nessun cambio funzionale, solo miglioramento di struttura, leggibilità e manutenibilità.  
> **Ordine di esecuzione:** rispetta la sequenza numerica; ogni step dipende dai precedenti.

---

## Contesto e problemi identificati

| # | File | Problema |
|---|------|----------|
| 1 | `commands/pg.py` | File "god" da 400+ righe: mescola stato globale, logica UI, business logic e display |
| 2 | Multipli file | `classi_str` del personaggio è inline in 4 posti diversi con formati diversi |
| 3 | `models/constants.py` | Mancano `ASI_LIVELLI` e `STANDARD_ARRAY`, definiti in `commands/pg.py` |
| 4 | `models/classi/classi.py` | Effetto collaterale a importazione: `carica_classe(...)` chiamata a livello di modulo |
| 5 | `models/classi/guerriero.py` | File vuoto — dead code |
| 6 | `storage/serializer.py` | Usa `Personaggio.__new__()` per bypassare `__post_init__` — code smell |
| 7 | `commands/pg.py` | `_mostra_lista_personaggi()` definita ma mai chiamata — dead code |
| 8 | `commands/pg.py` | `pg_show` è un wrapper vuoto intorno a `pg_status` — ridondante |
| 9 | `views/personaggio.py` | `_attr_table` aggiunge 4 celle per riga ma dichiara 1 colonna — bug latente |
| 10 | `utils/llm.py` | `_BASE_URL` hardcoded; `MODEL` letto da env a livello di modulo; import lazy inconsistente |

---

## Step 1 — `models/constants.py`: centralizza le costanti mancanti

**Cosa fare:** aggiungere in fondo al file le due costanti oggi sparse in `commands/pg.py`.

```python
# Livelli a cui scatta l'Ability Score Improvement
ASI_LIVELLI: frozenset[int] = frozenset({4, 8, 12, 16, 19})

# Standard Array per l'assegnazione degli attributi
STANDARD_ARRAY: tuple[int, ...] = (15, 14, 13, 12, 10, 8)
```

Usa `frozenset` per `ASI_LIVELLI` (lookup O(1), immutabile) e `tuple` per `STANDARD_ARRAY` (ordinato, immutabile).

---

## Step 2 — `models/player.py`: aggiungi `classi_str` e `Personaggio.from_saved()`

### 2a — Property `classi_str`

Aggiungere alla classe `Personaggio` la property:

```python
@property
def classi_str(self) -> str:
    """Stringa compatta delle classi: es. '1° Guerriero / 2° Mago'"""
    return " / ".join(f"{c.livello}° {c.nome.value}" for c in self.classi.values())
```

Questo elimina le 4 implementazioni inline sparse in `main.py`, `commands/pg.py`, `views/personaggio.py`, `utils/llm.py`.

### 2b — Classmethod `Personaggio.from_saved()`

Aggiungere il classmethod per la deserializzazione, che permette di costruire un `Personaggio` da dati già processati senza ri-eseguire `__post_init__`:

```python
@classmethod
def from_saved(
    cls,
    *,
    id: int,
    nome: str,
    classe_iniziale: "ClassiEnum",
    razza: "RazzaEnum | None",
    livello: int,
    exp: int,
    hp: int,
    attributi: "dict[AttributoEnum, Attributo]",
    competenze: "set[AbilitaEnum]",
    armi: set[str],
    armature: set[str],
    tiri_salvezza: "set[AttributoEnum]",
    classi: "dict[ClassiEnum, Classe]",
    descrizione: str,
) -> "Personaggio":
    """Factory per ricostruire un personaggio da dati già persistiti (bypassa __post_init__)."""
    obj = cls.__new__(cls)
    obj.id = id
    obj.nome = nome
    obj.classe_iniziale = classe_iniziale
    obj.razza = razza
    obj.livello = livello
    obj.exp = exp
    obj.hp = hp
    obj.attributi = attributi
    obj.competenze = competenze
    obj.armi = armi
    obj.armature = armature
    obj.tiri_salvezza = tiri_salvezza
    obj.classi = classi
    obj.scelta_abilita = {}
    obj.descrizione = descrizione
    return obj
```

Il bypass di `__post_init__` è *legittimo* qui: lo stato viene fornito già completo dal serializer. Renderlo esplicito con un classmethod chiarisce l'intento e rimuove la chiamata "magica" a `__new__` dal serializer.

---

## Step 3 — `storage/serializer.py`: usa `Personaggio.from_saved()`

Nella funzione `from_dict`, sostituire il blocco di assegnazioni manuali post-`__new__`:

**Da eliminare (blocco attuale):**
```python
pg = Personaggio.__new__(Personaggio)
pg.id = d["id"]
pg.nome = d["nome"]
# ... tutte le assegnazioni manuali
pg.scelta_abilita = {}
pg.descrizione = d.get("descrizione", "")
return pg
```

**Con:**
```python
return Personaggio.from_saved(
    id=d["id"],
    nome=d["nome"],
    classe_iniziale=classe_iniziale,
    razza=razza,
    livello=d["livello"],
    exp=d["exp"],
    hp=d["hp"],
    attributi=attributi,
    competenze={AbilitaEnum[a] for a in d["competenze"]},
    armi=set(d["armi"]),
    armature=set(d["armature"]),
    tiri_salvezza={AttributoEnum[a] for a in d["tiri_salvezza"]},
    classi=classi,
    descrizione=d.get("descrizione", ""),
)
```

---

## Step 4 — `views/personaggio.py`: usa `classi_str`, correggi `_attr_table`

### 4a — Usa la property centralizzata

Sostituire tutte le occorrenze inline di classi-join con `pg.classi_str`:

- `_classi_str(pg)` diventa semplicemente `pg.classi_str`; la funzione helper `_classi_str` va rimossa.

### 4b — Correggi `_attr_table`

Il metodo aggiunge 4 celle (`attr`, `valore`, `modificatore`, `ts`) per riga, ma dichiara solo 1 colonna (`add_column("Attributi")`). Aggiungere le 3 colonne mancanti:

```python
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
```

---

## Step 5 — `commands/pg.py`: import costanti, rimuovi dead code, semplifica

### 5a — Import da constants

Rimuovere le definizioni locali e importare:
```python
# Prima (da rimuovere):
ASI_LIVELLI = {4, 8, 12, 16, 19}
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# Dopo:
from models.constants import ASI_LIVELLI, STANDARD_ARRAY
```

### 5b — Rimuovi `_mostra_lista_personaggi`

La funzione è definita ma **mai chiamata** (il comando `/pg list` costruisce la propria tabella inline). Eliminarla.

### 5c — Rimuovi `pg_show` come alias ridondante

`pg_show` è identico a `pg_status`. Sostituire:
```python
@command("/pg show", "Alias di /pg status")
async def pg_show(_args):
    await pg_status(_args)
```
Con una registrazione diretta dello stesso handler:
```python
# Registra pg_status anche come /pg show
command("/pg show", "Mostra la scheda del personaggio attivo (alias di /pg status)")(pg_status)
```

Oppure, se si preferisce chiarezza, mantenere il wrapper ma documentarlo esplicitamente.

### 5d — Usa `pg.classi_str` nella choice list di `/pg list`

```python
# Prima:
"name": f"[{p.id}] {p.nome} — {' / '.join(f'{c.nome.value} {c.livello}' for c in p.classi.values())}",

# Dopo:
"name": f"[{p.id}] {p.nome} — {p.classi_str}",
```

### 5e — Semplifica `pg_xp` con guard clause

```python
# Prima:
try:
    amount = int(args[0])
except ValueError:
    console.print(...)
    return
if amount <= 0:
    console.print(...)
    return

# Dopo (guard clauses):
try:
    amount = int(args[0])
    if amount <= 0:
        raise ValueError
except ValueError:
    console.print(f"[red]'{args[0]}' non è un numero valido o positivo.[/red]")
    return
```

---

## Step 6 — `main.py`: usa `pg.classi_str`

Nella funzione `_make_prompt`:

```python
# Prima:
classe_str = " / ".join(f"{c.nome.value} {c.livello}" for c in pg.classi.values())
return f"🎲 [{pg.nome} · {classe_str}] > "

# Dopo:
return f"🎲 [{pg.nome} · {pg.classi_str}] > "
```

---

## Step 7 — `utils/llm.py`: usa `classi_str`, rendi `_BASE_URL` configurabile

### 7a — Usa la property centralizzata

```python
# Prima:
classi = ", ".join(f"{c.nome.value} (livello {c.livello})" for c in pg.classi.values())

# Dopo:
classi = pg.classi_str
```

### 7b — Rendi `_BASE_URL` configurabile via env var

```python
# Prima:
_BASE_URL = "https://api.perplexity.ai"

# Dopo:
_BASE_URL = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")
```

### 7c — Normalizza import di `openai`

Spostare l'import di `openai` in cima al file, con gestione dell'ImportError a livello di funzione solo se si vuole mantenere il lazy import. Altrimenti importare in cima con messaggio chiaro:

```python
try:
    from openai import AsyncOpenAI
except ImportError as exc:
    raise ImportError(
        "La libreria 'openai' non è installata. Esegui: pip install openai"
    ) from exc
```

---

## Step 8 — `models/classi/classi.py`: rimuovi effetti collaterali

Il file oggi esegue `carica_classe(...)` a livello di modulo (al momento dell'`import`), il che causa un errore se il JSON non esiste o il CWD è sbagliato.

**Soluzione:** trasformare in un registry lazy:

```python
# Prima:
Barbaro = carica_classe(Path(__file__).parent / "configurazioni" / "barbaro.json")

# Dopo:
from .base import Classe
from ..constants import ClassiEnum

def get_classe(nome: ClassiEnum) -> Classe:
    """Restituisce un'istanza di Classe dalla configurazione JSON."""
    return Classe.from_config(nome)
```

Oppure, se il file non serve a nulla (dato che `Classe.from_config` in `base.py` già gestisce il caricamento), **eliminare `classi.py` del tutto** e aggiornare eventuali import.

---

## Step 9 — `models/classi/guerriero.py`: rimuovi file vuoto

Il file è vuoto. Va eliminato. Verificare che nessun modulo lo importi prima di eliminarlo.

---

## Step 10 — Docstring "ready to document"

Aggiungere docstring minime (una riga) alle funzioni/classi pubbliche prive di documentazione:

| Simbolo | File | Docstring suggerita |
|---------|------|---------------------|
| `Personaggio` | `models/player.py` | `"""Rappresenta un personaggio giocante (PG) di D&D 5e."""` |
| `Attributo` | `models/player.py` | `"""Un attributo base del PG (es. Forza, Destrezza)."""` |
| `Abilita` | `models/player.py` | `"""Un'abilità derivata da un attributo base."""` |
| `Classe` | `models/classi/base.py` | `"""Configurazione di una classe D&D per un PG."""` |
| `carica_classe` | `models/classi/base.py` | `"""Deserializza una Classe da file JSON di configurazione."""` |
| `to_dict` | `storage/serializer.py` | `"""Serializza un Personaggio in un dict JSON-compatibile."""` |
| `from_dict` | `storage/serializer.py` | `"""Deserializza un Personaggio da un dict JSON."""` |
| `save` | `storage/repository.py` | `"""Persiste il PG su disco, assegnando un ID se necessario."""` |
| `load` | `storage/repository.py` | `"""Carica un PG dal disco tramite ID."""` |
| `list_all` | `storage/repository.py` | `"""Restituisce tutti i PG salvati, ordinati per ID."""` |
| `genera_descrizione` | `utils/llm.py` | `"""Genera una descrizione narrativa del PG via LLM."""` |
| `pg_panel` | `views/personaggio.py` | `"""Costruisce il pannello Rich completo per la visualizzazione del PG."""` |
| `pg_row` | `views/personaggio.py` | `"""Restituisce una tupla di stringhe per la riga nella tabella lista PG."""` |

---

## Riepilogo delle modifiche per file

| File | Azione |
|------|--------|
| `models/constants.py` | Aggiunta `ASI_LIVELLI`, `STANDARD_ARRAY` |
| `models/player.py` | Aggiunta property `classi_str`, classmethod `from_saved()`, docstring |
| `models/classi/base.py` | Docstring su `Classe` e `carica_classe` |
| `models/classi/classi.py` | Rimozione effetti collaterali o eliminazione file |
| `models/classi/guerriero.py` | **Eliminare** (file vuoto) |
| `storage/serializer.py` | Usa `Personaggio.from_saved()`, docstring |
| `storage/repository.py` | Docstring |
| `commands/pg.py` | Import costanti da `constants`, rimozione dead code, usa `classi_str`, semplifica guard clause |
| `views/personaggio.py` | Rimozione `_classi_str()`, usa `pg.classi_str`, fix `_attr_table`, docstring |
| `main.py` | Usa `pg.classi_str` |
| `utils/llm.py` | Usa `pg.classi_str`, `_BASE_URL` da env, normalizza import |

---

## Invarianti da rispettare

- Nessun cambio al comportamento runtime
- Nessuna nuova dipendenza esterna
- Tutti i file JSON di configurazione in `models/classi/configurazioni/` restano invariati
- Il formato di salvataggio JSON (`saves/*.json`) NON cambia: `to_dict` / `from_dict` devono produrre/leggere lo stesso schema
- I comandi CLI registrati (`/pg create`, `/pg list`, ecc.) restano identici
