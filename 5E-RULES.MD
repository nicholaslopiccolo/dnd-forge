# D&D 5e Rules Reference — dnd-forge

This file documents every D&D 5e rule implemented in this codebase.
It is the authoritative rules gate: **before any new feature ships, validate it against this file.**

---

## 1. Ability Scores (Attributi)

| Rule | Value | Source |
|------|-------|--------|
| Six core attributes | Forza, Destrezza, Costituzione, Intelligenza, Saggezza, Carisma | SRD §Ability Scores |
| Default value | 10 | SRD |
| Valid range | 1–20 | SRD |
| Modifier formula | `(score - 10) // 2` | SRD |

**Implemented in:** `src/cli/models/player.py:16–22`, `src/cli/models/constants.py:26–32`

---

## 2. Proficiency Bonus (Bonus Competenza)

| Level | Bonus |
|-------|-------|
| 1–4 | +2 |
| 5–8 | +3 |
| 9–12 | +4 |
| 13–16 | +5 |
| 17–20 | +6 |

**Formula:** `2 + (total_level - 1) // 4`

**Implemented in:** `src/cli/models/player.py:108–109`

---

## 3. Skills (Abilità)

18 skills, each tied to one ability score. Skill bonus = `attribute_modifier + (proficiency_bonus if proficient else 0)`.

| Attribute | Skills |
|-----------|--------|
| Forza | Atletica |
| Destrezza | Acrobazia, Furtività, Rapidità di Mano |
| Intelligenza | Arcano, Indagare, Natura, Religione, Storia |
| Saggezza | Addestrare Animali, Intuizione, Medicina, Percezione, Sopravvivenza |
| Carisma | Ingannare, Intimidire, Intrattenere, Persuasione |

*Note: Costituzione has no associated skills per 5e SRD.*

**Implemented in:** `src/cli/models/player.py:28–41`, `src/cli/models/constants.py:34–52`

---

## 4. Experience & Level Progression

| Level | Total XP Required |
|-------|-------------------|
| 1 | 0 |
| 2 | 300 |
| 3 | 900 |
| 4 | 2,700 |
| 5 | 6,500 |
| 6 | 14,000 |
| 7 | 23,000 |
| 8 | 34,000 |
| 9 | 48,000 |
| 10 | 64,000 |
| 11 | 85,000 |
| 12 | 100,000 |
| 13 | 120,000 |
| 14 | 140,000 |
| 15 | 165,000 |
| 16 | 195,000 |
| 17 | 225,000 |
| 18 | 265,000 |
| 19 | 305,000 |
| 20 | 355,000 (max) |

**Implemented in:** `src/cli/models/constants.py:3–24`

---

## 5. Ability Score Improvements (ASI)

ASI scatta al **livello della singola classe**, non al livello totale del personaggio. Ogni classe ha il proprio schedule:

| Classe | Livelli ASI di classe |
|--------|-----------------------|
| Tutte tranne Guerriero e Ladro | 4, 8, 12, 16, 19 |
| Guerriero | **4, 6, 8, 12, 14, 16, 19** |
| Ladro | **4, 8, 10, 12, 16, 19** |

**Options (choose one):**
- +2 a un singolo attributo (cap 20)
- +1 a due attributi diversi (cap 20 ciascuno)

*Feats non implementati.*

Il check corretto è `pg.classi[classe].livello in pg.classi[classe].asi_livelli` — usa il livello della classe appena avanzata, non `pg.livello` totale.

**Implemented in:** `src/cli/models/constants.py` (`ASI_LIVELLI_DEFAULT`), `src/cli/models/classi/base.py` (campo `asi_livelli`), `src/cli/commands/pg.py:385`, `guerriero.json`, `ladro.json`

---

## 6. Hit Points & Hit Dice

| Level | HP Gained |
|-------|-----------|
| 1 | `hp_dado + CON modifier` (full max) |
| 2+ | `(hp_dado // 2 + 1) + CON modifier` (fixed average) |

**Minimum HP gain per level: 1** — `max(1, hp_gain)` is enforced. A character always gains at least 1 HP per level regardless of CON modifier.

**Implemented in:** `src/cli/models/classi/base.py:46–56`

---

## 7. Classes (Classi)

### 7.1 Barbarian (Barbaro) — FULLY CONFIGURED

| Property | Value |
|----------|-------|
| Hit die | d12 |
| Weapon proficiencies | ARMI_SEMPLICI, ARMI_MARZIALI |
| Armor proficiencies | ARMATURA_LEGGERA, ARMATURA_MEDIA, SCUDO |
| Saving throws | Forza, Costituzione |
| Skill choices | 2 from: Atletica, Addestrare Animali, Intimidire, Natura, Percezione, Sopravvivenza |

