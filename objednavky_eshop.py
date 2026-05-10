"""
Správa objednávok v e-shope
============================
OOP verzia rozdelená do tried:
  - Objednavka    : nemenný dátový model (namedtuple)
  - EshopDatabaza : správa zoznamu objednávok (CRUD, filtrovanie, triedenie)
  - Analytika     : agregácie a štatistiky
  - Report        : výpis a export
"""

import array
import csv
import os
import random
from collections import namedtuple
from datetime import datetime
from html import escape
from db_connection import DBConnection

# ============================================================
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


# ============================================================
# SPRÁVA OBJEDNÁVOK
# ============================================================

class EshopDatabaza:
    """
    Spravuje zoznam objednávok.
    Zabezpečuje: pridanie, mazanie, úpravu, filtrovanie,
    triedenie a načítanie zo súboru.
    """

    def __init__(self) -> None:
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
        if not zakaznik.strip():
            raise ValueError("Meno zákazníka nesmie byť prázdne.")
        if not produkt.strip():
            raise ValueError("Názov produktu nesmie byť prázdny.")
        if cena_za_kus <= 0:
            raise ValueError("Cena za kus musí byť kladné číslo.")
        if not isinstance(pocet_kusov, int) or pocet_kusov <= 0:
            raise ValueError("Počet kusov musí byť kladné celé číslo.")
        self._objednavky.append(
            Objednavka(zakaznik.strip(), produkt.strip(), cena_za_kus, pocet_kusov)
        )

    def vymaz_zakaznika(self, meno: str) -> int:
        """Vymaže všetky objednávky zákazníka. Vráti počet vymazaných."""
        pred = self.pocet
        self._objednavky = [o for o in self._objednavky if o.zakaznik != meno]
        return pred - self.pocet

    def uprav_pocet_kusov(self, zakaznik: str, produkt: str, novy_pocet: int) -> bool:
        """Upraví počet kusov v prvej nájdenej objednávke. Vráti True ak sa našlo."""
        if not isinstance(novy_pocet, int) or novy_pocet <= 0:
            raise ValueError("Nový počet kusov musí byť kladné celé číslo.")
        for i, o in enumerate(self._objednavky):
            if o.zakaznik == zakaznik and o.produkt == produkt:
                self._objednavky[i] = o._replace(pocet_kusov=novy_pocet)
                return True
        return False

    # -- filtrovanie --

    def filtruj_zakaznika(self, meno: str) -> list[Objednavka]:
        return [o for o in self._objednavky if o.zakaznik == meno]

    def filtruj_nad_sumu(self, min_suma: float = 500.0) -> list[Objednavka]:
        return [o for o in self._objednavky if o.celkova_cena > min_suma]

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
# ============================================================
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
            vysledok[o.zakaznik] = vysledok.get(o.zakaznik, 0.0) + o.celkova_cena
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
        return [(m, s) for m, s in minuty.items() if s > min_suma]

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


# ============================================================
# REPORT
# ============================================================

