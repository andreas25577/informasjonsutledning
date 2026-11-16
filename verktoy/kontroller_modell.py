"""Kontrollerer sammenhengen mellom nivåene.

- Hvert konseptuelt element har materiell hjemmel, og alle kilde-ID-er finnes i kilderegisteret.
- Hvert logisk element realiserer et konseptuelt element som finnes.
- Regellisten viser bare til konseptuelle elementer som finnes.
- Lister konseptuelle elementer som ikke er realisert i den logiske modellen.

Bruk: python verktoy/kontroller_modell.py
"""
import csv, sys
from pathlib import Path
from linkml_runtime.utils.schemaview import SchemaView

ROT = Path(__file__).resolve().parent.parent
KONS = ROT / "schema/konseptuell/familieinnvandring.yaml"
LOGISK = ROT / "schema/domener/familieinnvandring.yaml"
ANALYSE = ROT / "analyse/familieinnvandring"

def ann(el, navn):
    try:
        a = el.annotations[navn]
    except (KeyError, AttributeError, TypeError):
        return ""
    return str(getattr(a, "value", a)).strip()

def konseptuelle_navn(sv):
    navn = set(sv.all_classes())
    for c in sv.all_classes():
        navn |= {f"{c}.{s.name}" for s in sv.class_induced_slots(c)}
    return navn

def main():
    feil = []
    kons, logisk = SchemaView(str(KONS)), SchemaView(str(LOGISK))
    ider = {r["kilde_id"] for r in csv.DictReader(open(ANALYSE / "kilderegister.csv", encoding="utf-8"))}
    for el in list(kons.all_classes().values()) + list(kons.all_slots().values()):
        if not ann(el, "materiell_hjemmel"):
            feil.append(f"konseptuell {el.name}: mangler materiell_hjemmel")
        for felt in ("materiell_hjemmel", "behandlingsgrunnlag", "innhentingshjemmel"):
            for k in ann(el, felt).split():
                if k not in ider:
                    feil.append(f"konseptuell {el.name}: {felt} peker på ukjent kilde-ID {k}")
    gyldige = konseptuelle_navn(kons)
    realisert = set()
    for el in list(logisk.all_classes().values()) + list(logisk.all_slots().values()):
        r = ann(el, "realiserer")
        if not r:
            feil.append(f"logisk {el.name}: mangler realiserer")
        elif r not in gyldige:
            feil.append(f"logisk {el.name}: realiserer ukjent konseptuelt element {r}")
        realisert.add(r)
    for r in csv.DictReader(open(ANALYSE / "regelliste.csv", encoding="utf-8")):
        for a in r["bruker_attributter"].split():
            if a not in gyldige:
                feil.append(f"regel {r['regel_id']}: bruker ukjent element {a}")
        if r["kilde_id"] not in ider:
            feil.append(f"regel {r['regel_id']}: ukjent kilde-ID {r['kilde_id']}")
    egne = set(kons.all_classes()) | {f"{c}.{s}" for c, k in kons.all_classes().items() for s in k.slots}
    ikke = sorted(egne - realisert)
    print(f"konseptuelle elementer: {len(egne)}, realisert i logisk modell: {len(egne & realisert)}")
    if ikke:
        print("ikke realisert (ikke en feil):", ", ".join(ikke))
    for x in feil:
        print("FEIL", x)
    return 1 if feil else 0

if __name__ == "__main__":
    sys.exit(main())
