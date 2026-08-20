# Auditoría SEO/GEO base de MyRenting

Fecha de auditoría: 11 de agosto de 2026.

## Alcance comprobado

- Código Next.js, generación estática y adaptación OpenNext/Cloudflare.
- Producción: inicio, catálogo, ficha, marca, categoría y respuesta editorial.
- `robots.txt`, `sitemap.xml`, `llms.txt`, metadata, canonicals y JSON-LD.
- Inventario bruto: 205 vehículos y 3.707 combinaciones. Catálogo público canonicalizado: 202 vehículos y 3.662 combinaciones únicas.
- Rendimiento de la portada mediante traza en Chrome sin limitación artificial.

## Resultado ejecutivo

La web es accesible, renderiza el contenido principal en HTML, utiliza canonicals absolutos y sirve las rutas públicas analizadas con contenido indexable. La portada obtiene LCP 288 ms, CLS 0 y TTFB 92 ms en la traza de laboratorio; rendimiento no es ahora el cuello de botella.

Los riesgos principales están en precisión y mantenimiento: cantidades antiguas escritas manualmente, propiedades técnicas nulas en JSON-LD, fechas globales que podían cambiar en cada build y diferencias de slug entre `llms.txt` y las URLs canónicas. Las correcciones de código correspondientes se incluyen en esta entrega.

## Evidencias principales

| Área | Evidencia | Diagnóstico | Prioridad |
|---|---|---|---|
| Renderizado | H1, texto comercial y enlaces están presentes en el DOM inicial | Correcto para crawlers | P0 superado |
| Canonicals | Inicio, fichas, marcas, categorías y respuestas publican canonical propio | Correcto en la muestra | P0 superado |
| Robots | Rutas públicas permitidas; `/api/`, `/gestion/` y `/opinar` bloqueadas | Correcto | P0 superado |
| Sitemap | XML publicado y válido; 317 URLs en la última verificación | Correcto tras la reparación previa | P0 superado |
| Rendimiento | LCP 288 ms, CLS 0, TTFB 92 ms | Excelente; no priorizar microoptimizaciones | P3 |
| CSS | Un CSS bloqueante; ahorro estimado 43 ms | Impacto despreciable actualmente | P3 |
| GTM | 126 ms de CPU de terceros; sin ahorro estimado | Mantener y vigilar | P2 |
| Inventario | 205/3.707 registros brutos; 202/3.662 registros públicos únicos | Fuente real canonicalizada | P0 |
| Metadata | Inicio decía 206 vehículos; informe decía 206/1.531 | Datos públicos inconsistentes | P0 corregido |
| Vehicle Schema | `cargoVolume.value` podía ser `null`; potencia podía ser 0 | JSON-LD de baja calidad | P0 corregido |
| Precio “desde” | Metadata tomaba la primera oferta, no la menor | Posible discrepancia con la ficha | P0 corregido |
| `llms.txt` | Marcas usaban `toLowerCase()` en vez del slug canónico | Enlaces rotos para marcas especiales | P0 corregido |
| Sitemap freshness | Todas las URLs recibían la fecha de cada build | Señal de actualización artificial | P1 corregido |
| Datos técnicos | Los 205 vehículos carecen de al menos consumo o maletero | No inventar; completar desde fuentes | P1 |
| Autoridad | Organización sin perfiles externos verificables en `sameAs` | Añadir solo tras verificar perfiles | P2 |
| Medición IA | Hay `generate_lead`, pero no cuadro específico por asistente | Falta atribución y Share of Voice | P2 |

## Segunda pasada P0

- No existen ofertas huérfanas, IDs repetidos ni combinaciones duplicadas por vehículo, perfil, plazo y kilometraje.
- El contenido de email y WhatsApp se genera desde una única fuente y se comprueba automáticamente.
- El evento `generate_lead` de email se registra después del éxito de FormSubmit, nunca antes.
- WhatsApp se registra al abrir el canal, ya que el navegador no puede confirmar el envío final dentro de WhatsApp.
- El formulario incorpora un honeypot real y descarta silenciosamente envíos automatizados básicos.
- Producción responde 200 para portada, robots, sitemap y `llms.txt`; los MIME son correctos.
- Sitemap y `llms.txt` usan caché de una hora; los recursos versionados de Next.js usan caché inmutable de un año. Las cabeceras se verificaron en producción.

## Search Console — 11 de agosto de 2026

- Todas las páginas conocidas: 1.948 indexadas y 606 excluidas, incluyendo un volumen importante de URLs históricas.
- Filtrando solo `https://myrenting.es/sitemap.xml`: 286 indexadas y 31 pendientes sobre 317 URLs publicadas en ese momento.
- Pendientes del sitemap: 27 descubiertas, 3 rastreadas sin indexar y 1 canonical distinta.
- No existen 404, `noindex` ni páginas alternativas dentro del sitemap actual.
- La canonical distinta era `/coches/m-empresa-426`, duplicado exacto de `/coches/m-empresa-387`.
- Se encontraron tres duplicados exactos del JAECOO 5, uno por perfil; se han retirado del catálogo y recibirán redirección permanente.
- El nuevo sitemap contiene 314 URLs únicas.
- Inicio, ficha, marca, categoría, respuesta, comparación y blog constan como indexados.
- El informe `/informes/renting-espana-2026` está disponible para Google y su indexación se solicitó el 11 de agosto de 2026.

## Schema P1

- Cada ficha relaciona una `WebPage`, un `Vehicle`, un `Product`, un `Offer`, el `WebSite` y la `Organization` mediante identificadores estables.
- La cifra publicada se declara como cuota mensual mediante `UnitPriceSpecification`, no como un precio de compra aislado.
- El Schema expone tipo de cliente, duración, kilómetros anuales, entrada y tratamiento del IVA.
- La disponibilidad diferencia `InStock`, `PreOrder` y `LimitedAvailability`.
- La auditoría del build exige esas condiciones en todas las fichas y falla si alguna vuelve a perderlas.

## Criterios de aceptación globales

1. Ninguna cifra pública se escribe manualmente si puede derivarse del inventario.
2. Ningún dato desconocido aparece como cero, `null`, “no incluido” o afirmación negativa.
3. Cada URL indexable responde 200, tiene canonical propio, un H1 y contenido útil en HTML.
4. El Schema debe coincidir con el contenido visible y validar sin propiedades vacías.
5. Las fechas reflejan una revisión real, no simplemente la fecha del despliegue.
6. Cada oferta mantiene perfil, IVA, plazo, kilómetros, entrada y fuente trazables.
7. Las acciones GEO se evalúan con citas y leads, no solo con rankings.
