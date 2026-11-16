"""Bygger kildene til nettstedet (GitHub Pages) i mappen nettsted/.

Bruk: python verktoy/bygg_nettsted.py
Deretter: mkdocs build

Lager: forside med oversiktsdiagram, norske sider for konseptuell og logisk modell,
begreper, regler, annotering og kilder, OWL-eksport av den konseptuelle modellen
og teknisk dokumentasjon fra LinkML (gen-doc).
"""
import csv, shutil, subprocess, sys
from pathlib import Path
import yaml
from linkml.generators.erdiagramgen import ERDiagramGenerator
from linkml_runtime.utils.schemaview import SchemaView

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "nettsted"
KONS = ROT / "schema/konseptuell/familieinnvandring.yaml"
LOGISK = ROT / "schema/domener/familieinnvandring.yaml"
ANALYSE = ROT / "analyse/familieinnvandring"
ADVARSEL = '!!! warning "Utkast"\n    Maskinelt utkast fra en pilot. Innholdet er ikke juridisk validert.\n'
JAS = {"vilkar": "vilkår"}
NORSK = {"date": "dato", "boolean": "ja/nei", "string": "tekst", "integer": "heltall", "Verdi": "verdi"}

def les(navn):
    return list(csv.DictReader(open(ANALYSE / navn, encoding="utf-8")))

def celle(t):
    return str(t).replace("|", "\\|").replace("\n", " ")

def ann(el, navn):
    try:
        a = el.annotations[navn]
    except (KeyError, AttributeError, TypeError):
        return ""
    return str(getattr(a, "value", a)).strip()

def verdi(sv, s):
    navn = s.range or sv.schema.default_range
    rng = sv.get_element(navn) if navn else None
    v = NORSK.get(navn) or getattr(rng, "title", None) or navn or "verdi"
    return v + (" (flere)" if s.multivalued else "")

