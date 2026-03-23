from .base import Classe
from ..constants import ClassiEnum


def get_classe(nome: ClassiEnum) -> Classe:
    """Restituisce un'istanza di Classe dalla configurazione JSON."""
    return Classe.from_config(nome)
