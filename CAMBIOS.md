# Resumen de cambios — sesión de migración y pipeline

Trabajo realizado sobre myrenting.es (agosto 2026). Todo está en `main`.

## 1. Home nueva (diseño naranja)
- `index.html` regenerado: 72 modelos con **foto real**, **ficha técnica** (potencia, combustible, consumo, plazas) y **tarjeta blanca con borde naranja**.
- El diseño vive en `templates/home.html` (plantilla) → se rellena con datos y **sobrevive a cada regeneración**.
- 71 fotos WebP optimizadas en `/img/modelos/`.

## 2. Pipeline de datos (4 capas) — ver `ESTRUCTURA.md`
```
1 SCRAPE  → data/raw/*.json         (M Automoción, Quadis, Kia)
2 BUILD   → data/build/catalogo.json (merge + specs)
3 GENERATE→ index.html + landings + sitemap + llms.txt
4 QA      → valida; si falla, aborta
```
- `run_weekly.py` = 1 comando para actualizar cada lunes.
- **Fuente de verdad** por dato: specs→`data/master/modelos.json`, ofertas→scrapers+`ofertas-manuales.json`, ZBE→`data/master/ciudades-zbe.json`.
- Precedencia: `ofertas-manuales.json` (a mano, ej. Kia) **gana** sobre lo scrapeado.

## 3. Specs para todos los modelos
- `enrich_modelos.py`: upsert (añade si falta, rellena si está, idempotente).
- 72/72 modelos con specs (antes 34).

## 4. SEO / GEO
- `llms.txt`: índice para IAs con precio+specs de 69 modelos.
- `robots.txt`: permite 12 bots de IA (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…) + 2 sitemaps.
- `sitemap-modelos.xml`: 69 URLs verificadas (sin 404).
- Módulo `scripts/3_generate/generar_ciudades.py`: landings de ciudad con **bloque ZBE** que cruza etiqueta del coche × norma de la ciudad (contenido único). **Pendiente de decidir volumen antes de publicar.**

## 5. Datos de referencia
- `MODELOS_FUENTES_URLS.csv`: los 72 modelos con fuente y URLs.
- `SPECS_MODELOS.csv`, `data/master/ciudades-zbe.json` (16 ciudades con datos ZBE).

## Pendiente
- Decidir volumen de landings de ciudad (A: todas / B: ZBE con multa / C: top ciudades) y publicarlas.
- Añadir oferta **Kia Niro** (nacional, sin ciudad) en `data/master/ofertas-manuales.json`.
