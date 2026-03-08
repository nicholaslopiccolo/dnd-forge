from player import Personaggio
from constants import AttributoEnum, ClassiEnum

if __name__ == "__main__":
    p = Personaggio("Thorvin", ClassiEnum.BARBARO, attributi={AttributoEnum.DESTREZZA: 16})
    print(p)