class Report:
    """
    Zodpovedá za výpis a export reportov.
    Pracuje s inštanciou EshopDatabaza.
    """

    def __init__(self, db: EshopDatabaza) -> None:
        self._db = db

    # -- tabuľka --

    @staticmethod
    def vypis_tabulku(zoznam: list) -> None:
        if not zoznam:
            print("  [Zoznam objednávok je prázdny]")
            return
        print(f"  {'#':<4} {'Zákazník':<22} {'Produkt':<15} {'Cena/ks':>10} {'Ks':>4} {'Spolu':>10}")
        print("  " + "-" * 69)
        for i, o in enumerate(zoznam, 1):
            print(
                f"  {i:<4} {o.zakaznik:<22} {o.produkt:<15} "
                f"{o.cena_za_kus:>9.2f}€ {o.pocet_kusov:>4} {o.celkova_cena:>9.2f}€"
            )

    # -- záverečný report --

    def vypis_zhrnutie(self) -> None:
        zoznam = self._db.vsetky
        if not zoznam:
            print("  [Žiadne objednávky – report nie je možný]")
            return

        an = Analytika(zoznam)
        stat = an.statistiky_cien()
        tz, tz_suma = an.top_zakaznik()
        tp, tp_kusy = an.top_produkt()
        minuty = an.minuty_na_zakaznika()

        w = 52
        print("  " + "=" * w)
        print("  ZÁVEREČNÝ REPORT E-SHOPU")
        print("  " + "=" * w)
        print(f"  Celkový počet objednávok    : {stat['pocet']}")
        print(f"  Celkový obrat               : {stat['sucet']:.2f} €")
        print(f"  Priemerná hodnota objednávky: {stat['priemer']:.2f} €")
        print(f"  Unikátni zákazníci          : {len(an.unikatni_zakaznici)}")
        print(f"  Unikátne produkty           : {len(an.unikatne_produkty)}")
        print(f"  Top zákazník                : {tz} ({tz_suma:.2f} €)")
        print(f"  Najpredávanejší produkt     : {tp} ({tp_kusy} ks)")
        print()
        print(f"  {'Zákazník':<22} {'Celkom':>12}")
        print("  " + "-" * 36)
        for meno, suma in sorted(minuty.items(), key=lambda x: x[1], reverse=True):
            print(f"  {meno:<22} {suma:>11.2f}€")
        print("  " + "=" * w)

    def exportuj_do_suboru(self, cesta: str) -> None:
        """Exportuje záverečný report do textového súboru."""
        import io
        import sys

        buf = io.StringIO()
        pov = sys.stdout
        sys.stdout = buf
        try:
            self.vypis_zhrnutie()
        finally:
            sys.stdout = pov

        obsah = buf.getvalue().replace("  ", "")
        with open(cesta, "w", encoding="utf-8") as f:
            f.write(f"Exportované: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(obsah)
        print(f"  Report exportovaný do: {cesta}")

    @staticmethod
    def exportuj_tabulku_csv(zoznam: list, cesta: str) -> None:
        with open(cesta, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["zakaznik", "produkt", "cena_za_kus", "pocet_kusov", "celkova_cena"])
            for o in zoznam:
                writer.writerow([o.zakaznik, o.produkt, o.cena_za_kus, o.pocet_kusov, o.celkova_cena])
        print(f"  CSV tabuľka exportovaná do: {cesta}")

    @staticmethod
    def exportuj_tabulku_html(zoznam: list, cesta: str) -> None:
        riadky = []
        for i, o in enumerate(zoznam, 1):
            riadky.append(
                "<tr>"
                f"<td>{i}</td>"
                f"<td>{escape(o.zakaznik)}</td>"
                f"<td>{escape(o.produkt)}</td>"
                f"<td class='number'>{o.cena_za_kus:.2f} €</td>"
                f"<td class='number'>{o.pocet_kusov}</td>"
                f"<td class='number'>{o.celkova_cena:.2f} €</td>"
                "</tr>"
            )

        obsah = f"""<!doctype html>
<html lang="sk">
<head>
    <meta charset="utf-8">
    <title>Objednávky e-shopu</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
        h1 {{ font-size: 24px; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 1100px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px 10px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .number {{ text-align: right; }}
    </style>
</head>
<body>
    <h1>Objednávky e-shopu</h1>
    <p>Počet objednávok: {len(zoznam)}</p>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Zákazník</th>
                <th>Produkt</th>
                <th>Cena za kus</th>
                <th>Počet kusov</th>
                <th>Celková cena</th>
            </tr>
        </thead>
        <tbody>
            {''.join(riadky)}
        </tbody>
    </table>
</body>
</html>
"""
        with open(cesta, "w", encoding="utf-8") as f:
            f.write(obsah)
        print(f"  HTML tabuľka exportovaná do: {cesta}")


# ============================================================
# VZOROVÉ DÁTa
# ============================================================

VZOROVE_OBJEDNAVKY = [
    ("Anna Nováková",  "Notebook",   899.00, 1),
    ("Peter Kováč",    "Myš",         25.50, 3),
    ("Jana Horáková",  "Klávesnica",  45.00, 2),
    ("Anna Nováková",  "Monitor",    320.00, 2),
    ("Tomáš Blaho",    "Notebook",   899.00, 1),
    ("Peter Kováč",    "Notebook",   899.00, 1),
    ("Jana Horáková",  "Myš",         25.50, 1),
    ("Martin Sloboda", "Slúchadlá",  149.00, 2),
    ("Tomáš Blaho",    "Monitor",    320.00, 1),
    ("Martin Sloboda", "Klávesnica",  45.00, 4),
    ("Anna Nováková",  "Slúchadlá",  149.00, 1),
    ("Peter Kováč",    "Monitor",    320.00, 1),
]


# ============================================================
# HLAVNÝ PROGRAM
# ============================================================

def main() -> None:
    print("Program sa spustil")
    dbconn = DBConnection()

    dbconn.execute("""
        CREATE TABLE IF NOT EXISTS objednavky (
            zakaznik TEXT NOT NULL,
            produkt TEXT NOT NULL,
            cena_za_kus NUMERIC(10, 2) NOT NULL,
            pocet_kusov INTEGER NOT NULL
        )
    """)

    dbconn.execute("TRUNCATE TABLE objednavky")

    fiktivne = generuj_fiktivne_data(100)

    for zakaznik, produkt, cena, pocet in fiktivne:
        dbconn.execute(
            """
            INSERT INTO objednavky (zakaznik, produkt, cena_za_kus, pocet_kusov)
            VALUES (%s, %s, %s, %s)
            """,
            (zakaznik, produkt, cena, pocet)
        )

    dbconn.commit()

    db = EshopDatabaza()
    db.nacitaj_data_db()

    print("Počet objednávok:", db.pocet)
    print("Objednávky:")
    Report.vypis_tabulku(db.vsetky)

    rep = Report(db)
    rep.vypis_zhrnutie()
    rep.exportuj_do_suboru("report.txt")
    Report.exportuj_tabulku_csv(db.vsetky, "objednavky.csv")
    Report.exportuj_tabulku_html(db.vsetky, "objednavky.html")

    dbconn.close()


def generuj_fiktivne_data(pocet=100):
    mena = ["Anna Nováková","Peter Kováč","Jana Horáková","Tomáš Blaho","Martin Sloboda","Eva Tóthová"]
    produkty = ["Notebook","Myš","Klávesnica","Monitor","Slúchadlá"]
    data = []
    for _ in range(pocet):
        zakaznik = random.choice(mena)
        produkt = random.choice(produkty)
        cena = round(random.uniform(10, 1500), 2)
        pocet_kusov = random.randint(1, 5)
        data.append((zakaznik, produkt, cena, pocet_kusov))
    return data




if __name__ == "__main__":
    main()    

#     an = Analytika(db)
#     rep = Report(db)

#     # ----------------------------------------------------------
#     print(sep + "1. ZOZNAM OBJEDNÁVOK")
#     print(f"  Celkový počet: {db.pocet}")
#     rep.vypis_tabulku(db.vsetky)

#     print("\n  Objednávky Anny Novákovej:")
#     rep.vypis_tabulku(db.filtruj_zakaznika("Anna Nováková"))

#     print("\n  Objednávky nad 500 €:")
#     rep.vypis_tabulku(db.filtruj_nad_sumu())

#     # ----------------------------------------------------------
#     print(sep + "2. NEMENNÝ ZÁZNAM (namedtuple)")
#     ukazka = db.vsetky[0]
#     print(f"  Zákazník  : {ukazka.zakaznik}")
#     print(f"  Produkt   : {ukazka.produkt}")
#     print(f"  Cena/ks   : {ukazka.cena_za_kus:.2f} €")
#     print(f"  Počet ks  : {ukazka.pocet_kusov}")
#     print(f"  Celkom    : {ukazka.celkova_cena:.2f} €")
#     print()
#     nova = ukazka._replace(pocet_kusov=ukazka.pocet_kusov + 1)
#     print(f"  Pôvodná (nezmenená): {ukazka}")
#     print(f"  Nová (po _replace) : {nova}")
#     print(f"  Sú rovnaké?        : {ukazka == nova}")

#     # ----------------------------------------------------------
#     print(sep + "3. MNOŽINY")
#     print(f"  Unikátni zákazníci ({len(an.unikatni_zakaznici)}): {sorted(an.unikatni_zakaznici)}")
#     print(f"  Unikátne produkty  ({len(an.unikatne_produkty)}): {sorted(an.unikatne_produkty)}")
#     print(f"\n  Zákazníci Notebooku   : {sorted(an.zakaznici_produktu('Notebook'))}")
#     print(f"  Produkty Petra Kováča : {sorted(an.produkty_zakaznika('Peter Kováč'))}")

#     # ----------------------------------------------------------
#     print(sep + "4. SLOVNÍKY")
#     print("  Minúté peniaze podľa zákazníka:")
#     for m, s in sorted(an.minuty_na_zakaznika().items()):
#         print(f"    {m:<22}: {s:>9.2f} €")

#     print("\n  Predané kusy podľa produktu:")
#     for p, k in sorted(an.predane_kusy_na_produkt().items()):
#         print(f"    {p:<15}: {k:>4} ks")

#     print("\n  Počet objednávok podľa zákazníka:")
#     for m, n in sorted(an.pocet_objednavok_na_zakaznika().items()):
#         print(f"    {m:<22}: {n:>4}")

#     tz, tz_s = an.top_zakaznik()
#     tp, tp_k = an.top_produkt()
#     print(f"\n  Top zákazník         : {tz} ({tz_s:.2f} €)")
#     print(f"  Najpredávanejší prod.: {tp} ({tp_k} ks)")

#     # ----------------------------------------------------------
#     print(sep + "5. ČÍSELNÉ POLE (array)")
#     pole = an.pole_cien()
#     stat = an.statistiky_cien()
#     print(f"  Pole cien : {list(pole)}")
#     print(f"  Min       : {stat['min']:.2f} €")
#     print(f"  Max       : {stat['max']:.2f} €")
#     print(f"  Priemer   : {stat['priemer']:.2f} €")
#     print(f"  Súčet     : {stat['sucet']:.2f} €")
#     print(f"  Počet     : {stat['pocet']}")

#     # ----------------------------------------------------------
#     print(sep + "6. VNORENÉ DÁTA")
#     vnorena = an.vnorena_struktura()
#     print("  Objednávky Tomáša Blahu:")
#     rep.vypis_tabulku(vnorena["Tomáš Blaho"])
#     suma_tb = sum(o.celkova_cena for o in vnorena["Tomáš Blaho"])
#     print(f"\n  Celková suma Tomáša Blahu: {suma_tb:.2f} €")
#     zmeno, pocet = an.zakaznik_s_najviac_objednavkami()
#     print(f"  Zákazník s najviac objednávkami: {zmeno} ({pocet})")
#     print("\n  Súhrnný report zákazníkov:")
#     print(f"  {'Zákazník':<22} {'Objednávky':>12} {'Celkom':>12}")
#     print("  " + "-" * 48)
#     for meno, objs in sorted(vnorena.items()):
#         print(f"  {meno:<22} {len(objs):>12} {sum(o.celkova_cena for o in objs):>11.2f}€")

#     # ----------------------------------------------------------
#     print(sep + "7. TRIEDENIE A VYHĽADÁVANIE")
#     print("  Zoradené podľa ceny (zostupne):")
#     rep.vypis_tabulku(db.zorad_podla_ceny())

#     print("\n  Zoradené podľa mena:")
#     rep.vypis_tabulku(db.zorad_podla_mena())

#     print("\n  Produkty podľa predaných kusov:")
#     for prod, ks in an.zorad_produkty_podla_kusov():
#         print(f"    {prod:<15}: {ks:>4} ks")

#     print("\n  Objednávky produktu 'Myš':")
#     rep.vypis_tabulku(db.filtruj_produkt("Myš"))

#     print("\n  Zákazníci nad 1 000 €:")
#     for m, s in sorted(an.zakaznici_nad_sumu(1000), key=lambda x: x[1], reverse=True):
#         print(f"    {m:<22}: {s:.2f} €")

#     # ----------------------------------------------------------
#     print(sep + "8. ZÁVEREČNÝ REPORT")
#     rep.vypis_zhrnutie()

#     # ----------------------------------------------------------
#     print(sep + "BONUS – CRUD operácie a export")
#     db.pridaj("Eva Tóthová", "Slúchadlá", 149.00, 3)
#     print(f"  Pridaná objednávka. Celkový počet: {db.pocet}")

#     ok = db.uprav_pocet_kusov("Eva Tóthová", "Slúchadlá", 5)
#     print(f"  Úprava kusov: {'OK' if ok else 'nenájdené'}")

#     vymazane = db.vymaz_zakaznika("Eva Tóthová")
#     print(f"  Vymazaných {vymazane} objednávok. Zostatok: {db.pocet}")

#     rep.exportuj_do_suboru("report.txt")

#     # ----------------------------------------------------------
#     print(sep + "OŠETRENIE CHÝB")

#     prazdna_db = EshopDatabaza()
#     Report.vypis_tabulku([])
#     print(f"  Štatistiky prázdnej DB: {Analytika(prazdna_db).statistiky_cien()}")

#     try:
#         Analytika(prazdna_db).top_zakaznik()
#     except ValueError as e:
#         print(f"  Prázdna DB – ValueError: {e}")

#     for popis, args in [
#         ("prázdne meno",  ("",    "Myš", 25.5,  2)),
#         ("nulová cena",   ("Ján", "Myš",  0.0,  2)),
#         ("záporný počet", ("Ján", "Myš", 25.5, -1)),
#     ]:
#         try:
#             db.pridaj(*args)
#         except ValueError as e:
#             print(f"  [{popis}] ValueError: {e}")


# if __name__ == "__main__":
#     main()
