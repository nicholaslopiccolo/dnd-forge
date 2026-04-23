from dataclasses import dataclass, field
from ..constants import ClassiEnum, AttributoEnum, AbilitaEnum, ASI_LIVELLI_DEFAULT

import json
from pathlib import Path


@dataclass
class Classe:
    """Configurazione di una classe D&D per un PG."""
    nome: ClassiEnum
    livello: int = 0
    hp_dado: int = 0

    # Armi e armature
    competence_armi: set[str] = field(default_factory=set)
    competence_armi_multiclasse: set[str] = field(default_factory=set)
    competence_armature: set[str] = field(default_factory=set)

    # Tiri salvezza
    tiri_salvezza: set[AttributoEnum] = field(default_factory=set)

    # Privilegi per livello
    privilegi: dict[int, list[str]] = field(default_factory=dict)

    # Competenze base (alcune classi)
    competenze_base: set[AbilitaEnum] = field(default_factory=set)

    # Abilità a scelta (creazione iniziale)
    skills_choices_num: int = 0
    skills_choices_opzioni: set[AbilitaEnum] = field(default_factory=set)

    # Armature ottenute solo al multiclasse (sottoinsieme di competence_armature)
    competence_armature_multiclasse: set[str] = field(default_factory=set)

    # Livelli di classe a cui scatta l'ASI (per-class, non per total level)
    asi_livelli: frozenset[int] = field(default_factory=frozenset)

    # Prerequisiti per il multiclasse (AND = tutti; OR = almeno uno)
    prerequisiti_and: dict[AttributoEnum, int] = field(default_factory=dict)
    prerequisiti_or: dict[AttributoEnum, int] = field(default_factory=dict)

    # Abilità guadagnate al multiclasse
    multiclass_skills_num: int = 0
    multiclass_skills_opzioni: set[AbilitaEnum] = field(default_factory=set)

    @classmethod
    def from_config(cls, nome: ClassiEnum) -> 'Classe':
        """Carica la classe dalla configurazione JSON se disponibile."""
        file_path = Path(__file__).parent / "configurazioni" / f"{nome.value.lower()}.json"
        if file_path.exists():
            return carica_classe(file_path)
        return cls(nome=nome)

    @staticmethod
    def has_config(nome: ClassiEnum) -> bool:
        """Returns True if a JSON configuration file exists for this class."""
        file_path = Path(__file__).parent / "configurazioni" / f"{nome.value.lower()}.json"
        return file_path.exists()

    def verifica_prerequisiti(self, personaggio) -> tuple[bool, str]:
        """Checks multiclassing prerequisites. Returns (soddisfatti, motivo_negazione)."""
        for attr, minimo in self.prerequisiti_and.items():
            valore = personaggio.attributi[attr].valore
            if valore < minimo:
                return False, f"{attr.value[:3].upper()} {valore} < {minimo}"

        if self.prerequisiti_or:
            if not any(
                personaggio.attributi[attr].valore >= minimo
                for attr, minimo in self.prerequisiti_or.items()
            ):
                nomi = "/".join(a.value[:3].upper() for a in self.prerequisiti_or)
                minimo = next(iter(self.prerequisiti_or.values()))
                return False, f"serve {nomi} ≥ {minimo}"

        return True, ""

    def level_up(self, personaggio, is_multiclasse: bool = False) -> None:
        """Applica un livello alla classe: incrementa livello, calcola HP, assegna competenze al Lv1."""
        self.livello += 1

        # Calcola e aggiunge HP
        con_mod = personaggio.attributi[AttributoEnum.COSTITUZIONE].modificatore
        if self.livello == 1:
            hp_gain = self.hp_dado + con_mod  # massimo al primo livello
        else:
            hp_gain = self.hp_dado // 2 + 1 + con_mod  # media livelli successivi
        personaggio.hp += max(1, hp_gain)

        # Applica privilegi del livello
        for feat in self.privilegi.get(self.livello, []):
            personaggio.aggiungi_feature(feat)

        # Al primo livello: assegna competenze, armi, armature e tiri salvezza
        if self.livello == 1:
            # competenze_base: solo alla classe di partenza (SRD p.163: non concesse al multiclasse)
            if not is_multiclasse:
                personaggio.competenze.update(self.competenze_base)
            # Al multiclasse si ottiene solo il sottoinsieme SRD-consentito (Table 6-1)
            armi = self.competence_armi_multiclasse if is_multiclasse else self.competence_armi
            personaggio.armi.update(armi)
            armature = self.competence_armature_multiclasse if is_multiclasse else self.competence_armature
            personaggio.armature.update(armature)

            # Tiri salvezza e skill metadata: solo alla classe di partenza, mai al multiclasse (SRD p.163)
            if not is_multiclasse:
                for attr_enum in self.tiri_salvezza:
                    if attr_enum in personaggio.attributi:
                        personaggio.attributi[attr_enum].ts = True

            if not is_multiclasse and self.skills_choices_num > 0:
                personaggio.scelta_abilita = {
                    "numero": self.skills_choices_num,
                    "opzioni": self.skills_choices_opzioni
                }

    def __str__(self) -> str:
        return f"{self.livello}° {self.nome.value}"


def carica_classe(file_path: str) -> 'Classe':
    """Deserializza una Classe da file JSON di configurazione."""
    with open(file_path, "r", encoding="utf-8") as f:
        dati = json.load(f)

    mc_and_raw = dati.get("prerequisiti_multiclasse_and", {})
    mc_or_raw = dati.get("prerequisiti_multiclasse_or", {})
    mc_skills = dati.get("competenze_multiclasse", {})

    armi_base = set(dati.get("competence_armi", []))
    armi_mc = set(dati.get("competence_armi_multiclasse", armi_base))
    armature_base = set(dati.get("competence_armature", []))
    armature_mc = set(dati.get("competence_armature_multiclasse", armature_base))

    return Classe(
        nome=ClassiEnum(dati["nome"]),
        hp_dado=dati.get("hp_dado", 0),
        competence_armi=armi_base,
        competence_armi_multiclasse=armi_mc,
        competence_armature=armature_base,
        competence_armature_multiclasse=armature_mc,
        tiri_salvezza={AttributoEnum[t] for t in dati.get("tiri_salvezza", [])},
        privilegi={int(lvl): feats for lvl, feats in dati.get("privilegi", {}).items()},
        competenze_base={AbilitaEnum[a] for a in dati.get("competenze_base", [])},
        skills_choices_num=dati.get("skills_choices", {}).get("numero", 0),
        skills_choices_opzioni={AbilitaEnum[a] for a in dati.get("skills_choices", {}).get("opzioni", [])},
        prerequisiti_and={AttributoEnum[k]: v for k, v in mc_and_raw.items()},
        prerequisiti_or={AttributoEnum[k]: v for k, v in mc_or_raw.items()},
        multiclass_skills_num=mc_skills.get("numero", 0),
        multiclass_skills_opzioni={AbilitaEnum[a] for a in mc_skills.get("opzioni", [])},
        asi_livelli=frozenset(dati.get("asi_livelli", ASI_LIVELLI_DEFAULT)),
    )