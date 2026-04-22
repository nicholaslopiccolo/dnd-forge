# dnd-forge — Project Specification

> **Tagline:** Forge your hero. Manage your campaign. Roll with confidence.

---

## Goal

`dnd-forge` is an open-source Python CLI toolkit for creating and managing D&D 5e character sheets programmatically. It supports full multiclass play, class-driven level-up logic, AI-generated character descriptions, and JSON-based persistence for campaign management.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| CLI shell | `prompt_toolkit` (with history) |
| Interactive prompts | `InquirerPy` |
| Terminal UI | `rich` |
| Persistence | JSON files (`saves/{id}.json`) |
| AI descriptions | Perplexity AI via OpenAI-compatible SDK |
| Data validation | `pydantic` (available, underused) |

---

## Architecture

```
src/cli/
├── main.py                  # Async CLI loop, prompt, entry point
├── commands/
│   ├── __init__.py          # @command() decorator, dispatch()
│   ├── pg.py                # All /pg subcommands (400+ lines, god file)
│   ├── help.py              # /help
│   └── exit.py              # /exit
├── models/
│   ├── constants.py         # Enums, EXP_LIVELLI, ASI_LIVELLI, STANDARD_ARRAY
│   ├── player.py            # Personaggio dataclass + Attributo + Abilita
│   └── classi/
│       ├── base.py          # Classe dataclass + carica_classe()
│       ├── classi.py        # get_classe() registry
│       └── configurazioni/
│           └── barbaro.json # Only class fully implemented
├── storage/
│   ├── repository.py        # save(), load(), list_all(), delete()
│   └── serializer.py        # to_dict(), from_dict()
├── utils/
│   ├── dadi.py              # d() dice roller
│   └── llm.py               # Perplexity AI integration
└── views/
    └── personaggio.py       # Rich panels: pg_panel(), pg_row()
```

---

## Features Implemented

### Character Creation (`/pg create`)
- Interactive guided flow via InquirerPy
- Name, class, race selection
- Attribute assignment: manual entry or standard array (15,14,13,12,10,8)
- Skill proficiency selection per class rules

### Multiclass Support
- Characters hold a `classi: dict[ClassiEnum, Classe]` with independent `livello` per class
- Total character level = sum of all class levels
- Display: `"1° Barbaro / 3° Mago / 9° Warlock"` via `classi_str` property
- HP calculation per class using class-specific `hp_dado`

### Level-Up & EXP System (`/pg xp`, `/pg levelup`)
- EXP thresholds for levels 1–20 (caps at 355,000 XP = level 20)
- Ability Score Improvement (ASI) at levels 4, 8, 12, 16, 19
- ASI: +2 to one attribute OR +1 to two different attributes (capped at 20)
- `pending_levelups()` computes earned but unprocessed levels from EXP

### Character Management
| Command | Description |
|---------|-------------|
| `/pg create` | Interactive character creation |
| `/pg list` | Browse saved characters; select active |
| `/pg status` / `/pg show` | Display character sheet |
| `/pg save` | Persist active character to disk |
| `/pg delete` | Remove character from disk |
| `/pg rename` | Change character name |
| `/pg xp <n>` | Add EXP, auto-trigger level-ups |
| `/pg levelup` | Manual level-up flow |
| `/pg describe` | AI-generated narrative description |
| `/help` | Show all commands |
| `/exit` | Exit CLI |

### AI Descriptions (`/pg describe`)
- Calls Perplexity AI (OpenAI-compatible) with character context
- Generates 150–200 word Italian narrative descriptions
- Interactive regeneration loop with hints
- Persists to save file

### Persistence
- `saves/{id}.json` stores full character state
- `Personaggio.from_saved()` classmethod reconstructs without re-triggering `__post_init__`
- `to_dict()` / `from_dict()` handle all enum serialization

### UI
- Rich `pg_panel()`: full character sheet with attributes, skills, HP, info panels
- Rich `pg_row()`: compact row for list view
- Emoji indicators, color-coded columns

---

## Class Configuration Schema

Classes are defined in `models/classi/configurazioni/*.json`:

```json
{
  "nome": "Barbaro",
  "hp_dado": 12,
  "armi": [...],
  "armature": [...],
  "tiri_salvezza": [...],
  "features": [...],
  "abilita": { "numero": 2, "scelte": [...] }
}
```

**Only `barbaro.json` is fully implemented.** Guerriero config is an empty dead file.

---

## Current Issues (from REFACTOR_PLAN.md)

| # | Issue | File | Status |
|---|-------|------|--------|
| 1 | God file 400+ lines mixing state/UI/logic | `commands/pg.py` | Open |
| 2 | `classi_str` duplicated inline in 4 places | Multiple | Steps 1–2 done in c1d9ed8 |
| 3 | `ASI_LIVELLI`, `STANDARD_ARRAY` not in constants | `constants.py` | Fixed in c1d9ed8 |
| 4 | Module-level side effects on import | `classi/classi.py` | Fixed in c1d9ed8 |
| 5 | Empty dead file | `classi/guerriero.py` | Open |
| 6 | `Personaggio.__new__()` in serializer | `serializer.py` | Fixed in c1d9ed8 |
| 7 | `_mostra_lista_personaggi()` never called | `commands/pg.py` | Open |
| 8 | `pg_show` is a wrapper duplicate of `pg_status` | `commands/pg.py` | Open |
| 9 | `_attr_table` declares 1 column, adds 4 cells/row | `views/personaggio.py` | Open |
| 10 | `_BASE_URL` hardcoded in LLM util | `utils/llm.py` | Open |

Refactoring steps 1–2 were completed in commit `c1d9ed8`. Steps 3–10 are pending.

---

## Environment

| Variable | Purpose | Default |
|----------|---------|---------|
| `PERPLEXITY_API_KEY` | Auth for AI descriptions | Required for `/pg describe` |
| `PERPLEXITY_BASE_URL` | Perplexity endpoint | `https://api.perplexity.ai` |

---

## Saved Characters (test data)

| ID | Name | Race | Classes | HP |
|----|------|------|---------|-----|
| 3 | Pulce | Gnomo | Barbaro 5 / Mago 3 / Warlock 9 | 94 |
| 4 | Spillo | Tiefling | Barbaro 10 | 98 |

---

## Non-Goals (current scope)

- No web UI or REST API
- No combat simulation
- No spell slot tracking
- No encounter management
- No multi-user / campaign server

---

## Pending Roadmap

1. **Complete refactoring steps 3–10** per `REFACTOR_PLAN.md`
2. **Add more class configs** (Guerriero, Mago, Warlock, etc.)
3. **Fix `_attr_table` layout bug** (1 declared column, 4 cells added)
4. **Split `commands/pg.py`** into focused submodules
5. **Add docstrings** to all public symbols per Step 10 of refactor plan
