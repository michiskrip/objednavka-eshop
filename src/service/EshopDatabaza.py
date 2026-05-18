import os
from decimal import Decimal

from lib.db_connection import DBConnection
from src.model.Objednavka import Objednavka


# SPRÁVA OBJEDNÁVOK
# ============================================================

class EshopDatabaza:
    """
    Spravuje zoznam objednávok.
    Zabezpečuje: pridanie, mazanie, úpravu, filtrovanie,
    triedenie a načítanie zo súboru.
    """

    def __init__(self) -> None:
        self._db = DBConnection()
        self._objednavky: list[Objednavka] = []

    # -- vlastnosti --

    @property
    def vsetky(self) -> list[Objednavka]:
        """Vráti kópiu zoznamu všetkých objednávok."""
        return list(self._objednavky)

    @property
    def pocet(self) -> int:
        return len(self._objednavky)

    # -- CRUD --

    def pridaj(self, zakaznik: str, produkt: str, cena_za_kus: float, pocet_kusov: int) -> None:
        """Validuje vstup a pridá novú objednávku."""
        cena = Decimal(str(cena_za_kus))
        if not zakaznik.strip():
            raise ValueError("Meno zákazníka nesmie byť prázdne.")
        if not produkt.strip():
            raise ValueError("Názov produktu nesmie byť prázdny.")
        if cena <= 0:
            raise ValueError("Cena za kus musí byť kladné číslo.")
        if not isinstance(pocet_kusov, int) or pocet_kusov <= 0:
            raise ValueError("Počet kusov musí byť kladné celé číslo.")
        self._objednavky.append(
            Objednavka(zakaznik.strip(), produkt.strip(), cena, pocet_kusov)
        )
        self._db.execute(
    "INSERT INTO objednavky (zakaznik, produkt, cena_za_kus, pocet_kusov) VALUES (%s, %s, %s, %s)",
    (zakaznik.strip(), produkt.strip(), float(cena), pocet_kusov)
)
        self._db.commit()

    def vymaz_zakaznika(self, meno: str) -> int:
        """Vymaže všetky objednávky zákazníka. Vráti počet vymazaných."""
        pred = self.pocet
        self._objednavky = [o for o in self._objednavky if o.zakaznik != meno]
        self._db.execute("DELETE FROM objednavky WHERE zakaznik = %s", (meno,))
        self._db.commit()
        return pred - self.pocet

    def uprav_pocet_kusov(self, zakaznik: str, produkt: str, novy_pocet: int) -> bool:
        """Upraví počet kusov v prvej nájdenej objednávke. Vráti True ak sa našlo."""
        if not isinstance(novy_pocet, int) or novy_pocet <= 0:
            raise ValueError("Nový počet kusov musí byť kladné celé číslo.")
        for i, o in enumerate(self._objednavky):
            if o.zakaznik == zakaznik and o.produkt == produkt:
                self._objednavky[i] = o._replace(pocet_kusov=novy_pocet)
                self._db.execute(
                "UPDATE objednavky SET pocet_kusov = %s WHERE zakaznik = %s AND produkt = %s",
                (novy_pocet, zakaznik, produkt)
            )
            self._db.commit()
            return True
        return False

    # -- filtrovanie --

    def filtruj_zakaznika(self, meno: str) -> list[Objednavka]:
        return [o for o in self._objednavky if o.zakaznik == meno]

    def filtruj_nad_sumu(self, min_suma: float = 500.0) -> list[Objednavka]:
        hranica = Decimal(str(min_suma))
        return [o for o in self._objednavky if o.celkova_cena > hranica]

    def filtruj_produkt(self, produkt: str) -> list[Objednavka]:
        return [o for o in self._objednavky if o.produkt == produkt]

    # -- triedenie --

    def zorad_podla_ceny(self, zostupne: bool = True) -> list[Objednavka]:
        return sorted(self._objednavky, key=lambda o: o.celkova_cena, reverse=zostupne)

    def zorad_podla_mena(self) -> list[Objednavka]:
        return sorted(self._objednavky, key=lambda o: o.zakaznik)

    # -- súbor --

    def nacitaj_zo_suboru(self, cesta: str) -> int:
        """Načíta objednávky z CSV (formát: zakaznik;produkt;cena;pocet). Vráti počet načítaných."""
        if not os.path.exists(cesta):
            raise FileNotFoundError(f"Súbor '{cesta}' neexistuje.")
        nacitane = 0
        with open(cesta, encoding="utf-8") as f:
            for cislo, riadok in enumerate(f, 1):
                riadok = riadok.strip()
                if not riadok or riadok.startswith("#"):
                    continue
                casti = riadok.split(";")
                if len(casti) != 4:
                    print(f"  [Varovanie] Riadok {cislo}: nesprávny formát, preskočený.")
                    continue
                try:
                    zakaznik, produkt, cena_str, pocet_str = casti
                    self.pridaj(zakaznik, produkt, float(cena_str), int(pocet_str))
                    nacitane += 1
                except (ValueError, TypeError) as e:
                    print(f"  [Varovanie] Riadok {cislo}: {e}, preskočený.")
        return nacitane

    def nacitaj_data_db (self):
        """Načíta objednávky z databázy."""
        db = DBConnection()
        data = db.fetch_all("SELECT zakaznik, produkt, cena_za_kus, pocet_kusov FROM objednavky")
        for zakaznik, produkt, cena_za_kus, pocet_kusov in data:
            self.pridaj(zakaznik, produkt, cena_za_kus, pocet_kusov)