def main():
    if UT.exists():
        shutil.rmtree(UT)
    UT.mkdir()
    kons, logisk = SchemaView(str(KONS)), SchemaView(str(LOGISK))
    kilder = {r["kilde_id"]: r for r in les("kilderegister.csv")}

    def lenker(ider):
        ut = []
        for k in ider.split():
            r = kilder.get(k)
            ut.append(f'[{k}](kilder.md#{k} "{celle(r["tekst"][:200]).replace(chr(34), chr(39))}")' if r else k)
        return ", ".join(ut)

    def kons_navn(peker):
        """Visningsnavn for et konseptuelt element, f.eks. Person.alder -> Person: alder."""
        if "." in peker:
            c, s = peker.split(".", 1)
            return f"{kons.get_class(c).title or c}: {kons.get_slot(s).title or s}"
        return kons.get_class(peker).title or peker

    # Forside
    er = ERDiagramGenerator(str(KONS)).serialize().replace("Verdi ", "verdi ").replace("VerdiList ", "verdi ")
    (UT / "index.md").write_text(f"""# UDI regelverksmodell

Informasjonsmodell utledet av utlendingsregelverket. Hver klasse, egenskap og relasjon kan spores til paragraf, ledd og punkt.

{ADVARSEL}
Piloten gjelder familieinnvandring. Foreløpig er bare utlendingsloven § 39 og § 40 analysert.

## Tre nivåer

| Nivå | Innhold | Hjemmel |
| --- | --- | --- |
| [Begreper](begreper.md) | Termer og definisjoner etter SKOS-AP-NO | Kilde på definisjonen |
| [Konseptuell modell](konseptuell.md) | Det regelverket selv nevner: hvem og hva reglene gjelder, forholdene mellom dem og egenskapene vilkårene bygger på. Ingen datatyper. | Hjemlene står her |
| [Logisk modell](logisk.md) | Datatyper, ja/nei-felt og kodeverk | Peker til det konseptuelle elementet den realiserer |

## Oversikt over den konseptuelle modellen

{er}

## Mer

- [Regler](regler.md): vilkår og avledningsregler som bruker opplysningene
- [Annotering](annotering.md): klassifisering av lovteksten etter Wetsanalyse
- [Kilder](kilder.md): lovteksten, delt i ledd og punkter
- [Konseptuell modell som OWL](nedlasting/familieinnvandring-konseptuell.owl.ttl)
- Teknisk dokumentasjon fra LinkML: [konseptuell](teknisk/konseptuell/index.md) og [logisk](teknisk/logisk/index.md)
""", encoding="utf-8")

    # Konseptuell modell
    o = ["# Konseptuell modell\n", ADVARSEL,
         "Modellen gjengir det regelverket selv nevner, uten datatyper. Kilde-ID-ene peker til [kilderegisteret](kilder.md). Hold pekeren over en ID for å se lovteksten.\n"]
    for c in kons.all_classes().values():
        o.append(f"## {c.title or c.name}\n")
        o.append(f"{c.description or ''}\n")
        linje = f"Klasse i Wetsanalyse: {JAS.get(ann(c, 'jas_klasse'), ann(c, 'jas_klasse'))} · Hjemmel: {lenker(ann(c, 'materiell_hjemmel'))}"
        if c.is_a:
            linje += f" · Underordnet: {kons.get_class(c.is_a).title or c.is_a}"
        o.append(linje + "\n")
        if c.slots:
            o.append("| Egenskap eller relasjon | Peker til | Beskrivelse | Klasse i Wetsanalyse | Materiell hjemmel | Behandlingsgrunnlag | Innhentingshjemmel | Særlig kategori |")
            o.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
            for n in c.slots:
                s = kons.get_slot(n)
                skjonn = " (skjønnsmessig vurdering)" if ann(s, "skjonnsmessig_vurdering") else ""
                o.append(f"| {celle(s.title or s.name)} | {celle(verdi(kons, s))} | {celle(s.description or '')}{skjonn} | {JAS.get(ann(s, 'jas_klasse'), ann(s, 'jas_klasse'))} | {lenker(ann(s, 'materiell_hjemmel'))} | {lenker(ann(s, 'behandlingsgrunnlag'))} | {lenker(ann(s, 'innhentingshjemmel'))} | {celle(ann(s, 'saerlig_kategori')).replace('_', ' ')} |")
            o.append("")
    (UT / "konseptuell.md").write_text("\n".join(o), encoding="utf-8")

    # Logisk modell
    o = ["# Logisk modell\n", ADVARSEL,
         "Den logiske modellen realiserer den [konseptuelle modellen](konseptuell.md) med datatyper, ja/nei-felt og kodeverk. Disse valgene har ingen egen hjemmel. Hjemmelen følger av det konseptuelle elementet hvert element realiserer.\n"]
    realisert = set()
    for c in logisk.all_classes().values():
        r = ann(c, "realiserer"); realisert.add(r)
        o.append(f"## {c.title or c.name}\n")
        o.append(f"Realiserer: {kons_navn(r)}" + (f" · Underordnet: {logisk.get_class(c.is_a).title or c.is_a}" if c.is_a else "") + "\n")
        if ann(c, "designvalg"):
            o.append(f"Designvalg: {ann(c, 'designvalg')}\n")
        if c.slots:
            o.append("| Attributt eller relasjon | Verdi | Realiserer | Designvalg |\n| --- | --- | --- | --- |")
            for n in c.slots:
                s = logisk.get_slot(n); r = ann(s, "realiserer"); realisert.add(r)
                o.append(f"| {celle(s.title or s.name)} | {celle(verdi(logisk, s))} | {celle(kons_navn(r))} | {celle(ann(s, 'designvalg'))} |")
            o.append("")
    o.append("## Kodeverk\n")
    for e in logisk.all_enums().values():
        o.append(f"### {e.title or e.name}\n\n{e.description or ''}\n")
        o.append("| Verdi |\n| --- |")
        for pv in e.permissible_values.values():
            o.append(f"| {celle(pv.title or pv.text)} |")
        o.append("")
    egne = set(kons.all_classes()) | {f"{c}.{s}" for c, k in kons.all_classes().items() for s in k.slots}
    ikke = sorted(egne - realisert)
    if ikke:
        o.append("## Konseptuelle elementer uten egen realisering\n")
        o.append("Disse elementene i den konseptuelle modellen har ikke et eget element i den logiske modellen. Noen er dekket indirekte, for eksempel en hendelse som er forenklet til en dato.\n")
        o += [f"- {kons_navn(x)}" for x in ikke]
    (UT / "logisk.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Begreper
    b = yaml.safe_load(open(ROT / "begreper/familieinnvandring.yaml", encoding="utf-8"))
    forhold = {"sitat_fra_kilde": "sitat fra kilde", "basert_pa_kilde": "basert på kilde", "egendefinert": "egendefinert"}
    o = ["# Begreper\n", ADVARSEL, "Begrepene følger SKOS-AP-NO. Alle har status kandidat.\n",
         "| Anbefalt term | Definisjon | Forhold til kilde | Kilde | Merknad |", "| --- | --- | --- | --- | --- |"]
    for x in b["begreper"]:
        d = x["definisjon"][0]
        o.append(f"| {celle(x['anbefalt_term']['nb'])} | {celle(d['tekst']['nb'])} | {forhold.get(d.get('forhold_til_kilde'), '')} | {lenker(' '.join(d.get('kilde', [])))} | {celle(' '.join(m['nb'] for m in x.get('merknad', [])))} |")
    (UT / "begreper.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Regler
    o = ["# Regler\n", ADVARSEL, "Vilkår og avledningsregler holdes utenfor informasjonsmodellen. Listen viser hvilke elementer i den konseptuelle modellen hver regel bruker.\n",
         "| Regel | Kilde | Type | Beskrivelse | Bruker | Skjønn |", "| --- | --- | --- | --- | --- | --- |"]
    for r in les("regelliste.csv"):
        o.append(f"| {r['regel_id']} | {lenker(r['kilde_id'])} | {JAS.get(r['type'], r['type'])} | {celle(r['beskrivelse'])} | {celle('; '.join(kons_navn(a) for a in r['bruker_attributter'].split()))} | {r['skjonn']} |")
    (UT / "regler.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Annotering
    o = ["# Annotering\n", ADVARSEL, "Hvert tekstutdrag er klassifisert etter Wetsanalyse (Juridisch Analyseschema 1.0.10). Status viser om juristen har vurdert raden.\n",
         "| ID | Kilde | Tekstutdrag | Klasse | Foreslått term | Kommentar | Status |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in les("annotering.csv"):
        o.append(f"| {r['annotering_id']} | {lenker(r['kilde_id'])} | {celle(r['tekstutdrag'])} | {JAS.get(r['klasse'], r['klasse'])} | {celle(r['foreslatt_term'])} | {celle(r['kommentar'])} | {r['status']} |")
    (UT / "annotering.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Kilder
    o = ["# Kilder\n", "Lovteksten er hentet fra Lovdatas åpne data (NLOD 2.0) og delt i ledd og punkter. Hver rad har en kilde-ID som modellen viser til.\n"]
    forrige = None
    for r in kilder.values():
        nokkel = (r["dokument"], r["bestemmelse"])
        if nokkel != forrige:
            navn = "Utlendingsloven" if r["kildeniva"] == "lov" else "Utlendingsforskriften"
            o.append(f"\n## {navn} {r['bestemmelse']}\n\n[Åpne hos Lovdata]({r['lenke'].replace('§', '%C2%A7')}) · ajourført {r['ajourfort']}\n")
            forrige = nokkel
        innrykk = "    " * (r["kilde_id"].count("-") - (2 if r["kildeniva"] == "lov" else 3))
        o.append(f'{innrykk}- <span id="{r["kilde_id"]}"></span>`{r["kilde_id"]}` {r["tekst"]}')
    (UT / "kilder.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Håndskrevne sider
    for f in ("navnekonvensjoner.md", "provekjoring-utl-40.md"):
        shutil.copy(ROT / "docs" / f, UT / f)

    # OWL-eksport og teknisk dokumentasjon fra LinkML
    (UT / "nedlasting").mkdir()
    with open(UT / "nedlasting/familieinnvandring-konseptuell.owl.ttl", "w", encoding="utf-8") as f:
        subprocess.run(["gen-owl", str(KONS)], check=True, stdout=f, stderr=subprocess.DEVNULL)
    for navn, skjema in (("konseptuell", KONS), ("logisk", LOGISK)):
        subprocess.run(["gen-doc", "-d", str(UT / "teknisk" / navn), "--diagram-type", "mermaid_class_diagram", str(skjema)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("nettsted bygget:", len(list(UT.rglob("*.md"))), "sider")

if __name__ == "__main__":
    sys.exit(main())
