"""
Správa objednávok v e-shope
============================
Precvičenie: zoznamy, n-tice, množiny, slovníky, číselné polia,
vnorené dátové štruktúry, filtrovanie, triedenie, agregácia, reportovanie.
"""

import array
import os
from collections import namedtuple
from datetime import datetime

# ---------------------------------------------------------------------------
# Dátový model – nemenný záznam (namedtuple)
# ---------------------------------------------------------------------------
Objednavka = namedtuple("Objednavka", ["zakaznik", "produkt", "cena_za_kus", "pocet_kusov"])

# ---------------------------------------------------------------------------
# Pomocná funkcia
# ---------------------------------------------------------------------------
def celkova_cena(obj: Objednavka) -> float:
    """Vráti celkovú cenu jednej objednávky."""
    return obj.cena_za_kus * obj.pocet_kusov


# ============================================================
# 1. ZOZNAM OBJEDNÁVOK – počiatočné dáta
# ============================================================
objednavky: list[Objednavka] = [
    Objednavka("Anna Nováková",   "Notebook",    899.00, 1),
    Objednavka("Peter Kováč",     "Myš",          25.50, 3),
    Objednavka("Jana Horáková",   "Klávesnica",   45.00, 2),
    Objednavka("Anna Nováková",   "Monitor",     320.00, 2),
    Objednavka("Tomáš Blaho",     "Notebook",    899.00, 1),
    Objednavka("Peter Kováč",     "Notebook",    899.00, 1),
    Objednavka("Jana Horáková",   "Myš",          25.50, 1),
    Objednavka("Martin Sloboda",  "Slúchadlá",   149.00, 2),
    Objednavka("Tomáš Blaho",     "Monitor",     320.00, 1),
    Objednavka("Martin Sloboda",  "Klávesnica",   45.00, 4),
    Objednavka("Anna Nováková",   "Slúchadlá",   149.00, 1),
    Objednavka("Peter Kováč",     "Monitor",     320.00, 1),
]


# ============================================================
# 1. PRÁCA SO ZOZNAMOM
# ============================================================
def vypis_vsetky_objednavky(zoznam: list[Objednavka]) -> None:
    """Vypíše všetky objednávky."""
    if not zoznam:
        print("  [Zoznam objednávok je prázdny]")
        return
    print(f"  {'#':<4} {'Zákazník':<20} {'Produkt':<15} {'Cena/ks':>10} {'Ks':>4} {'Spolu':>10}")
    print("  " + "-" * 67)
    for i, o in enumerate(zoznam, 1):
        print(f"  {i:<4} {o.zakaznik:<20} {o.produkt:<15} {o.cena_za_kus:>9.2f}€ {o.pocet_kusov:>4} {celkova_cena(o):>9.2f}€")


def filtruj_podla_zakaznika(zoznam: list[Objednavka], meno: str) -> list[Objednavka]:
    """Vráti zoznam objednávok daného zákazníka."""
    return [o for o in zoznam if o.zakaznik == meno]


def pocet_objednavok(zoznam: list[Objednavka]) -> int:
    """Vráti celkový počet objednávok."""
    return len(zoznam)


def objednavky_nad_sumu(zoznam: list[Objednavka], min_suma: float = 500.0) -> list[Objednavka]:
    """Vráti objednávky, ktorých celková cena je vyššia ako min_suma."""
    return [o for o in zoznam if celkova_cena(o) > min_suma]


# ============================================================
# 2. PRÁCA S NEMENNÝM ZÁZNAMOM (namedtuple)
# ============================================================
def demo_nemennost(obj: Objednavka) -> None:
    """
    Ukáže, že údaje namedtuple sa nemenia priamo –
    zmena je možná iba cez vytvorenie novej objednávky.
    """
    print(f"  Pôvodná objednávka : {obj}")
    # namedtuple._replace() vracia NOVÚ n-ticu; pôvodná zostáva nezmenená
    nova = obj._replace(pocet_kusov=obj.pocet_kusov + 1)
    print(f"  Nová objednávka    : {nova}")
    print(f"  Pôvodná (nezmenená): {obj}")
    print(f"  Sú rovnaké?        : {obj == nova}")


