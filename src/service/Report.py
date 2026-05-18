import csv
from datetime import datetime
from html import escape

from src.service.Analytika import Analytika
from src.service.EshopDatabaza import EshopDatabaza


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

