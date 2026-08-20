# Atribución de asistentes de IA en GTM y GA4

La web empuja un evento `traffic_attribution` antes de cargar GTM. No contiene datos personales.

Campos disponibles:

- `traffic_channel`: `AI Assistants` u `Other`.
- `ai_source`: ChatGPT, Perplexity, Gemini, Microsoft Copilot o Claude.
- `landing_page_path`: primera ruta visitada.
- `referring_domain`: dominio de referencia cuando el navegador lo entrega.
- `campaign_source`: valor de `utm_source`.

El evento `generate_lead` incorpora los mismos campos guardados durante la sesión.

## Estado de configuración (11 de agosto de 2026)

- Contenedor GTM `GTM-NHXGQF97`, versión 5, publicado.
- Eventos GA4 `traffic_attribution` y `generate_lead` configurados con sus activadores y variables de capa de datos.
- Cinco dimensiones de evento creadas en GA4: canal, fuente IA, página de entrada, dominio referente y fuente de campaña.
- Pendiente únicamente desplegar la versión actual de la aplicación, verificar el evento en producción y marcar `generate_lead` como evento clave cuando GA4 lo haya recibido por primera vez.

## Configuración aplicada en GTM

1. Crear variables de capa de datos para los cinco campos.
2. Crear un evento GA4 para `traffic_attribution` con activador del mismo nombre.
3. Añadir los cinco parámetros al evento `generate_lead` existente.
4. Registrar los cinco campos como dimensiones personalizadas en GA4.
5. Crear una comparación o audiencia con `traffic_channel` exactamente igual a `AI Assistants`.
6. Verificar en Preview/DebugView una visita con `?utm_source=chatgpt` y un lead de prueba.

Los referers pueden perderse por políticas del navegador. Para campañas o enlaces controlables se recomienda añadir `utm_source=chatgpt`, `utm_source=perplexity`, `utm_source=gemini`, `utm_source=copilot` o `utm_source=claude`.