# ============================================================
# 3. PRÁCA S MNOŽINOU
# ============================================================
def unikatni_zakaznici(zoznam: list[Objednavka]) -> set[str]:
    return {o.zakaznik for o in zoznam}


def unikatne_produkty(zoznam: list[Objednavka]) -> set[str]:
    return {o.produkt for o in zoznam}


def zakaznici_produktu(zoznam: list[Objednavka], produkt: str) -> set[str]:
    """Vráti množinu zákazníkov, ktorí si objednali daný produkt."""
    return {o.zakaznik for o in zoznam if o.produkt == produkt}


def produkty_zakaznika(zoznam: list[Objednavka], meno: str) -> set[str]:
    """Vráti množinu produktov, ktoré si objednal daný zákazník."""
    return {o.produkt for o in zoznam if o.zakaznik == meno}


# ============================================================
# 4. PRÁCA SO SLOVNÍKOM
# ============================================================
def minuty_na_zakaznika(zoznam: list[Objednavka]) -> dict[str, float]:
    """Koľko peňazí minul každý zákazník."""
    prehled: dict[str, float] = {}
    for o in zoznam:
        prehled[o.zakaznik] = prehled.get(o.zakaznik, 0.0) + celkova_cena(o)
    return prehled


def predane_kusy_na_produkt(zoznam: list[Objednavka]) -> dict[str, int]:
    """Koľko kusov sa predalo z každého produktu."""
    prehled: dict[str, int] = {}
    for o in zoznam:
        prehled[o.produkt] = prehled.get(o.produkt, 0) + o.pocet_kusov
    return prehled


def pocet_objednavok_na_zakaznika(zoznam: list[Objednavka]) -> dict[str, int]:
    """Koľko objednávok má každý zákazník."""
    prehled: dict[str, int] = {}
    for o in zoznam:
        prehled[o.zakaznik] = prehled.get(o.zakaznik, 0) + 1
    return prehled


def top_zakaznik(zoznam: list[Objednavka]) -> tuple[str, float]:
    """Zákazník s najvyššou minutou sumou."""
    if not zoznam:
        raise ValueError("Zoznam objednávok je prázdny.")
    minuty = minuty_na_zakaznika(zoznam)
    meno = max(minuty, key=minuty.__getitem__)
    return meno, minuty[meno]


def top_produkt(zoznam: list[Objednavka]) -> tuple[str, int]:
    """Produkt s najväčším počtom predaných kusov."""
    if not zoznam:
        raise ValueError("Zoznam objednávok je prázdny.")
    kusy = predane_kusy_na_produkt(zoznam)
    produkt = max(kusy, key=kusy.__getitem__)
    return produkt, kusy[produkt]


# ============================================================
# 5. PRÁCA S ČÍSELNÝM POĽOM (array.array)
# ============================================================
def vytvor_pole_cien(zoznam: list[Objednavka]) -> array.array:
    """Vráti array.array s celkovými cenami objednávok (typ 'd' = double)."""
    return array.array("d", (celkova_cena(o) for o in zoznam))


def statistiky_cien(pole: array.array) -> dict:
    """Štatistiky nad poľom celkových cien."""
    if len(pole) == 0:
        return {"min": None, "max": None, "priemer": None, "sucet": None, "pocet": 0}
    return {
        "min":    min(pole),
        "max":    max(pole),
        "priemer": sum(pole) / len(pole),
        "sucet":  sum(pole),
        "pocet":  len(pole),
    }


# ============================================================
# 6. VNORENÉ DÁTA – zákazník → zoznam objednávok
# ============================================================
def vytvor_vnorenu_strukturu(zoznam: list[Objednavka]) -> dict[str, list[Objednavka]]:
    """Každý zákazník obsahuje zoznam svojich objednávok."""
    struktura: dict[str, list[Objednavka]] = {}
    for o in zoznam:
        struktura.setdefault(o.zakaznik, []).append(o)
    return struktura


