# Hoja maestra SEO/GEO

Estados: `HECHO`, `SIGUIENTE`, `PENDIENTE`. Cada acción debe cerrarse solo después de ejecutar su verificación.

| ID | Pri. | Estado | Archivo o superficie | Modificación | Verificación | Impacto esperado |
|---|---|---|---|---|---|---|
| 001 | P0 | HECHO | `src/app/page.tsx` | Derivar cantidades de vehículos y combinaciones | Build + inspeccionar description | Precisión y confianza |
| 002 | P0 | HECHO | `src/app/informes/renting-espana-2026/page.tsx` | Eliminar cifras antiguas de metadata | Comparar metadata con JSON | Precisión GEO |
| 003 | P0 | HECHO | `src/app/respuestas/page.tsx` | Derivar número de respuestas | Build + contar FAQs | Evita desactualización |
| 004 | P0 | HECHO | `src/components/seo/Schema.tsx` | Omitir potencia/maletero desconocidos | Validar ficha con datos nulos | Schema válido |
| 005 | P0 | HECHO | `src/app/coches/[slug]/page.tsx` | Calcular realmente el precio mínimo | Comparar title, ficha y ofertas | CTR y exactitud |
| 006 | P0 | HECHO | `src/app/llms.txt/route.ts` | Usar `contentSlug()` para marcas | Comprobar LYNK&CO y Mercedes-Benz | Acceso de agentes |
| 007 | P1 | HECHO | `src/app/sitemap.ts` | Usar fecha del inventario, no del build | Dos builds sin cambios producen misma fecha | Freshness honesto |
| 008 | P0 | HECHO | Todas las rutas sitemap | Auditor automático de asset/canonical/H1/noindex | 317 URLs, cero fallos | Crawlability |
| 009 | P0 | HECHO | `scripts/seo/` | Validar todos los JSON-LD del build | Cero JSON inválido o valores nulos | Rich results/GEO |
| 010 | P0 | HECHO | Inventario | Detectar ofertas huérfanas y vehículos sin oferta | Cero referencias rotas | Integridad comercial |
| 011 | P0 | HECHO | Inventario | Detectar duplicados por vehículo/perfil/plazo/km | Cero combinaciones duplicadas | Calidad de catálogo |
| 012 | P0 | HECHO | Oferta y formulario | Probar payload de email, WhatsApp y analítica sin enviar | Todos los campos coinciden | Leads correctos |
| 013 | P0 | HECHO | Oferta y formulario | Registrar email solo tras éxito; WhatsApp al abrir canal | Auditoría de eventos superada | Analítica fiable |
| 014 | P0 | HECHO | Cloudflare | Caché diferenciada para metadata y assets versionados | 200 + MIME + Cache-Control verificados | Acceso crawler |
| 015 | P0 | HECHO | Search Console | Inspeccionar inicio, ficha, marca, categoría, respuesta, comparación, blog e informe | Plantillas indexadas; informe apto y solicitado | Indexación |
| 016 | P1 | HECHO | `Schema.tsx` | Identificadores consistentes entre WebPage, Product, Vehicle, WebSite y Organization | Auditoría JSON-LD | Entidad coherente |
| 017 | P1 | HECHO | Vehicle Schema | Cuota modelada con `UnitPriceSpecification` mensual | 202 fichas validadas | Semántica comercial |
| 018 | P1 | PENDIENTE | Vehicle Schema | Añadir `priceValidUntil` solo si la fuente lo aporta | Test contra fecha real | Freshness de oferta |
| 019 | P1 | HECHO | Vehicle Schema | Perfil, kilómetros, plazo, entrada e IVA estructurados | Campos exigidos por auditor | Comprensión IA |
| 020 | P1 | HECHO | Listing Schema | Catálogo canonicalizado e ItemList limitado a vehículos activos | Sitemap y build: 202 fichas únicas | Coherencia |
| 021 | P1 | HECHO | Article/Report Schema | Unificar author/publisher/@id/dateModified | Auditor automático del grafo editorial | Autoridad editorial |
| 022 | P1 | HECHO | Open Graph | Metadata específica y foto real en fichas; tarjeta de marca para el resto | Auditor de `og:title` + build | Compartidos/CTR |
| 023 | P1 | HECHO | Metadata fichas | Incluir IVA/perfil cuando sea inequívoco | Typecheck, build y auditor SEO | Relevancia comercial |
| 024 | P1 | NO APLICA | Sitemap | Separar índices solo al superar 50.000 URLs; catálogo actual muy inferior | Control de número de URLs | Escalabilidad |
| 025 | P1 | HECHO | Sitemap | Incluir solo URLs canónicas 200 e indexables | Cruce auditor/sitemap | Crawl budget |
| 026 | P1 | HECHO | Marcas | Introducción calculada desde modelos, precios y perfiles reales | Build cambia con inventario | Long-tail citable |
| 027 | P1 | HECHO | Modelos | Agrupar variantes por modelo y perfil | 69 URLs estables generadas desde inventario | Arquitectura SEO |
| 028 | P1 | HECHO | Categorías | Separar particular/autónomo/empresa sin duplicar texto | Canonicals y contenido diferenciados | Intención correcta |
| 029 | P1 | HECHO | Categorías | Añadir páginas por combustible con inventario suficiente | 5 combustibles, todos con más de 20 vehículos | Cobertura temática |
| 030 | P1 | HECHO | Enlazado interno | Breadcrumb + marca + modelo + categoría + combustible | Enlaces desde cada ficha | Descubrimiento |
| 031 | P1 | HECHO | Catálogo | URLs de filtros: indexables solo si tienen demanda y contenido | `matriz-facetas.md` + sitemap sin parámetros | Evita facetas basura |
| 032 | P1 | HECHO | Respuestas | Sustituir revisión fija por fecha editorial centralizada | Fecha visible = Schema | Confianza |
| 033 | P1 | HECHO | Respuestas | Fuentes primarias de Agencia Tributaria en fiscalidad | Enlaces y fecha de revisión visibles | E-E-A-T |
| 034 | P1 | HECHO | Comparativas | Comparar primero público, plazo y kilómetros idénticos | Aviso explícito si no existe igualdad | Citas IA |
| 035 | P1 | HECHO | Comparativas | Evitar “no incluido” cuando el dato es desconocido | Tres estados: sí/no/no consta | Precisión |
| 036 | P1 | HECHO | Fichas | Mostrar procedencia y fecha por oferta | Fuente trazable visible | Confianza/lead |
| 037 | P1 | HECHO | Fichas | Publicar consumo/maletero solo si constan y enlazar fuente | Pendientes visibles como “Consultar” | Contenido útil |
| 038 | P1 | HECHO | `llms.txt` | Añadir informes, metodología, modelos y combustibles | Auditor de secciones prioritarias | Descubrimiento IA |
| 039 | P2 | HECHO | Informes | Índice mensual de cuotas por perfil y dataset JSON | Tabla, metodología y datos reproducibles | Citaciones externas |
| 040 | P2 | HECHO | Informes | Histórico de mínimos/medianas por marca iniciado en 2026-08 | Snapshot mensual persistente | Autoridad propia |
| 041 | P2 | HECHO | Informes | Estudio de entrada, cuota y coste total sin inventar muestras | Fórmula y limitación visibles | Diferenciación |
| 042 | P2 | HECHO | Opiniones | Invitación única, consentimiento, moderación y retirada | Flujo D1 existente y texto visible | Reviews reales |
| 043 | P2 | HECHO | Opiniones | Metodología de verificación y `CollectionPage` Schema | Texto, política y Schema auditables | Confianza |
| 044 | P2 | REQUIERE PERFILES | Organization Schema | Identidad legal y contacto añadidos; `sameAs` espera perfiles oficiales | No publicar enlaces no confirmados | Entidad de marca |
| 045 | P2 | PREPARADO | Autoridad externa | NAP canónico y checklist de elegibilidad documentados | Falta dirección/perfiles confirmados | Confianza local |
| 046 | P2 | PREPARADO | Digital PR | Sala de prensa, cita sugerida y dataset canónico publicados | Falta distribución externa | Autoridad |
| 047 | P2 | LISTO PARA DESPLEGAR | GTM/GA4 | Capturar referrer, UTM, fuente IA y landing; heredar en lead | GTM v5 publicado; falta desplegar la aplicación y comprobar producción | Atribución IA |
| 048 | P2 | HECHO | Analítica | Eventos GA4 y dimensiones personalizadas para canal, fuente IA, landing, referente y campaña | 5 dimensiones creadas; marcar `generate_lead` como evento clave tras su primera recepción | AI leads |
| 049 | P2 | PREPARADO | Benchmark | 100 consultas, plantilla y calculadora AI Share of Voice | Faltan 300 observaciones reales | AI Share of Voice |
| 050 | P3 | PREPARADO | Experimentos | Registro de answer-first, tablas y fuentes por cohortes | Requiere dos ciclos mensuales | Mejora continua |

## Cierre operativo

1. Desplegar el build de producción ya generado y verificar `traffic_attribution` en `myrenting.es`.
2. Tras el primer envío de formulario, marcar `generate_lead` como evento clave en GA4.
3. Completar `sameAs` y NAP cuando existan perfiles oficiales y dirección comercial confirmados.
4. Ejecutar mensualmente las 100 consultas del benchmark y registrar 300 observaciones reales.
5. Mantener los experimentos P3 por ciclos; no son un bloqueo para publicar.
