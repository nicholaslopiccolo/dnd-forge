from __future__ import annotations

from dataclasses import dataclass, field

from .constants import EXP_LIVELLI, AbilitaEnum, AttributoEnum, ClassiEnum, RazzaEnum
from .classi.base import Classe

@dataclass
class Attributo:
    """Un attributo base del PG (es. Forza, Destrezza)."""
    nome: str
    valore: int = 10
    ts: bool = False

    @property
    def modificatore(self) -> int:
        return (self.valore - 10) // 2

    def tiro_salvezza(self, bonus_competenza: int) -> int:
        if self.ts:
            return self.modificatore + bonus_competenza
        return self.modificatore
    
    def __str__(self) -> str:
        return f"{self.nome[:3].upper()} {self.valore} ({self.modificatore:+})"


@dataclass
class Abilita:
    """Un'abilità derivata da un attributo base."""
    nome: AbilitaEnum
    attributo: Attributo
    competente: bool = False

    def bonus(self, bonus_competenza: int) -> int:
        """Calcola il bonus dell'abilità"""
        return self.attributo.modificatore + (bonus_competenza if self.competente else 0)
    
    def __str__(self) -> str:
        return f"{self.nome.label} ({self.attributo.nome[:3].upper()})"


@dataclass
class Personaggio:
    """Rappresenta un personaggio giocante (PG) di D&D 5e."""
    nome: str
    classe_iniziale: ClassiEnum

    id: int = 0
    razza: RazzaEnum | None = None
    livello: int = 0
    exp: int = 0
    classi: dict[ClassiEnum, Classe] = field(default_factory=dict)
    hp: int = 0

    attributi: dict[AttributoEnum, Attributo] = field(default_factory=dict)
    competenze: set[AbilitaEnum] = field(default_factory=set)

    armi: set[str] = field(default_factory=set)
    armature: set[str] = field(default_factory=set)
    tiri_salvezza: set[AttributoEnum] = field(default_factory=set)
    scelta_abilita: dict = field(default_factory=dict)

    descrizione: str = ""

    def __post_init__(self):
        if not self.nome:
            raise ValueError("Il nome del personaggio è obbligatorio")

        if self.classe_iniziale is None:
            raise ValueError("La classe iniziale è obbligatoria")

        # inizializza attributi a 10 se non specificati
        default_attr = {attr: Attributo(attr.value, 10) for attr in AttributoEnum}

        for attr, valore in self.attributi.items():
            if isinstance(valore, int):
                default_attr[attr] = Attributo(attr.value, valore)
            else:
                default_attr[attr] = valore

        self.attributi = default_attr

        # inizializza la classe
        self.classi[self.classe_iniziale] = Classe.from_config(self.classe_iniziale)

        # livello 1 iniziale
        self.level_up(classe=self.classe_iniziale)

    @property
    def abilita(self) -> list[Abilita]:
        return [
            Abilita(
                abilita,
                self.attributi[abilita.attributo],
                abilita in self.competenze
            )
            for abilita in AbilitaEnum
        ]

    @property
    def classi_str(self) -> str:
        """Stringa compatta delle classi: es. '1° Guerriero / 2° Mago'."""
        return " / ".join(f"{c.livello}\u00b0 {c.nome.value}" for c in self.classi.values())

    @property
    def bonus_competenza(self) -> int:
        return 2 + (self.livello - 1) // 4

    def add_exp(self, amount: int) -> None:
        """Aggiunge EXP senza triggerare level-up automatici."""
        self.exp = min(self.exp + amount, 355000)

    def pending_levelups(self) -> int:
        """Restituisce quanti level-up sono in attesa."""
        count = 0
        livello = self.livello
        while livello < 20 and self.exp >= EXP_LIVELLI[livello + 1]:
            livello += 1
            count += 1
        return count

    def level_up(self, classe: ClassiEnum | None = None) -> None:
        self.livello += 1
        self.exp = max(0, self.exp - EXP_LIVELLI[self.livello])  # rimuove EXP del livello appena raggiunto

        if classe is None:
            if len(self.classi) == 1:
                classe = next(iter(self.classi))
            else:
                raise ValueError("Specifica la classe per il level up")

        if classe not in self.classi:
            self.classi[classe] = Classe(nome=classe)

        self.classi[classe].level_up(self)

    def aggiungi_feature(self, feature: str) -> None:
        # TODO: implementare il sistema di privilegi/feature
        pass

    @classmethod
    def from_saved(
        cls,
        *,
        id: int,
        nome: str,
        classe_iniziale: ClassiEnum,
        razza: RazzaEnum | None,
        livello: int,
        exp: int,
        hp: int,
        attributi: dict[AttributoEnum, Attributo],
        competenze: set[AbilitaEnum],
        armi: set[str],
        armature: set[str],
        tiri_salvezza: set[AttributoEnum],
        classi: dict[ClassiEnum, Classe],
        descrizione: str,
    ) -> Personaggio:
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

    def __str__(self) -> str:
        return f"{self.nome} — Liv.{self.livello} {self.classe_iniziale.value}"