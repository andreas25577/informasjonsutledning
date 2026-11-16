"""Bygger kildene til nettstedet (GitHub Pages) i mappen nettsted/.

Bruk: python verktoy/bygg_nettsted.py
Deretter: mkdocs build

Lager: forside med oversiktsdiagram, norske sider for modell og hjemler, begreper,
regler, annotering og kilder, og teknisk dokumentasjon fra LinkML (gen-doc).
"""
import csv, shutil, subprocess, sys
from pathlib import Path
import yaml
from linkml.generators.erdiagramgen import ERDiagramGenerator
from linkml_runtime.utils.schemaview import SchemaView

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "nettsted"
SKJEMA = ROT / "schema/domener/familieinnvandring.yaml"
ANALYSE = ROT / "analyse/familieinnvandring"
ADVARSEL = '!!! warning "Utkast"\n    Maskinelt utkast fra en pilot. Innholdet er ikke juridisk validert.\n'

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

def main():
    if UT.exists():
        shutil.rmtree(UT)
    UT.mkdir()
    sv = SchemaView(str(SKJEMA))
    kilder = {r["kilde_id"]: r for r in les("kilderegister.csv")}

    def lenker(ider):
        ut = []
        for k in ider.split():
            r = kilder.get(k)
            ut.append(f'[{k}](kilder.md#{k} "{celle(r["tekst"][:200]).replace(chr(34), chr(39))}")' if r else k)
        return ", ".join(ut)

    # Forside
    er = ERDiagramGenerator(str(SKJEMA)).serialize()
    (UT / "index.md").write_text(f"""# UDI regelverksmodell

Konseptuell informasjonsmodell utledet av utlendingsregelverket. Hver klasse, hvert attributt og hver relasjon kan spores til paragraf, ledd og punkt.

{ADVARSEL}
Piloten gjelder familieinnvandring. Foreløpig er bare utlendingsloven § 39 og § 40 analysert.

## Oversikt over modellen

{er}

## Innhold

- [Modell og hjemler](modell.md): klasser, attributter og relasjoner med hjemmel
- [Begreper](begreper.md): begreper med definisjon og kilde
- [Regler](regler.md): vilkår og avledningsregler som bruker opplysningene
- [Annotering](annotering.md): klassifisering av lovteksten etter Wetsanalyse
- [Kilder](kilder.md): lovteksten, delt i ledd og punkter
- [Teknisk dokumentasjon](teknisk/index.md): generert fra LinkML-skjemaet
""", encoding="utf-8")

    # Modell og hjemler
    o = ["# Modell og hjemler\n", ADVARSEL,
         "Kilde-ID-ene peker til [kilderegisteret](kilder.md). Hold pekeren over en ID for å se lovteksten.\n"]
    for c in sv.all_classes().values():
        o.append(f"## {c.title or c.name}\n")
        o.append(f"{c.description or ''}\n")
        if c.is_a:
            o.append(f"Arver fra: {sv.get_class(c.is_a).title or c.is_a}\n")
        o.append(f"Hjemmel: {lenker(ann(c, 'materiell_hjemmel'))} · Teknisk navn: [`{c.name}`](teknisk/{c.name}.md)\n")
        egne = [sv.induced_slot(n, c.name) for n in c.slots]
        if egne:
            o.append("| Attributt eller relasjon | Verdi | Beskrivelse | Materiell hjemmel | Behandlingsgrunnlag | Innhentingshjemmel | Særlig kategori |")
            o.append("| --- | --- | --- | --- | --- | --- | --- |")
            for s in egne:
                rng = sv.get_element(s.range) if s.range else None
                norsk = {"date": "dato", "boolean": "ja/nei", "string": "tekst", "integer": "heltall"}
                verdi = (getattr(rng, "title", None) or norsk.get(s.range, s.range) or "tekst") + (" (flere)" if s.multivalued else "")
                o.append(f"| {celle(s.title or s.name)} | {celle(verdi)} | {celle(s.description or '')} | {lenker(ann(s, 'materiell_hjemmel'))} | {lenker(ann(s, 'behandlingsgrunnlag'))} | {lenker(ann(s, 'innhentingshjemmel'))} | {celle(ann(s, 'saerlig_kategori')).replace('_', ' ')} |")
            o.append("")
    o.append("## Kodeverk\n")
    for e in sv.all_enums().values():
        o.append(f"### {e.title or e.name}\n\n{e.description or ''}\n")
        o.append("| Verdi | Hjemmel |\n| --- | --- |")
        for pv in e.permissible_values.values():
            o.append(f"| {celle(pv.title or pv.text)} | {lenker(ann(pv, 'materiell_hjemmel'))} |")
        o.append("")
    (UT / "modell.md").write_text("\n".join(o), encoding="utf-8")

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
    o = ["# Regler\n", ADVARSEL, "Vilkår og avledningsregler holdes utenfor informasjonsmodellen. Listen viser hvilke opplysninger hver regel bruker.\n",
         "| Regel | Kilde | Type | Beskrivelse | Bruker | Skjønn |", "| --- | --- | --- | --- | --- | --- |"]
    for r in les("regelliste.csv"):
        o.append(f"| {r['regel_id']} | {lenker(r['kilde_id'])} | {r['type'].replace('vilkar', 'vilkår')} | {celle(r['beskrivelse'])} | {celle(', '.join(r['bruker_attributter'].split()))} | {r['skjonn']} |")
    (UT / "regler.md").write_text("\n".join(o) + "\n", encoding="utf-8")

    # Annotering
    o = ["# Annotering\n", ADVARSEL, "Hvert tekstutdrag er klassifisert etter Wetsanalyse (Juridisch Analyseschema 1.0.10). Status viser om juristen har vurdert raden.\n",
         "| ID | Kilde | Tekstutdrag | Klasse | Foreslått term | Kommentar | Status |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in les("annotering.csv"):
        o.append(f"| {r['annotering_id']} | {lenker(r['kilde_id'])} | {celle(r['tekstutdrag'])} | {r['klasse'].replace('vilkar', 'vilkår')} | {celle(r['foreslatt_term'])} | {celle(r['kommentar'])} | {r['status']} |")
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

    # Teknisk dokumentasjon fra LinkML
    subprocess.run(["gen-doc", "-d", str(UT / "teknisk"), "--diagram-type", "mermaid_class_diagram", str(SKJEMA)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("nettsted bygget:", len(list(UT.rglob("*.md"))), "sider")

if __name__ == "__main__":
    sys.exit(main())
