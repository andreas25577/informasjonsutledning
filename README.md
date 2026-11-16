# UDI regelverksmodell

Konseptuell informasjonsmodell utledet av utlendingsregelverket. Hver klasse, hvert attributt og hver relasjon kan spores til paragraf, ledd og punkt.

Status: pilot på familieinnvandring. Ingenting her er juridisk validert ennå.

## Innhold

| Mappe | Innhold |
| --- | --- |
| `schema/felles/` | Felles skjema: SKOS-AP-NO, rettskilde, typer, kjerneklasser |
| `schema/kodeverk/` | Ett kodeverk per fil |
| `schema/domener/` | Én modell per fagområde |
| `schema/analyse.yaml` | Skjema som validerer arbeidsfilene |
| `begreper/` | Begreper som data etter SKOS-AP-NO |
| `analyse/<fagområde>/` | Avgrensning, kilderegister, annotering, regelliste, hjemmelsmatrise |
| `kilder/` | Kildefiler fra Lovdata (ikke i Git) |
| `generert/`, `docs/` | Generert fra skjemaene |

## Regelverksversjon

Piloten er låst til Lovdatas åpne data slik de var ajourført på nedlastingsdatoen. Datoen står i kilderegisteret.

| Kilde | Lovdata-ID | Sist endret ved (per 16.11.2026) |
| --- | --- | --- |
| Utlendingsloven | LOV-2008-05-15-35 | LOV-2026-06-19-50 (fra 01.07.2026) og LOV-2025-06-20-82 (fra 01.10.2026) |
| Utlendingsforskriften | FOR-2009-10-15-1286 | FOR-2026-10-19-2098 |

Kilde: Lovdata, åpne data under NLOD 2.0.

## Validering

```
pip install linkml
linkml-lint schema/
linkml-validate -s schema/felles/skos-ap-no.yaml -C Begrepssamling tests/data/eksempel-begrepssamling.yaml
```

## Metode

Se `METODE.md` og `docs/navnekonvensjoner.md`.
