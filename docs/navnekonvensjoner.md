# Navnekonvensjoner

## Språk og skrivemåte

| Element | Regel | Eksempel |
| --- | --- | --- |
| Klasse | Norsk, entall, stor forbokstav i hvert ord, uten æøå | `Soker`, `Referanseperson` |
| Attributt og relasjon | Norsk, små bokstaver, understrek, uten æøå | `fodselsdato`, `er_gift_med` |
| Kodeverk | Som klasse | `Sivilstand` |
| Kodeverdi | Som attributt | `gift`, `samboer` |
| Visningsnavn | Korrekt norsk i `title` | `Søker`, `fødselsdato` |
| Filnavn | Små bokstaver, bindestrek, uten æøå | `familieinnvandring.yaml` |

Æ, ø og å skrives `ae`, `o` og `a` i navn. Visningsnavnet i `title` har alltid riktig skrivemåte.

## Kilde-ID

En kilde-ID peker på ett ledd, punkt eller bokstav i kilderegisteret.

Mønster: `<kilde>-<paragraf>-<ledd>[-<bokstav eller nummer>]`

| Kilde | Forkortelse | Eksempel | Betyr |
| --- | --- | --- | --- |
| Utlendingsloven | `utl` | `utl-40-1` | § 40 første ledd |
| Utlendingsloven | `utl` | `utl-40a-2` | § 40 a annet ledd |
| Utlendingsloven | `utl` | `utl-40-1-c` | § 40 første ledd bokstav c |
| Utlendingsforskriften | `utf` | `utf-10-8-1` | § 10-8 første ledd |
| Personopplysningsloven | `popl` | `popl-1-1` | § 1 første ledd |
| Personvernforordningen | `gdpr` | `gdpr-6-1-e` | artikkel 6 nr. 1 bokstav e |
| Forvaltningsloven | `fvl` | | |

## Moduler og import

Lagene importerer bare nedover: `domener` → `kodeverk` → `felles`. Et fagområde importerer aldri et annet fagområde.

## Nivåer

| Nivå | Mappe | Innhold |
| --- | --- | --- |
| Begreper | `begreper/` | Termer og definisjoner etter SKOS-AP-NO |
| Konseptuell modell | `schema/konseptuell/` | Klasser, egenskaper og relasjoner slik regelverket nevner dem. Ingen datatyper. |
| Logisk modell | `schema/domener/`, `schema/felles/kjerne.yaml`, `schema/kodeverk/` | Datatyper, ja/nei-felt og kodeverk |

## Hjemmel på modellelementer

Hjemlene står i den konseptuelle modellen. Hver klasse, egenskap og relasjon har annotasjonene `jas_klasse` (klassen i Wetsanalyse), `materiell_hjemmel` og `kildeniva`. Egenskaper og relasjoner har også `behandlingsgrunnlag`, `innhentingshjemmel` og `saerlig_kategori`. Verdiene er kilde-ID-er, ikke fritekst.

Hvert element i den logiske modellen har annotasjonen `realiserer`, som peker til et konseptuelt element (`Person.alder`). `designvalg` forklarer valg som ikke følger av regelverket. `verktoy/kontroller_modell.py` kontrollerer pekerne.

## URI

Basis-URI er foreløpig `https://w3id.org/udi/regelverksmodell/`. Den bestemmes endelig før publisering.
