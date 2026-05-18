import array
from decimal import Decimal

from src.model.Objednavka import Objednavka
from src.service.EshopDatabaza import EshopDatabaza


# ANALYTIKA
# ============================================================

class Analytika:
    """
    Počíta agregácie a štatistiky nad zoznamom objednávok.
    Prijíma inštanciu EshopDatabaza alebo ľubovoľný zoznam Objednavka.
    """

    def __init__(self, zdroj) -> None:
        self._data: list[Objednavka] = (
            zdroj.vsetky if isinstance(zdroj, EshopDatabaza) else list(zdroj)
        )

    def _over_neprazdne(self) -> None:
        if not self._data:
            raise ValueError("Zoznam objednávok je prázdny.")

    # -- množiny --

    @property
    def unikatni_zakaznici(self) -> set[str]:
        return {o.zakaznik for o in self._data}

    @property
    def unikatne_produkty(self) -> set[str]:
        return {o.produkt for o in self._data}

    def zakaznici_produktu(self, produkt: str) -> set[str]:
        return {o.zakaznik for o in self._data if o.produkt == produkt}

    def produkty_zakaznika(self, meno: str) -> set[str]:
        return {o.produkt for o in self._data if o.zakaznik == meno}
    
     # -- slovníky --

    def minuty_na_zakaznika(self) -> dict[str, float]:
        vysledok: dict[str, float] = {}
        for o in self._data:
            vysledok[o.zakaznik] = vysledok.get(o.zakaznik, Decimal("0")) + o.celkova_cena
        return vysledok

    def predane_kusy_na_produkt(self) -> dict[str, int]:
        vysledok: dict[str, int] = {}
        for o in self._data:
            vysledok[o.produkt] = vysledok.get(o.produkt, 0) + o.pocet_kusov
        return vysledok

    def pocet_objednavok_na_zakaznika(self) -> dict[str, int]:
        vysledok: dict[str, int] = {}
        for o in self._data:
            vysledok[o.zakaznik] = vysledok.get(o.zakaznik, 0) + 1
        return vysledok

    def vnorena_struktura(self) -> dict[str, list]:
        """Vráti slovník: zákazník → jeho zoznam objednávok."""
        struktura: dict[str, list] = {}
        for o in self._data:
            struktura.setdefault(o.zakaznik, []).append(o)
        return struktura

    # -- top --

    def top_zakaznik(self) -> tuple[str, float]:
        self._over_neprazdne()
        minuty = self.minuty_na_zakaznika()
        meno = max(minuty, key=minuty.__getitem__)
        return meno, minuty[meno]

    def top_produkt(self) -> tuple[str, int]:
        self._over_neprazdne()
        kusy = self.predane_kusy_na_produkt()
        produkt = max(kusy, key=kusy.__getitem__)
        return produkt, kusy[produkt]

    def zakaznik_s_najviac_objednavkami(self) -> tuple[str, int]:
        self._over_neprazdne()
        pocty = self.pocet_objednavok_na_zakaznika()
        meno = max(pocty, key=pocty.__getitem__)
        return meno, pocty[meno]

    def zakaznici_nad_sumu(self, min_suma: float) -> list[tuple[str, float]]:
        minuty = self.minuty_na_zakaznika()
        hranica = Decimal(str(min_suma))
        return [(m, s) for m, s in minuty.items() if s > hranica]

    def zorad_produkty_podla_kusov(self) -> list[tuple[str, int]]:
        kusy = self.predane_kusy_na_produkt()
        return sorted(kusy.items(), key=lambda x: x[1], reverse=True)

    # -- číselné pole --

    def pole_cien(self) -> array.array:
        """Vráti array.array (typ double) s celkovými cenami objednávok."""
        return array.array("d", (o.celkova_cena for o in self._data))

    def statistiky_cien(self) -> dict:
        pole = self.pole_cien()
        if not pole:
            return {"min": None, "max": None, "priemer": None, "sucet": None, "pocet": 0}
        return {
            "min":    min(pole),
            "max":    max(pole),
            "priemer": sum(pole) / len(pole),
            "sucet":  sum(pole),
            "pocet":  len(pole),
        }
