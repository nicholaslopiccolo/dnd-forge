from enum import Enum

EXP_LIVELLI = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000
}

class AttributoEnum(Enum):
    FORZA = "forza"
    DESTREZZA = "destrezza"
    COSTITUZIONE = "costituzione"
    INTELLIGENZA = "intelligenza"
    SAGGEZZA = "saggezza"
    CARISMA = "carisma"

class AbilitaEnum(Enum):
    ACROBAZIA = ("Acrobazia", AttributoEnum.DESTREZZA)
    ADDESTRARE_ANIMALI = ("Addestrare Animali", AttributoEnum.SAGGEZZA)
    ARCANO = ("Arcano", AttributoEnum.INTELLIGENZA)
    ATLETICA = ("Atletica", AttributoEnum.FORZA)
    FURTIVITA = ("Furtività", AttributoEnum.DESTREZZA)
    INDAGARE = ("Indagare", AttributoEnum.INTELLIGENZA)
    INGANNARE = ("Ingannare", AttributoEnum.CARISMA)
    INTIMIDIRE = ("Intimidire", AttributoEnum.CARISMA)
    INTUIZIONE = ("Intuizione", AttributoEnum.SAGGEZZA)
    INTRATTENERE = ("Intrattenere", AttributoEnum.CARISMA)
    MEDICINA = ("Medicina", AttributoEnum.SAGGEZZA)
    NATURA = ("Natura", AttributoEnum.INTELLIGENZA)
    PERCEZIONE = ("Percezione", AttributoEnum.SAGGEZZA)
    PERSUASIONE = ("Persuasione", AttributoEnum.CARISMA)
    RAPIDITA_DI_MANO = ("Rapidità di Mano", AttributoEnum.DESTREZZA)
    RELIGIONE = ("Religione", AttributoEnum.INTELLIGENZA)
    SOPRAVVIVENZA = ("Sopravvivenza", AttributoEnum.SAGGEZZA)
    STORIA = ("Storia", AttributoEnum.INTELLIGENZA)

    def __init__(self, label, attributo):
        self.label = label
        self.attributo = attributo

    def __str__(self) -> str:
        return f"{self.label}"

class ClassiEnum(Enum):
    ARTEFICE = "Artefice"
    BARBARO = "Barbaro"
    GUERRIERO = "Guerriero"
    LADRO = "Ladro"
    MONACO = "Monaco"
    PALADINO = "Paladino"
    RANGER = "Ranger"
    BARDO = "Bardo"
    CHIERICO = "Chierico"
    DRUIDO = "Druido"
    MAGO = "Mago"
    STREGONE = "Stregone"
    WARLOCK = "Warlock"


class RazzaEnum(Enum):
    UMANO = "Umano"
    ELFO = "Elfo"
    NANO = "Nano"
    HALFLING = "Halfling"
    GNOMO = "Gnomo"
    MEZZORCO = "Mezzorco"
    TIEFLING = "Tiefling"
    DRAGONIDE = "Dragonide"
    MEZZELFO = "Mezzelfo"


# Livelli a cui scatta l'Ability Score Improvement
ASI_LIVELLI: frozenset[int] = frozenset({4, 8, 12, 16, 19})

# Valori dello Standard Array per l'assegnazione degli attributi
STANDARD_ARRAY: tuple[int, ...] = (15, 14, 13, 12, 10, 8)