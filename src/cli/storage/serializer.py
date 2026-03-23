"""
Serializzazione/deserializzazione di Personaggio da/verso dict JSON-compatibile.
"""
from __future__ import annotations

from models.constants import AbilitaEnum, AttributoEnum, ClassiEnum, RazzaEnum
from models.player import Attributo, Personaggio
from models.classi.base import Classe


def to_dict(pg: Personaggio) -> dict:
    return {
        "id": pg.id,
        "nome": pg.nome,
        "classe_iniziale": pg.classe_iniziale.name,
        "razza": pg.razza.name if pg.razza else None,
        "livello": pg.livello,
        "exp": pg.exp,
        "hp": pg.hp,
        "attributi": {
            attr.name: {"valore": a.valore, "ts": a.ts}
            for attr, a in pg.attributi.items()
        },
        "competenze": [a.name for a in pg.competenze],
        "armi": list(pg.armi),
        "armature": list(pg.armature),
        "tiri_salvezza": [a.name for a in pg.tiri_salvezza],
        "classi": {
            c.nome.name: {
                "livello": c.livello,
                "hp_dado": c.hp_dado,
                "competence_armi": list(c.competence_armi),
                "competence_armature": list(c.competence_armature),
                "tiri_salvezza": [t.name for t in c.tiri_salvezza],
                "privilegi": {str(k): v for k, v in c.privilegi.items()},
                "skills_choices_num": c.skills_choices_num,
                "skills_choices_opzioni": [a.name for a in c.skills_choices_opzioni],
                "competenze_base": [a.name for a in c.competenze_base],
            }
            for c in pg.classi.values()
        },
        "descrizione": pg.descrizione,
    }


def from_dict(d: dict) -> Personaggio:
    classe_iniziale = ClassiEnum[d["classe_iniziale"]]
    razza = RazzaEnum[d["razza"]] if d.get("razza") else None

    attributi = {
        AttributoEnum[k]: Attributo(
            nome=AttributoEnum[k].value,
            valore=v["valore"],
            ts=v["ts"],
        )
        for k, v in d["attributi"].items()
    }

    classi = {}
    for nome_str, cd in d["classi"].items():
        nome_enum = ClassiEnum[nome_str]
        classi[nome_enum] = Classe(
            nome=nome_enum,
            livello=cd["livello"],
            hp_dado=cd["hp_dado"],
            competence_armi=set(cd["competence_armi"]),
            competence_armature=set(cd["competence_armature"]),
            tiri_salvezza={AttributoEnum[t] for t in cd["tiri_salvezza"]},
            privilegi={int(k): v for k, v in cd["privilegi"].items()},
            skills_choices_num=cd["skills_choices_num"],
            skills_choices_opzioni={AbilitaEnum[a] for a in cd["skills_choices_opzioni"]},
            competenze_base={AbilitaEnum[a] for a in cd["competenze_base"]},
        )

    pg = Personaggio.__new__(Personaggio)
    pg.id = d["id"]
    pg.nome = d["nome"]
    pg.classe_iniziale = classe_iniziale
    pg.razza = razza
    pg.livello = d["livello"]
    pg.exp = d["exp"]
    pg.hp = d["hp"]
    pg.attributi = attributi
    pg.competenze = {AbilitaEnum[a] for a in d["competenze"]}
    pg.armi = set(d["armi"])
    pg.armature = set(d["armature"])
    pg.tiri_salvezza = {AttributoEnum[a] for a in d["tiri_salvezza"]}
    pg.classi = classi
    pg.scelta_abilita = {}
    pg.descrizione = d.get("descrizione", "")
    return pg
