"""
Integrazione Perplexity AI per la generazione della descrizione del personaggio.
Richiede la variabile d'ambiente PERPLEXITY_API_KEY.
"""
from __future__ import annotations
import os
from models.player import Personaggio

_BASE_URL = "https://api.perplexity.ai"
MODEL = os.getenv("DND_LLM_MODEL", "sonar-pro")


def _build_system_prompt(pg: Personaggio) -> str:
    classi = ", ".join(f"{c.nome.value} (livello {c.livello})" for c in pg.classi.values())
    razza = pg.razza.value if pg.razza else "sconosciuta"
    attributi = "  ".join(
        f"{attr.value[:3].upper()} {a.valore} ({a.modificatore:+})"
        for attr, a in pg.attributi.items()
    )
    competenze = ", ".join(ab.label for ab in pg.competenze) if pg.competenze else "nessuna"

    return (
        "Sei un narratore fantasy esperto nel mondo di Dungeons & Dragons 5a edizione. "
        "Il tuo compito è scrivere una descrizione narrativa, evocativa e in prima persona "
        "del personaggio che ti viene descritto. La descrizione deve essere in italiano, "
        "lunga circa 150-200 parole, e deve riflettere la classe, la razza e i valori del personaggio."
        "Non includere i punteggi numerici degli attributi nella descrizione ma usali per descrivere al meglio il personaggio. "
        "Non includere riferimenti bibliografici, note a piè di pagina, citazioni numeriche come [1] o [2], "
        "né alcun tipo di markup di citazione. Scrivi solo testo narrativo puro.\n\n"
        f"**Personaggio:**\n"
        f"- Nome: {pg.nome}\n"
        f"- Razza: {razza}\n"
        f"- Classe/i: {classi}\n"
        f"- Livello totale: {pg.livello}\n"
        f"- Attributi: {attributi}\n"
        f"- Competenze nelle abilità: {competenze}\n"
        f"- HP: {pg.hp}\n"
    )


async def genera_descrizione(pg: Personaggio, flavor: str = "") -> str:
    try:
        from openai import AsyncOpenAI
    except ImportError:
        raise RuntimeError(
            "La libreria 'openai' non è installata. Esegui: pip install openai"
        )

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Variabile d'ambiente PERPLEXITY_API_KEY non impostata."
        )

    client = AsyncOpenAI(api_key=api_key, base_url=_BASE_URL)

    user_message = flavor.strip() if flavor.strip() else (
        "Scrivi una descrizione del mio personaggio come se stesse presentandosi all'inizio di un'avventura."
    )

    response = await client.chat.completions.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {"role": "system", "content": _build_system_prompt(pg)},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content