**Class features by level:**

| Level | Feature |
|-------|---------|
| 1 | Ira (Rage), Difesa Senza Armatura (Unarmored Defense) |
| 2 | Attacco Spericolato (Reckless Attack), Senso del Pericolo (Danger Sense) |
| 3 | Sentiero Primordiale (Primal Path — subclass) |
| 5 | Attacco Extra (Extra Attack), Movimento Rapido (Fast Movement) |
| 7 | Istinto Ferino (Feral Instinct) |
| 9 | Critico Brutale (Brutal Critical) |
| 11 | Ira Indomita (Relentless Rage) |
| 15 | Ira Persistente (Persistent Rage) |
| 18 | Forza Indomita (Indomitable Might) |
| 20 | Campione Primordiale (Primal Champion) |

### 7.2 Wizard (Mago) — PARTIALLY CONFIGURED

| Property | Value |
|----------|-------|
| Hit die | d6 |
| Weapon proficiencies | ARMI_SEMPLICI |
| Armor proficiencies | None |
| Saving throws | Intelligenza, Saggezza |
| Skill choices | 2 from: Arcano, Indagare, Intuizione, Medicina, Religione, Storia |

**Class features by level:**

| Level | Feature |
|-------|---------|
| 1 | Incantare (Spellcasting), Recupero Arcano (Arcane Recovery) |
| 2 | Tradizione Arcana (Arcane Tradition — subclass) |
| 6 | Caratteristica della Tradizione |
| 10 | Caratteristica della Tradizione |
| 14 | Caratteristica della Tradizione |
| 18 | Maestria degli Incantesimi (Spell Mastery) |
| 20 | Firma degli Incantesimi (Signature Spells) |

### 7.3 Warlock — PARTIALLY CONFIGURED

| Property | Value |
|----------|-------|
| Hit die | d8 |
| Weapon proficiencies | ARMI_SEMPLICI |
| Armor proficiencies | ARMATURA_LEGGERA |
| Saving throws | Saggezza, Carisma |
| Skill choices | 2 from: Arcano, Indagare, Ingannare, Intimidire, Natura, Religione, Storia |

**Class features by level:**

| Level | Feature |
|-------|---------|
| 1 | Patrono Sovrannaturale (Otherworldly Patron), Magia del Patto (Pact Magic) |
| 2 | Invocazioni Occulte (Eldritch Invocations) |
| 3 | Dono del Patto (Pact Boon) |
| 6 | Capacità del Patrono |
| 10 | Capacità del Patrono |
| 11 | Arcanum Mistico (6th level) |
| 13 | Arcanum Mistico (7th level) |
| 14 | Capacità del Patrono |
| 15 | Arcanum Mistico (8th level) |
| 17 | Arcanum Mistico (9th level) |
| 20 | Padrone Supremo (Eldritch Master) |

---

## 8. Multiclass Rules

- Each class levels independently within a character.
- **Total character level** = sum of all class levels.
- HP from each class is accumulated using that class's `hp_dado`.
- Proficiency bonus is always calculated from total character level, not a single class level.

**Cosa NON si ottiene al multiclasse (SRD PHB p.163):**
- Tiri salvezza della nuova classe — **mai**, per nessuna classe
- Competenze base automatiche (`competenze_base`) — sostituite dal meccanismo `multiclass_skills_*`
- Skill metadata di creazione (`skills_choices`) — inutilizzate al multiclasse

**Implemented in:** `src/cli/models/classi/base.py:99–109` (flag `is_multiclasse`)

### 8.1 Prerequisites (Prerequisiti Multiclasse) — ENFORCED

Minimum ability score requirements to enter a class via multiclassing (SRD Table 6-1). All values confirmed against SRD:

| Classe | Tipo | Prerequisito |
|--------|------|-------------|
| Artefice | AND | INT ≥ 13 |
| Barbaro | AND | FOR ≥ 13 |
| Bardo | AND | CAR ≥ 13 |
| Chierico | AND | SAG ≥ 13 |
| Druido | AND | SAG ≥ 13 |
| Guerriero | OR | FOR ≥ 13 **oppure** DES ≥ 13 |
| Ladro | AND | DES ≥ 13 |
| Mago | AND | INT ≥ 13 |
| Monaco | AND | DES ≥ 13 **e** SAG ≥ 13 |
| Paladino | AND | FOR ≥ 13 **e** CAR ≥ 13 |
| Ranger | AND | DES ≥ 13 **e** SAG ≥ 13 |
| Stregone | AND | CAR ≥ 13 |
| Warlock | AND | CAR ≥ 13 |

