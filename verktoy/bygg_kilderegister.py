"""Bygger kilderegister.csv fra Lovdatas åpne data (XML/HTML) ut fra avgrensning.csv.

Bruk: python bygg_kilderegister.py <avgrensning.csv> <lov.xml> <forskrift.xml> <ut.csv>
Én rad per ledd og per punkt (bokstav/nummer) i hver bestemmelse med status med/avklares.
"""
import csv, re, sys
from bs4 import BeautifulSoup

DOK = {
    "utlendingsloven": dict(pre="utl", niva="lov", ajour="2026-11-14"),
    "utlendingsforskriften": dict(pre="utf", niva="forskrift", ajour="2026-11-15"),
}

def ren(t):
    return re.sub(r"\s+", " ", t).strip()

def egen_tekst(node):
    """Tekst i noden uten nestede lister."""
    kopi = BeautifulSoup(str(node), "html.parser")
    for ol in kopi.find_all(["ol", "ul"]):
        ol.decompose()
    return ren(kopi.get_text(""))

def punkter(node, prefiks, ut, felles):
    for liste in node.find_all(["ol", "ul"], recursive=False):
        for li in liste.find_all("li", recursive=False):
            navn = (li.get("data-name") or "").strip().rstrip(".").replace(" ", "").lower()
            navn = re.sub(r"[^0-9a-z]", "", navn) or str(len(ut))
            kid = f"{prefiks}-{navn}"
            ut.append(dict(felles, kilde_id=kid, punkt=kid.split("-", 3)[-1] if kid.count("-") >= 3 else navn, tekst=egen_tekst(li)))
            for art in li.find_all("article", recursive=False):
                punkter(art, kid, ut, felles)
                for p in art.find_all("article", class_="legalP", recursive=False):
                    punkter(p, kid, ut, felles)

def main(avgr, lov, forskrift, utfil):
    supper = {"utlendingsloven": BeautifulSoup(open(lov, encoding="utf-8").read(), "html.parser"),
              "utlendingsforskriften": BeautifulSoup(open(forskrift, encoding="utf-8").read(), "html.parser")}
    meta = {}
    for k, s in supper.items():
        meta[k] = dict(dokument=s.find("dd", class_="legacyID").get_text(strip=True),
                       eli="https://lovdata.no" + s.find("dd", class_="eli").get_text(strip=True))
    ut, mangler = [], []
    for r in csv.DictReader(open(avgr, encoding="utf-8")):
        if r["kilde"] not in DOK or r["status"] == "ikke_med":
            continue
        d, s = DOK[r["kilde"]], supper[r["kilde"]]
        navn = r["bestemmelse"].replace(" ", "")
        art = s.find("article", attrs={"class": "legalArticle", "data-name": navn})
        if art is None:
            mangler.append(r["bestemmelse"]); continue
        pid = navn.lstrip("§").lower()
        felles = dict(kildeniva=d["niva"], dokument=meta[r["kilde"]]["dokument"], bestemmelse=r["bestemmelse"],
                      eli=meta[r["kilde"]]["eli"], lenke="https://lovdata.no/" + art.get("data-lovdata-url", ""),
                      ajourfort=d["ajour"], punkt="")
        for n, ledd in enumerate(art.find_all("article", class_="legalP", recursive=False), 1):
            kid = f"{d['pre']}-{pid}-{n}"
            f2 = dict(felles, ledd=n)
            ut.append(dict(f2, kilde_id=kid, tekst=egen_tekst(ledd)))
            punkter(ledd, kid, ut, f2)
    felt = ["kilde_id", "kildeniva", "dokument", "bestemmelse", "ledd", "punkt", "tekst", "eli", "lenke", "ajourfort"]
    with open(utfil, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=felt); w.writeheader(); w.writerows(ut)
    print("rader:", len(ut), "mangler:", mangler)

if __name__ == "__main__":
    main(*sys.argv[1:5])
