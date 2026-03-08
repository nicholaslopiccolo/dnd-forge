from dataclasses import dataclass, field
from constants import ClassiEnum, AttributoEnum, AbilitaEnum

import json
import os


@dataclass
class Classe:
    nome: ClassiEnum
    livello: int = 0
    
    # Armi e armature
    competence_armi: set[str] = field(default_factory=set)
    competence_armature: set[str] = field(default_factory=set)

    # Tiri salvezza
    tiri_salvezza: set[AttributoEnum] = field(default_factory=set)

    # Privilegi per livello
    privilegi: dict[int, list[str]] = field(default_factory=dict)

    # Competenze base (alcune classi)
    competenze_base: set[AbilitaEnum] = field(default_factory=set)

    # Abilità a scelta
    skills_choices_num: int = 0
    skills_choices_opzioni: set[AbilitaEnum] = field(default_factory=set)

    @classmethod
    def from_config(cls, nome: ClassiEnum) -> 'Classe':
        """Carica la classe dalla configurazione JSON se disponibile."""
        config_dir = os.path.join(os.path.dirname(__file__), "configurazioni")
        file_path = os.path.join(config_dir, f"{nome.value.lower()}.json")
        if os.path.exists(file_path):
            return carica_classe(file_path)
        return cls(nome=nome)

    def level_up(self, personaggio) -> None:
        self.livello += 1

        # Applica privilegi del livello
        for feat in self.privilegi.get(self.livello, []):
            personaggio.aggiungi_feature(feat)

        # Al primo livello: assegna competenze, armi, armature e tiri salvezza
        if self.livello == 1:
            personaggio.competenze.update(self.competenze_base)
            personaggio.armi.update(self.competence_armi)
            personaggio.armature.update(self.competence_armature)

            for attr_enum in self.tiri_salvezza:
                if attr_enum in personaggio.attributi:
                    personaggio.attributi[attr_enum].ts = True

            if self.skills_choices_num > 0:
                personaggio.scelta_abilita = {
                    "numero": self.skills_choices_num,
                    "opzioni": self.skills_choices_opzioni
                }

    def __str__(self) -> str:
        return f"{self.livello}° {self.nome.value}"


@dataclass
class AbilitaDiClasse:
    nome: str
    descrizione: str

    def __str__(self) -> str:
        return f"{self.nome}: {self.descrizione}"


def carica_classe(file_path: str) -> 'Classe':
    with open(file_path, "r", encoding="utf-8") as f:
        dati = json.load(f)

    return Classe(
        nome=ClassiEnum(dati["nome"]),
        competence_armi=set(dati.get("competence_armi", [])),
        competence_armature=set(dati.get("competence_armature", [])),
        tiri_salvezza={AttributoEnum[t] for t in dati.get("tiri_salvezza", [])},
        privilegi={int(lvl): feats for lvl, feats in dati.get("privilegi", {}).items()},
        competenze_base={AbilitaEnum[a] for a in dati.get("competenze_base", [])},
        skills_choices_num=dati.get("skills_choices", {}).get("numero", 0),
        skills_choices_opzioni={AbilitaEnum[a] for a in dati.get("skills_choices", {}).get("opzioni", [])}
    )