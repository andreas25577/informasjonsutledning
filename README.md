# UDI regelverksmodell

Informasjonsmodell utledet av utlendingsregelverket, i tre nivåer: begreper, konseptuell modell og logisk modell. Hver klasse, egenskap og relasjon kan spores til paragraf, ledd og punkt.

Status: pilot på familieinnvandring. Ingenting her er juridisk validert ennå.

## Innhold

| Mappe | Innhold |
| --- | --- |
| `schema/felles/` | Felles skjema: SKOS-AP-NO og logiske kjerneklasser |
| `schema/konseptuell/` | Konseptuell modell per fagområde. Hjemlene står her. |
| `schema/domener/`, `schema/kodeverk/` | Logisk modell og kodeverk. Peker til den konseptuelle modellen. |
| `schema/analyse.yaml` | Skjema som validerer arbeidsfilene |
| `begreper/` | Begreper som data etter SKOS-AP-NO |
| `analyse/<fagområde>/` | Avgrensning, kilderegister, annotering, regelliste |
| `verktoy/` | Skript som bygger kilderegister, hjemmelsmatrise og nettsted, og kontrollerer nivåene |
| `kilder/` | Kildefiler fra Lovdata (ikke i Git) |
| `generert/`, `docs/` | Generert fra skjemaene |

## Regelverksversjon

Piloten er låst til Lovdatas åpne data slik de var ajourført på nedlastingsdatoen. Datoen står i kilderegisteret.

| Kilde | Lovdata-ID | Sist endret ved (per 16.11.2026) |
| --- | --- | --- |
| Utlendingsloven | LOV-2008-05-15-35 | LOV-2026-06-19-50 (fra 01.07.2026) og LOV-2025-06-20-82 (fra 01.10.2026) |
| Utlendingsforskriften | FOR-2009-10-15-1286 | FOR-2026-10-19-2098 |

Kilde: Lovdata, åpne data under NLOD 2.0.

## Nettsted

Modellen vises på https://andreas25577.github.io/informasjonsutledning/. Nettstedet bygges og publiseres automatisk ved hver push til `main`.

Bygge lokalt:

```
pip install -r requirements.txt
python verktoy/bygg_nettsted.py
mkdocs serve
```

## Internt

Mappen `intern/` og hjemmelsmatrisen er ikke med i Git. De inneholder funn som ikke er juridisk vurdert.

## Validering

```
pip install linkml
linkml-lint schema/
linkml-validate -s schema/felles/skos-ap-no.yaml -C Begrepssamling begreper/familieinnvandring.yaml
python verktoy/kontroller_modell.py
```

## Metode

Se `docs/navnekonvensjoner.md` og `docs/provekjoring-utl-40.md`.
