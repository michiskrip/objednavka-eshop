from collections import namedtuple


# DÁTOVÝ MODEL
# ============================================================

class Objednavka(namedtuple("_Objednavka", ["zakaznik", "produkt", "cena_za_kus", "pocet_kusov"])):
    """Nemenný záznam jednej objednávky."""

    @property
    def celkova_cena(self) -> float:
        """Celková cena = cena za kus × počet kusov."""
        return self.cena_za_kus * self.pocet_kusov

    def __str__(self) -> str:
        return (
            f"{self.zakaznik:<22} | {self.produkt:<15} | "
            f"{self.cena_za_kus:>8.2f}€ × {self.pocet_kusov:>3} ks = {self.celkova_cena:>9.2f}€"
        )