def suma_zakaznika(vnorena: dict[str, list[Objednavka]], meno: str) -> float:
    """Celková suma všetkých objednávok jedného zákazníka."""
    if meno not in vnorena:
        raise KeyError(f"Zákazník '{meno}' neexistuje.")
    return sum(celkova_cena(o) for o in vnorena[meno])


def zakaznik_s_najviac_objednavkami(vnorena: dict[str, list[Objednavka]]) -> tuple[str, int]:
    """Zákazník s najväčším počtom objednávok."""
    if not vnorena:
        raise ValueError("Štruktúra je prázdna.")
    meno = max(vnorena, key=lambda k: len(vnorena[k]))
    return meno, len(vnorena[meno])


def suhrny_report_zakaznikov(vnorena: dict[str, list[Objednavka]]) -> None:
    """Vypíše súhrnný report pre všetkých zákazníkov."""
    print(f"  {'Zákazník':<22} {'Objednávky':>12} {'Celkom':>12}")
    print("  " + "-" * 48)
    for meno, objs in sorted(vnorena.items()):
        print(f"  {meno:<22} {len(objs):>12} {sum(celkova_cena(o) for o in objs):>11.2f}€")


# ============================================================
# 7. TRIEDENIE A VYHĽADÁVANIE
# ============================================================
def zorad_podla_ceny(zoznam: list[Objednavka], zostupne: bool = True) -> list[Objednavka]:
    return sorted(zoznam, key=celkova_cena, reverse=zostupne)


def zorad_podla_mena(zoznam: list[Objednavka]) -> list[Objednavka]:
    return sorted(zoznam, key=lambda o: o.zakaznik)


def zorad_produkty_podla_kusov(zoznam: list[Objednavka]) -> list[tuple[str, int]]:
    """Vráti zoznam (produkt, kusy) zoradený zostupne podľa predaných kusov."""
    kusy = predane_kusy_na_produkt(zoznam)
    return sorted(kusy.items(), key=lambda x: x[1], reverse=True)


def hladaj_objednavky_produktu(zoznam: list[Objednavka], produkt: str) -> list[Objednavka]:
    return [o for o in zoznam if o.produkt == produkt]


def zakaznici_nad_sumu(zoznam: list[Objednavka], min_suma: float) -> list[tuple[str, float]]:
    """Zákazníci, ktorí minuli viac ako zadanú sumu."""
    minuty = minuty_na_zakaznika(zoznam)
    return [(m, s) for m, s in minuty.items() if s > min_suma]


# ============================================================
# 8. VÝSTUPNÝ REPORT
# ============================================================
def vypis_report(zoznam: list[Objednavka]) -> None:
    if not zoznam:
        print("  [Žiadne objednávky – report nie je možný]")
        return

    pole = vytvor_pole_cien(zoznam)
    stat = statistiky_cien(pole)
    tz, tz_suma = top_zakaznik(zoznam)
    tp, tp_kusy = top_produkt(zoznam)
    minuty = minuty_na_zakaznika(zoznam)

    sirka = 50
    print("  " + "=" * sirka)
    print("  ZÁVEREČNÝ REPORT E-SHOPU")
    print("  " + "=" * sirka)
    print(f"  Celkový počet objednávok   : {stat['pocet']}")
    print(f"  Celkový obrat              : {stat['sucet']:.2f} €")
    print(f"  Priemerná hodnota objednávky: {stat['priemer']:.2f} €")
    print(f"  Unikátni zákazníci         : {len(unikatni_zakaznici(zoznam))}")
    print(f"  Unikátne produkty          : {len(unikatne_produkty(zoznam))}")
    print(f"  Top zákazník               : {tz} ({tz_suma:.2f} €)")
    print(f"  Najpredávanejší produkt    : {tp} ({tp_kusy} ks)")
    print()
    print("  Prehľad zákazníkov:")
    print(f"  {'Zákazník':<22} {'Celkom':>12}")
    print("  " + "-" * 36)
    for meno, suma in sorted(minuty.items(), key=lambda x: x[1], reverse=True):
        print(f"  {meno:<22} {suma:>11.2f}€")
    print("  " + "=" * sirka)