- AND prerequisites: tutti devono essere soddisfatti contemporaneamente.
- OR prerequisites: almeno uno deve essere soddisfatto (Guerriero è l'unico caso attuale).
- La scelta di classe è disabilitata nella UI se i prerequisiti non sono soddisfatti.

**Implemented in:** `src/cli/models/classi/base.py:54–70`, JSON `prerequisiti_multiclasse_and` / `prerequisiti_multiclasse_or`

### 8.2 Skill Proficiencies Gained at Multiclass (SRD Table 6-1)

When a character enters a new class for the first time via multiclassing, they gain these skill proficiencies (cannot duplicate already-held proficiencies):

| Classe | N. | Opzioni |
|--------|-----|---------|
| Artefice | 0 | — |
| Barbaro | 1 | Atletica, Addestrare Animali, Intimidire, Natura, Percezione, Sopravvivenza |
| Bardo | 1 | Qualsiasi abilità (tutte e 18) |
| Chierico | 0 | — |
| Druido | 0 | — |
| Guerriero | 1 | Acrobazia, Addestrare Animali, Atletica, Storia, Intuizione, Intimidire, Percezione, Sopravvivenza |
| Ladro | 1 | Acrobazia, Atletica, Ingannare, Intuizione, Intimidire, Indagare, Percezione, Intrattenere, Persuasione, Rapidità di Mano, Furtività |
| Mago | 0 | — |
| Monaco | 1 | Acrobazia, Atletica, Storia, Intuizione, Religione, Furtività |
| Paladino | 0 | — |
| Ranger | 1 | Addestrare Animali, Atletica, Intuizione, Indagare, Natura, Percezione, Furtività, Sopravvivenza |
| Stregone | 0 | — |
| Warlock | 1 | Arcano, Ingannare, Storia, Intimidire, Indagare, Natura, Religione |

**Armi al multiclasse — regola critica (SRD Table 6-1):**

8 classi non concedono alcuna arma al multiclasse (solo alla classe di partenza):

| Classe | Armi inizio classe | Armi via multiclasse |
|--------|-------------------|---------------------|
| Artefice | ARMI_SEMPLICI | **nessuna** |
| Bardo | ARMI_SEMPLICI + 4 specifiche | **nessuna** |
| Chierico | ARMI_SEMPLICI | **nessuna** |
| Druido | ARMI_SEMPLICI | **nessuna** |
| Ladro | ARMI_SEMPLICI + 4 specifiche | **nessuna** |
| Mago | ARMI_SEMPLICI | **nessuna** |
| Stregone | ARMI_SEMPLICI | **nessuna** |
| Warlock | ARMI_SEMPLICI | **nessuna** |
| Barbaro, Guerriero, Monaco, Paladino, Ranger | stessa lista | stessa lista ✓ |

**Armature al multiclasse — regola critica (SRD Table 6-1):**

Tre classi concedono meno armature al multiclasse rispetto alla classe di partenza:

| Classe | Armature inizio classe | Armature via multiclasse |
|--------|------------------------|--------------------------|
| Barbaro | Leggera, Media, Scudo | **Scudo soltanto** |
| Guerriero | Leggera, Media, Pesante, Scudo | Leggera, Media, Scudo (**no Pesante**) |
| Paladino | Leggera, Media, Pesante, Scudo | Leggera, Media, Scudo (**no Pesante**) |
| Tutte le altre | stessa lista | stessa lista ✓ |

Implementato via campi JSON `competence_armi_multiclasse` / `competence_armature_multiclasse` e flag `is_multiclasse` propagato `pg.py → player.py → base.py`.

**Implemented in:** `src/cli/commands/pg.py:376–383`, JSON `competenze_multiclasse`

### 8.3 Serializzazione dei campi di configurazione

I campi di configurazione pura vengono **sempre ricaricati dal JSON della classe** tramite `Classe.from_config()` al load — non dal save file. Lo stato mutabile (`livello`, competenze acquisite) proviene dal save.

**Campi config-only (non scritti nel save, ricaricati da JSON):**
- `hp_dado` — evita save corrotti con `hp_dado: 0`
- `asi_livelli`
- `competence_armi_multiclasse`
- `competence_armature_multiclasse`
- `prerequisiti_and` / `prerequisiti_or`
- `multiclass_skills_num` / `multiclass_skills_opzioni`

Questo garantisce backward-compatibility con save precedenti e mantiene i valori sincronizzati con le config aggiornate.

**Nota save corrotti pre-fix:** `saves/6.json` (GUERRIERO `hp_dado: 0`) e `saves/7.json` (FORZA `ts: true` e `ARMATURA_PESANTE` errati) contengono dati pre-fix. I campi config-only vengono corretti automaticamente al load; lo stato mutabile corrotto (TS e armature errati in 7.json) persiste — si raccomanda di ricreare quei personaggi.

**Implemented in:** `src/cli/storage/serializer.py:from_dict()`

### 8.4 ASI per classe (fixed)

L'ASI si basa sul **livello della singola classe** (`pg.classi[classe].livello`), non sul livello totale. Ogni classe ha il proprio schedule in `asi_livelli` (frozenset):
- Default (tutte le classi tranne Guerriero e Ladro): `{4, 8, 12, 16, 19}`
- Guerriero: `{4, 6, 8, 12, 14, 16, 19}`
- Ladro: `{4, 8, 10, 12, 16, 19}`

**Implemented in:** `src/cli/commands/pg.py:385`, `src/cli/models/constants.py:90`

---

## 9. Attribute Assignment Methods

### Standard Array (Distribuzione Standard)
Predefined values: **15, 14, 13, 12, 10, 8** — each assigned to one ability score, no repeats.

### Manual Assignment (Inserimento Manuale)
Any integer 1–20 per attribute. No point-buy budget enforced.

**Implemented in:** `src/cli/models/constants.py:93`, `src/cli/commands/pg.py:54–83`

---

## 10. Dice System

- Single die roll: `d(n)` → `random.randint(1, n)`
- Used for HP generation.
- No advantage/disadvantage mechanic yet.

**Implemented in:** `src/cli/utils/dadi.py`

---

## 11. Races (Razze) — Cosmetic Only

Ten races available: Umano, Elfo, Nano, Halfling, Gnomo, Mezzorco, Tiefling, Dragonide, Mezzelfo.

**Not implemented:** Racial ability score adjustments, racial traits, darkvision, resistances, languages, speed.

---

## 12. Hardcoded Rules Values

| Constant | Value | Rule Reference |
|----------|-------|----------------|
| ASI trigger levels | 4, 8, 12, 16, 19 | SRD class tables |
| Standard array | 15, 14, 13, 12, 10, 8 | SRD Character Creation |
| Ability score cap | 20 | SRD |
| Max character level | 20 | SRD |
| Max XP | 355,000 | SRD level table |
| Proficiency bonus | `2 + (level - 1) // 4` | SRD |
| Ability modifier | `(score - 10) // 2` | SRD |
| HP at level 1 | `hp_dado + CON mod` | SRD |
| HP at level 2+ | `(hp_dado // 2 + 1) + CON mod` | SRD average roll |
| HP minimum per level | 1 | SRD |
| Multiclass prereq — Barbaro | FOR ≥ 13 | SRD Table 6-1 |
| Multiclass prereq — Mago | INT ≥ 13 | SRD Table 6-1 |
| Multiclass prereq — Warlock | CAR ≥ 13 | SRD Table 6-1 |

---

## 13. NOT IMPLEMENTED (Out of Scope)

The following 5e mechanics are **not yet in scope**. Do not implement them without updating this document and getting rules validation first.

- Combat: attack rolls, damage, AC, initiative, action economy
- Spells: spell slots, spell lists, spell save DC, concentration
- Feats
- Short rest / Long rest / Hit dice recovery
- Conditions (blinded, charmed, frightened, etc.)
- Racial ability score bonuses and racial traits
- Subclass mechanical effects
- Equipment stats (weapon damage, armor AC bonus)
- Flanking, cover, range, movement in combat
- Passive checks (Passive Perception, etc.)
- Contested checks

---

## Feature Validation Checklist

Before merging any new feature, confirm:

- [ ] Terminology matches D&D 5e SRD usage (in Italian translation)
- [ ] Ability modifier formula is `(score - 10) // 2`
- [ ] Proficiency bonus uses total character level, not single-class level
- [ ] Ability score cap of 20 is enforced where modified
- [ ] HP formula matches §6 above
- [ ] ASI triggers only at levels 4, 8, 12, 16, 19
- [ ] New class feature levels match the official 5e class table
- [ ] Multiclass HP accumulates correctly per class hit die
- [ ] XP thresholds match the level table in §4
- [ ] Skills map to the correct ability scores per §3
- [ ] Any new rule not in this document is added here before implementation
