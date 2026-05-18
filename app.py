"""
Flask webový frontend pre správu objednávok e-shopu.
Spustenie: python3 app.py
URL:       http://localhost:5000
"""

from decimal import Decimal

from flask import Flask, render_template, request, redirect, url_for, flash
#from objednavky_eshop import VZOROVE_OBJEDNAVKY
from src.service.Analytika import Analytika
from src.service.EshopDatabaza import EshopDatabaza
from src.service.Report import Report


VZOROVE_OBJEDNAVKY = [
    ("Anna Novakova",     "Notebook",      899.00, 1),
    ("Peter Kovac",       "Mys",            25.50, 3),
    ("Jana Horakova",     "Klavesnica",     45.00, 2),
    ("Anna Novakova",     "Monitor",       320.00, 2),
    ("Tomas Blaho",       "Notebook",      899.00, 1),
    ("Peter Kovac",       "Notebook",      899.00, 1),
    ("Jana Horakova",     "Mys",            25.50, 1),
    ("Martin Sloboda",    "Sluchadla",     149.00, 2),
    ("Tomas Blaho",       "Monitor",       320.00, 1),
    ("Martin Sloboda",    "Klavesnica",     45.00, 4),
    ("Lucia Mrkvickova",  "Webkamera",      79.90, 2),
    ("Marek Urban",       "USB-C kabel",    12.99, 5),
    ("Eva Fialova",       "Tablet",        429.00, 1),
    ("Norbert Sima",      "Externy disk",  119.90, 2),
    ("Lucia Mrkvickova",  "Monitor",       320.00, 1),
]

app = Flask(__name__)
app.secret_key = "eshop-dev-key"

# Globálna databáza (in-memory, reset pri reštarte servera)
db = EshopDatabaza()
for args in VZOROVE_OBJEDNAVKY:
    db.pridaj(*args)


# ── Pomocné ──────────────────────────────────────────────────
def get_analytika():
    return Analytika(db)


# ── Stránky ──────────────────────────────────────────────────

@app.route("/")
def index():
    an = get_analytika()
    stat = an.statistiky_cien()
    tz, tz_s = an.top_zakaznik()
    tp, tp_k = an.top_produkt()
    return render_template(
        "index.html",
        objednavky=db.vsetky,
        stat=stat,
        top_zakaznik=(tz, tz_s),
        top_produkt=(tp, tp_k),
        pocet_zakaznikov=len(an.unikatni_zakaznici),
        pocet_produktov=len(an.unikatne_produkty),
    )


@app.route("/objednavky")
def objednavky():
    zoradenie = request.args.get("sort", "default")
    hladany_zakaznik = request.args.get("zakaznik", "").strip()
    hladany_produkt = request.args.get("produkt", "").strip()
    min_suma = request.args.get("min_suma", "")

    zoznam = db.vsetky

    if hladany_zakaznik:
        zoznam = [o for o in zoznam if hladany_zakaznik.lower() in o.zakaznik.lower()]
    if hladany_produkt:
        zoznam = [o for o in zoznam if hladany_produkt.lower() in o.produkt.lower()]
    if min_suma:
        try:
            hranica = Decimal(min_suma)
            zoznam = [o for o in zoznam if o.celkova_cena > hranica]
        except ValueError:
            pass

    if zoradenie == "cena_desc":
        zoznam = sorted(zoznam, key=lambda o: o.celkova_cena, reverse=True)
    elif zoradenie == "cena_asc":
        zoznam = sorted(zoznam, key=lambda o: o.celkova_cena)
    elif zoradenie == "meno":
        zoznam = sorted(zoznam, key=lambda o: o.zakaznik)
    elif zoradenie == "produkt":
        zoznam = sorted(zoznam, key=lambda o: o.produkt)

    an = get_analytika()
    return render_template(
        "objednavky.html",
        objednavky=zoznam,
        zakaznici=sorted(an.unikatni_zakaznici),
        produkty=sorted(an.unikatne_produkty),
        sort=zoradenie,
        filter_zakaznik=hladany_zakaznik,
        filter_produkt=hladany_produkt,
        filter_min_suma=min_suma,
    )


@app.route("/analytika")
def analytika():
    an = get_analytika()
    return render_template(
        "analytika.html",
        minuty=sorted(an.minuty_na_zakaznika().items(), key=lambda x: x[1], reverse=True),
        kusy=sorted(an.predane_kusy_na_produkt().items(), key=lambda x: x[1], reverse=True),
        pocty=sorted(an.pocet_objednavok_na_zakaznika().items(), key=lambda x: x[1], reverse=True),
        pole_cien=list(an.pole_cien()),
        stat=an.statistiky_cien(),
    )


@app.route("/pridat", methods=["GET", "POST"])
def pridat():
    if request.method == "POST":
        try:
            db.pridaj(
                request.form["zakaznik"],
                request.form["produkt"],
                request.form["cena_za_kus"],
                int(request.form["pocet_kusov"]),
            )
            flash("Objednávka bola úspešne pridaná.", "success")
            return redirect(url_for("objednavky"))
        except (ValueError, KeyError) as e:
            flash(f"Chyba: {e}", "error")
    return render_template("pridat.html")


@app.route("/uprav/<zakaznik>/<produkt>", methods=["POST"])
def uprav(zakaznik, produkt):
    try:
        novy_pocet = int(request.form["pocet_kusov"])
        db.uprav_pocet_kusov(zakaznik, produkt, novy_pocet)
        flash("Počet kusov bol upravený.", "success")
    except ValueError as e:
        flash(f"Chyba: {e}", "error")
    return redirect(url_for("objednavky"))


@app.route("/vymaz/<zakaznik>")
def vymaz(zakaznik):
    pocet = db.vymaz_zakaznika(zakaznik)
    flash(f"Vymazaných {pocet} objednávok zákazníka {zakaznik}.", "success")
    return redirect(url_for("objednavky"))



if __name__ == "__main__":
    app.run(debug=True, port=5000)