# ============================================================
# BONUSOVÉ FUNKCIE
# ============================================================
def pridaj_objednavku(
    zoznam: list[Objednavka],
    zakaznik: str,
    produkt: str,
    cena_za_kus: float,
    pocet_kusov: int,
) -> None:
    """Pridá novú objednávku po validácii vstupných dát."""
    if not zakaznik.strip():
        raise ValueError("Meno zákazníka nesmie byť prázdne.")
    if not produkt.strip():
        raise ValueError("Názov produktu nesmie byť prázdny.")
    if cena_za_kus <= 0:
        raise ValueError("Cena za kus musí byť kladné číslo.")
    if pocet_kusov <= 0 or not isinstance(pocet_kusov, int):
        raise ValueError("Počet kusov musí byť kladné celé číslo.")
    zoznam.append(Objednavka(zakaznik.strip(), produkt.strip(), cena_za_kus, pocet_kusov))


def vymaz_objednavky_zakaznika(zoznam: list[Objednavka], meno: str) -> int:
    """
    Vymaže všetky objednávky daného zákazníka.
    Vráti počet vymazaných záznamov.
    """
    povodny_pocet = len(zoznam)
    zoznam[:] = [o for o in zoznam if o.zakaznik != meno]
    return povodny_pocet - len(zoznam)


def uprav_pocet_kusov(
    zoznam: list[Objednavka],
    zakaznik: str,
    produkt: str,
    novy_pocet: int,
) -> bool:
    """
    Upraví počet kusov v prvej nájdenej objednávke zákazníka pre daný produkt.
    Vráti True ak sa zmena podarila, inak False.
    """
    if novy_pocet <= 0 or not isinstance(novy_pocet, int):
        raise ValueError("Nový počet kusov musí byť kladné celé číslo.")
    for i, o in enumerate(zoznam):
        if o.zakaznik == zakaznik and o.produkt == produkt:
            zoznam[i] = o._replace(pocet_kusov=novy_pocet)
            return True
    return False


