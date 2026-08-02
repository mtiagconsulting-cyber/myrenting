# Estructura de datos y actualización — myrenting.es

Objetivo: que al **actualizar cada semana** todo esté ordenado, sepamos **qué fichero alimenta a qué**, y **nada se rompa**.

## Regla de oro
**Los datos y el HTML nunca se mezclan. El HTML SIEMPRE se genera; nunca se edita a mano.**
Si editas un `.html` a mano, la siguiente actualización lo sobrescribe.

## Las 4 capas

```
[1 SCRAPE]  fuentes  ─►  data/raw/*.json         (crudo, se pisa cada semana)
[2 BUILD]   merge    ─►  data/build/catalogo.json (lo único que leen los generadores)
[3 GENERATE] plantillas ─► index.html + landings + sitemap + llms.txt
[4 QA]      valida   ─►  si falla, ABORTA y no publica
```

## Qué fichero coge de qué (fuente de la verdad)

| Fichero | Qué es | Quién lo escribe | Manda sobre |
|---|---|---|---|
| `data/raw/mautomocion.json` | ofertas M Automoción (crudo) | scraper | — |
| `data/raw/quadis.json` | ofertas Quadis (crudo) | scraper | — |
| `data/master/ofertas-manuales.json` | **Kia** + correcciones a mano | TÚ | **gana** sobre lo scrapeado |
| `data/master/modelos.json` | specs por modelo (potencia, etiqueta DGT, consumo, plazas, imagen) | curado | enriquece |
| `data/master/ciudades-zbe.json` | datos ZBE por ciudad (para GEO) | curado | — |
| `data/build/catalogo.json` | **merge final** (raw + manuales + specs) | `build_catalogo.py` | lo consumen los generadores |

**Precedencia:** `ofertas-manuales.json` (a mano) **>** scrapeado. `modelos.json` añade specs. Un modelo que esté en manuales no desaparece aunque el scraping no lo traiga.

## Actualización semanal (cada lunes) = 1 comando

```bash
python3 run_weekly.py                 # ciclo completo: scrape → build → generate → qa → commit
python3 run_weekly.py --sin-scrape    # usa data/raw actual (no vuelve a scrapear)
python3 run_weekly.py --sin-publicar  # genera y valida, pero NO commitea (para revisar antes)
```

Si cualquier paso falla, el ciclo **se detiene y no publica nada**.

## Dónde meto la oferta de Kia
En `data/master/ofertas-manuales.json` (hay una plantilla dentro). Formato por oferta:
`fuente, tipo (particular/empresa/autonomo), make, model, version, fuel, precio_desde, duracion, km, url, image, combinaciones[]`.

## Carpetas
```
data/
  raw/      ← crudo de scrapers (NO versionado)
  master/   ← fuente de verdad (SÍ versionado): modelos, ofertas-manuales, ciudades-zbe
  build/    ← intermedio catalogo.json (NO versionado)
scripts/
  1_scrape/   run_scrapers.py
  2_build/    build_catalogo.py  ·  migrar_datos.py (única vez)
  3_generate/ generar_todo.py
  4_qa/       validar.py
templates/    ← plantillas HTML (aquí vivirá el diseño naranja)
run_weekly.py ← orquestador
```

## GEO (novedades ya incluidas)
- `llms.txt` — índice para IAs con precio+specs de cada modelo (dato directo, citable).
- `robots.txt` — permite explícitamente GPTBot, ClaudeBot, PerplexityBot, Google-Extended…
- Cada landing lleva JSON-LD `Product` + `Car` + oferta agregada.
