"""Bygger hjemmelsmatrise.csv fra annotasjonene i et LinkML-skjema og kontrollerer alle kilde-ID-er.

Bruk: python bygg_hjemmelsmatrise.py <skjema.yaml> <kilderegister.csv> <ut.csv> [funn.csv]
Funn holdes utenfor det åpne repoet: de leses fra en egen fil og skrives bare til matrisen.
"""
import csv, sys
from linkml_runtime.utils.schemaview import SchemaView

def ann(el, navn):
    a = el.annotations.get(navn) if el.annotations else None
    return str(a.value).strip() if a is not None else ""

def main(skjema, register, utfil, funnfil=None):
    sv = SchemaView(skjema)
    ider = {r["kilde_id"] for r in csv.DictReader(open(register, encoding="utf-8"))}
    rader, feil = [], []
    funnliste = {r["element"]: r["funn"] for r in csv.DictReader(open(funnfil, encoding="utf-8"))} if funnfil else {}
    def sjekk(navn, felt, verdi):
        for k in verdi.split():
            if k not in ider:
                feil.append(f"{navn}: {felt} peker på ukjent kilde-ID {k}")
    for c in sv.all_classes().values():
        mh = ann(c, "materiell_hjemmel")
        if not mh: feil.append(f"{c.name}: mangler materiell_hjemmel")
        sjekk(c.name, "materiell_hjemmel", mh)
        rader.append(dict(element=c.name, type="klasse", visningsnavn=c.title or "", materiell_hjemmel=mh,
                          behandlingsgrunnlag="", innhentingshjemmel="", saerlig_kategori="", funn=""))
    for s in sv.all_slots().values():
        mh, bg, ih = ann(s, "materiell_hjemmel"), ann(s, "behandlingsgrunnlag"), ann(s, "innhentingshjemmel")
        funn = funnliste.get(s.name, "")
        if not mh: feil.append(f"{s.name}: mangler materiell_hjemmel")
        if not bg: feil.append(f"{s.name}: mangler behandlingsgrunnlag")
        if not ih and not funn: funn = "Ingen særskilt innhentingshjemmel registrert. Opplysningen kommer fra søknaden eller fra UDIs egne vedtak."
        for felt, v in (("materiell_hjemmel", mh), ("behandlingsgrunnlag", bg), ("innhentingshjemmel", ih)):
            sjekk(s.name, felt, v)
        rader.append(dict(element=s.name, type="attributt" if (s.range in sv.all_types() or s.range in sv.all_enums() or not s.range) else "relasjon",
                          visningsnavn=s.title or "", materiell_hjemmel=mh, behandlingsgrunnlag=bg, innhentingshjemmel=ih,
                          saerlig_kategori=ann(s, "saerlig_kategori"), funn=funn))
    with open(utfil, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rader[0])); w.writeheader(); w.writerows(rader)
    print("elementer:", len(rader), "feil:", len(feil))
    for x in feil: print("  FEIL", x)
    sys.exit(1 if feil else 0)

if __name__ == "__main__":
    main(*sys.argv[1:5])