def export_report_do_suboru(zoznam: list[Objednavka], cesta: str) -> None:
    """Exportuje report do textového súboru."""
    import io, sys
    buffer = io.StringIO()
    stary_stdout = sys.stdout
    sys.stdout = buffer
    try:
        vypis_report(zoznam)
    finally:
        sys.stdout = stary_stdout
    obsah = buffer.getvalue().replace("  ", "")  # odstráni odsadenie konzoly
    with open(cesta, "w", encoding="utf-8") as f:
        f.write(f"Exportované: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(obsah)
    print(f"  Report exportovaný do: {cesta}")


def nacitaj_objednavky_zo_suboru(cesta: str) -> list[Objednavka]:
    """
    Načíta objednávky z CSV súboru.
    Formát riadku: zakaznik;produkt;cena_za_kus;pocet_kusov
    """
    if not os.path.exists(cesta):
        raise FileNotFoundError(f"Súbor '{cesta}' neexistuje.")
    zoznam: list[Objednavka] = []
    with open(cesta, encoding="utf-8") as f:
        for cislo_riadku, riadok in enumerate(f, 1):
            riadok = riadok.strip()
            if not riadok or riadok.startswith("#"):
                continue
            casti = riadok.split(";")
            if len(casti) != 4:
                print(f"  [Varovanie] Riadok {cislo_riadku} má nesprávny formát, preskočený.")
                continue
            try:
                zakaznik, produkt, cena_str, pocet_str = casti
                cena = float(cena_str.strip())
                pocet = int(pocet_str.strip())
                pridaj_objednavku(zoznam, zakaznik, produkt, cena, pocet)
            except (ValueError, TypeError) as e:
                print(f"  [Varovanie] Riadok {cislo_riadku}: {e}, preskočený.")
    return zoznam


# ============================================================
# HLAVNÝ PROGRAM – ukážka všetkých sekcií
# ============================================================
def main() -> None:
    sep = "\n" + "~" * 60 + "\n"

    # ----------------------------------------------------------
    print(sep + "1. ZOZNAM OBJEDNÁVOK")
    print(f"  Počet objednávok: {pocet_objednavok(objednavky)}")
    vypis_vsetky_objednavky(objednavky)

    print("\n  Objednávky Anny Novákovej:")
    vypis_vsetky_objednavky(filtruj_podla_zakaznika(objednavky, "Anna Nováková"))

    print("\n  Objednávky nad 500 €:")
    vypis_vsetky_objednavky(objednavky_nad_sumu(objednavky))

    # ----------------------------------------------------------
    print(sep + "2. NEMENNÝ ZÁZNAM (namedtuple)")
    ukazka = objednavky[0]
    print(f"  Zákazník  : {ukazka.zakaznik}")
    print(f"  Produkt   : {ukazka.produkt}")
    print(f"  Cena/ks   : {ukazka.cena_za_kus:.2f} €")
    print(f"  Počet ks  : {ukazka.pocet_kusov}")
    print(f"  Celkom    : {celkova_cena(ukazka):.2f} €")
    print()
    demo_nemennost(ukazka)

    # ----------------------------------------------------------
    print(sep + "3. MNOŽINY")
    zakaznici = unikatni_zakaznici(objednavky)
    produkty  = unikatne_produkty(objednavky)
    print(f"  Unikátni zákazníci ({len(zakaznici)}): {sorted(zakaznici)}")
    print(f"  Unikátne produkty  ({len(produkty)}): {sorted(produkty)}")
    print(f"\n  Zákazníci, ktorí si objednali Notebook:")
    print(f"    {sorted(zakaznici_produktu(objednavky, 'Notebook'))}")
    print(f"\n  Produkty Petra Kováča:")
    print(f"    {sorted(produkty_zakaznika(objednavky, 'Peter Kováč'))}")

    # ----------------------------------------------------------
    print(sep + "4. SLOVNÍKY")
    minuty = minuty_na_zakaznika(objednavky)
    print("  Minúté peniaze podľa zákazníka:")
    for m, s in sorted(minuty.items()):
        print(f"    {m:<22}: {s:>9.2f} €")

    kusy = predane_kusy_na_produkt(objednavky)
    print("\n  Predané kusy podľa produktu:")
    for p, k in sorted(kusy.items()):
        print(f"    {p:<15}: {k:>4} ks")

    pocty = pocet_objednavok_na_zakaznika(objednavky)
    print("\n  Počet objednávok podľa zákazníka:")
    for m, n in sorted(pocty.items()):
        print(f"    {m:<22}: {n:>4}")

    tz, tz_s = top_zakaznik(objednavky)
    tp, tp_k = top_produkt(objednavky)
    print(f"\n  Top zákazník         : {tz} ({tz_s:.2f} €)")
    print(f"  Najpredávanejší prod.: {tp} ({tp_k} ks)")

    # ----------------------------------------------------------
    print(sep + "5. ČÍSELNÉ POLE (array)")
    pole = vytvor_pole_cien(objednavky)
    stat = statistiky_cien(pole)
    print(f"  Pole cien : {list(pole)}")
    print(f"  Min       : {stat['min']:.2f} €")
    print(f"  Max       : {stat['max']:.2f} €")
    print(f"  Priemer   : {stat['priemer']:.2f} €")
    print(f"  Súčet     : {stat['sucet']:.2f} €")
    print(f"  Počet     : {stat['pocet']}")

    # ----------------------------------------------------------
    print(sep + "6. VNORENÉ DÁTA")
    vnorena = vytvor_vnorenu_strukturu(objednavky)
    print("  Objednávky Tomáša Blahu:")
    vypis_vsetky_objednavky(vnorena["Tomáš Blaho"])
    print(f"\n  Celková suma Tomáša Blahu: {suma_zakaznika(vnorena, 'Tomáš Blaho'):.2f} €")
    zmeno, pocet = zakaznik_s_najviac_objednavkami(vnorena)
    print(f"  Zákazník s najviac objednávkami: {zmeno} ({pocet})")
    print("\n  Súhrnný report:")
    suhrny_report_zakaznikov(vnorena)

    # ----------------------------------------------------------
    print(sep + "7. TRIEDENIE A VYHĽADÁVANIE")
    print("  Objednávky zoradené podľa ceny (zostupne):")
    vypis_vsetky_objednavky(zorad_podla_ceny(objednavky))

    print("\n  Objednávky zoradené podľa mena:")
    vypis_vsetky_objednavky(zorad_podla_mena(objednavky))

    print("\n  Produkty podľa predaných kusov:")
    for prod, ks in zorad_produkty_podla_kusov(objednavky):
        print(f"    {prod:<15}: {ks:>4} ks")

    print("\n  Všetky objednávky produktu 'Myš':")
    vypis_vsetky_objednavky(hladaj_objednavky_produktu(objednavky, "Myš"))

    print("\n  Zákazníci, ktorí minuli viac ako 1000 €:")
    for m, s in sorted(zakaznici_nad_sumu(objednavky, 1000), key=lambda x: x[1], reverse=True):
        print(f"    {m:<22}: {s:.2f} €")

    # ----------------------------------------------------------
    print(sep + "8. ZÁVEREČNÝ REPORT")
    vypis_report(objednavky)

    # ----------------------------------------------------------
    print(sep + "BONUS – pridanie, mazanie, úprava, export")

    # Pridanie
    pridaj_objednavku(objednavky, "Eva Tóthová", "Slúchadlá", 149.00, 3)
    print(f"  Objednávka pridaná. Celkový počet: {pocet_objednavok(objednavky)}")

    # Úprava
    upravene = uprav_pocet_kusov(objednavky, "Eva Tóthová", "Slúchadlá", 5)
    print(f"  Úprava počtu kusov: {'OK' if upravene else 'nenájdené'}")

    # Mazanie
    vymazane = vymaz_objednavky_zakaznika(objednavky, "Eva Tóthová")
    print(f"  Vymazaných {vymazane} objednávok zákazníka Eva Tóthová.")
    print(f"  Zostatok objednávok: {pocet_objednavok(objednavky)}")

    # Export
    export_report_do_suboru(objednavky, "sprava_obj_eshop/report.txt")

    # Ošetrenie prázdneho zoznamu
    print(sep + "Ošetrenie prázdneho zoznamu")
    prazdny: list[Objednavka] = []
    vypis_vsetky_objednavky(prazdny)
    pole_prazdne = vytvor_pole_cien(prazdny)
    print(f"  Štatistiky prázdneho zoznamu: {statistiky_cien(pole_prazdne)}")

    # Ošetrenie neexistujúceho zákazníka
    print(sep + "Ošetrenie neexistujúceho zákazníka")
    try:
        vnorena2 = vytvor_vnorenu_strukturu(objednavky)
        suma_zakaznika(vnorena2, "Neexistujúci Zákazník")
    except KeyError as e:
        print(f"  KeyError: {e}")

    # Validácia vstupov
    print(sep + "Validácia vstupných dát")
    for popis, args in [
        ("prázdne meno",       ("",           "Myš",  25.5, 2)),
        ("nulová cena",        ("Ján",         "Myš",  0.0,  2)),
        ("záporný počet ks",   ("Ján",         "Myš",  25.5, -1)),
    ]:
        try:
            pridaj_objednavku(objednavky, *args)
        except ValueError as e:
            print(f"  [{popis}] ValueError: {e}")


if __name__ == "__main__":
    main()
