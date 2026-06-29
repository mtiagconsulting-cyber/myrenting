#!/usr/bin/env python3
"""
generar_blog_estatico.py
Genera 5 artículos de blog estáticos para myrenting.es.
Sin API, sin dependencias externas. Solo Python estándar.

Uso:
    python3 generar_blog_estatico.py

Resultado:
    blog/index.html     → listado del blog
    blog/<slug>.html    → 5 artículos individuales
    sitemap.xml         → actualizado con URLs del blog
"""

import re, json
from pathlib import Path
from datetime import date

# ── Configuración ──────────────────────────────────────────────────────────────
BASE     = Path("/Users/matthiasthomassen/Documents/Myrenting")
BLOG_DIR = BASE / "blog"
BLOG_DIR.mkdir(exist_ok=True)
BASE_URL = "https://www.myrenting.es"

_meses = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
          "May":"mayo","June":"junio","July":"julio","August":"agosto",
          "September":"septiembre","October":"octubre","November":"noviembre","December":"diciembre"}
HOY = date.today().strftime("%d de %B de %Y")
for _en, _es in _meses.items():
    HOY = HOY.replace(_en, _es)

# ── CSS compartido ─────────────────────────────────────────────────────────────
CSS_BASE = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--accent:#F04E00;--ink:#111110;--ink-2:#1C1C1A;--ink-3:#6F6F6B;--ink-4:#9F9F9B;
          --green:#00c47a;--green-lt:#e0faf1;--surface:#fff;--surface-2:#f7f8fa;
          --surface-3:#eeeff4;--border:#e4e4ec;--radius:14px;--radius-sm:8px}
    body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--surface-2);
         color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased}
    nav{background:rgba(255,255,255,.95);backdrop-filter:blur(16px);
        border-bottom:1px solid var(--border);position:sticky;top:0;z-index:200}
    .nav-inner{max-width:1280px;margin:0 auto;padding:0 28px;height:62px;
               display:flex;align-items:center;justify-content:space-between}
    .logo{font-size:1.25rem;font-weight:800;color:var(--ink);text-decoration:none}
    .logo-dot{width:8px;height:8px;background:var(--accent);border-radius:50%;
              display:inline-block;margin-left:3px;margin-bottom:10px}
    .nav-back{color:var(--ink-3);text-decoration:none;font-size:.875rem;font-weight:500}
    .nav-back:hover{color:var(--ink)}
    footer{background:#F7F7F5;border-top:1px solid #E8E8E5;color:#6F6F6B;padding:32px 28px;text-align:center;font-size:.8rem}
    footer a{color:#6F6F6B;text-decoration:none;margin:0 6px}
    footer a:hover{color:#111110}
    footer p+p{margin-top:8px}
"""

# ── 5 artículos con contenido completo ────────────────────────────────────────
ARTICULOS = [

# ── 1 ──────────────────────────────────────────────────────────────────────────
{
"slug":        "renting-vs-compra-coche",
"titulo":      "Renting vs compra de coche: ¿cuál es mejor en 2026?",
"descripcion": "Comparativa definitiva entre renting y compra en España. Cuándo sale más barato cada opción, ventajas fiscales y cálculo real con ejemplos.",
"keywords":    "renting vs compra coche, renting o comprar coche, ventajas renting coche España",
"categoria":   "Guías",
"contenido":   """
<p>Antes de firmar nada, la pregunta que se hace todo el mundo es la misma: <strong>¿me sale mejor el renting o compro el coche directamente?</strong> La respuesta honesta es que depende de tu situación, pero hay una manera muy sencilla de calcularlo.</p>

<p>En este artículo desglosamos los números reales para que puedas tomar la decisión con los ojos abiertos, sin publicidad ni intereses de por medio.</p>

<h2>¿Qué es exactamente el renting?</h2>
<p>El renting es un alquiler a largo plazo —normalmente entre 2 y 4 años— en el que pagas una cuota mensual fija que incluye seguro a todo riesgo, mantenimiento, asistencia en carretera y gestión de la ITV. Al terminar el contrato, devuelves el coche. Sin más.</p>
<p>No es una hipoteca del coche. No es un crédito. Es literalmente pagar por usar el coche, igual que pagas por Netflix o por tu piso de alquiler.</p>

<h2>El cálculo real: renting vs compra en 3 años</h2>
<p>Tomemos un ejemplo concreto: un <strong>Seat Arona</strong> con precio de venta de 24.000€.</p>
<ul>
  <li><strong>Si lo compras:</strong> desembolso inicial de 24.000€ (o financiado con intereses). En 3 años, el coche habrá perdido aproximadamente un 35% de su valor → <strong>depreciación: ~8.400€</strong>. Suma seguro (~700€/año × 3 = 2.100€) y mantenimiento (~600€/año × 3 = 1.800€). <strong>Coste real en 3 años: ~12.300€</strong>.</li>
  <li><strong>Si haces renting:</strong> cuota media ~290€/mes × 36 meses = <strong>10.440€</strong> total. Con seguro y mantenimiento ya incluidos.</li>
</ul>
<p>En este ejemplo el renting sale <strong>~1.860€ más barato</strong> en 3 años, y además no has tenido que desembolsar nada al principio ni preocuparte de vender el coche después.</p>

<h2>Cuándo la compra gana al renting</h2>
<p>La compra suele ganar si piensas <strong>quedarte el coche más de 6-7 años</strong>. A partir de ese punto, la depreciación se ralentiza mucho y los costes fijos del renting se acumulan. También gana si tienes el dinero en efectivo (sin financiación) y el coche mantiene bien su valor residual.</p>

<h2>Cuándo el renting es claramente mejor</h2>
<ul>
  <li>Cambias de coche cada 3-4 años.</li>
  <li>Eres autónomo y puedes deducir el IVA y parte del IRPF.</li>
  <li>No quieres sorpresas: averías, cambio de neumáticos, revisiones…</li>
  <li>No tienes ahorros para la entrada o prefieres no inmovilizar capital.</li>
</ul>

<h2>La variable que más importa: tu perfil fiscal</h2>
<p>Si eres autónomo, el renting es todavía más interesante. Puedes deducirte el <strong>21% de IVA</strong> de cada cuota si el uso es profesional, y hasta el <strong>50% en IRPF</strong> si el uso es mixto. En el ejemplo anterior, el ahorro fiscal en 3 años puede superar los 2.000€.</p>

<p class="cta-inline">¿Listo para comparar precios reales? <a href="/">Ver todas las ofertas de renting en Myrenting →</a></p>
""",
},

# ── 2 ──────────────────────────────────────────────────────────────────────────
{
"slug":        "que-incluye-renting-coche",
"titulo":      "¿Qué incluye el renting de un coche? Todo lo que cubre la cuota",
"descripcion": "Desglose completo de qué cubre y qué no cubre la cuota de renting: seguro, mantenimiento, ITV, neumáticos, multas y más.",
"keywords":    "que incluye renting coche, cuota renting que cubre, renting todo incluido",
"categoria":   "Guías",
"contenido":   """
<p>Una de las dudas más frecuentes antes de contratar un renting es saber exactamente qué está pagando con esa cuota mensual. La respuesta corta es: <strong>casi todo lo que necesitas para circular</strong>. Pero hay matices importantes que conviene conocer antes de firmar.</p>

<h2>Lo que SÍ incluye la cuota de renting</h2>
<p>Aunque puede variar ligeramente entre gestoras, la cuota estándar de renting cubre:</p>
<ul>
  <li><strong>Seguro a todo riesgo</strong> sin franquicia y sin distinción de conductor. Puedes prestar el coche a alguien de tu confianza sin problema.</li>
  <li><strong>Mantenimiento preventivo</strong>: revisiones periódicas en taller oficial según las indicaciones del fabricante.</li>
  <li><strong>Mantenimiento correctivo</strong>: reparaciones por desgaste normal (frenos, embrague, filtros…).</li>
  <li><strong>Asistencia en carretera 24 horas</strong>: si el coche se avería o tienes una incidencia, llamas y te solucionan el problema.</li>
  <li><strong>Gestión de multas de tráfico</strong>: la gestora se encarga de la tramitación administrativa (tú sigues pagando la multa, pero ellos gestionan el papeleo).</li>
  <li><strong>ITV</strong>: cuando corresponde, la gestora organiza la inspección técnica.</li>
</ul>

<h2>Lo que NO incluye (y muchos se sorprenden)</h2>
<ul>
  <li><strong>Combustible</strong>: esto siempre corre por tu cuenta.</li>
  <li><strong>Peajes y aparcamiento</strong>: gastos de uso diario no incluidos.</li>
  <li><strong>Exceso de kilómetros</strong>: si superas los km anuales pactados, pagarás un penalización (~0,08-0,12€/km extra según gestora).</li>
  <li><strong>Daños por mal uso</strong>: golpes, rayadas o daños que no sean desgaste normal van a tu cuenta (el seguro todo riesgo cubre accidentes, no descuidos del conductor).</li>
</ul>

<h2>¿Los neumáticos están incluidos?</h2>
<p>Depende de la gestora y del contrato. Algunas incluyen el cambio de neumáticos por desgaste normal; otras lo cobran aparte. Es uno de los puntos que más conviene revisar antes de firmar, especialmente si haces muchos kilómetros.</p>

<h2>Diferencias entre gestoras</h2>
<p>Arval, Ayvens y Alphabet tienen coberturas muy similares en lo esencial, pero pueden diferir en detalles como: número de revisiones incluidas, cobertura de daños en llantas, o si incluyen coche de sustitución durante reparaciones. Siempre merece la pena leer las condiciones generales antes de contratar.</p>

<p class="cta-inline">¿Quieres comparar qué incluye cada gestora? <a href="/">Ver todas las ofertas de renting en Myrenting →</a></p>
""",
},

# ── 3 ──────────────────────────────────────────────────────────────────────────
{
"slug":        "renting-para-autonomos",
"titulo":      "Renting para autónomos: ventajas fiscales y cómo deducirlo",
"descripcion": "Todo lo que necesita saber un autónomo sobre el renting: deducción del IVA, IRPF, qué documentación necesitas y cómo elegir la oferta correcta.",
"keywords":    "renting autonomos, renting coche autonomo deduccion, renting fiscal autonomo España",
"categoria":   "Fiscal",
"contenido":   """
<p>Si eres autónomo, el renting de coche no es solo una comodidad — es una <strong>herramienta fiscal</strong>. Bien utilizado, puedes deducirte una parte importante de lo que pagas cada mes y reducir tu carga tributaria de forma completamente legal.</p>

<h2>¿Qué puedes deducir exactamente?</h2>
<p>Como autónomo, la deducción depende del uso que hagas del vehículo:</p>
<ul>
  <li><strong>Uso exclusivamente profesional:</strong> deduces el <strong>100% del IVA</strong> de la cuota y el <strong>100% en IRPF</strong>. Requiere poder demostrar que el coche no tiene uso particular (lo que en la práctica es difícil de justificar con un turismo).</li>
  <li><strong>Uso mixto (profesional y particular):</strong> Hacienda permite deducir el <strong>50% del IVA</strong> sin necesidad de justificación adicional para vehículos turismos. En IRPF, la deducción también se limita al 50% del gasto.</li>
  <li><strong>Vehículos de transporte o actividad específica</strong> (agentes comerciales, taxis, formadores de conducción…): deducción del 100% tanto en IVA como en IRPF.</li>
</ul>

<h2>El ahorro real con un ejemplo</h2>
<p>Supón que contratas un renting a <strong>350€/mes</strong> con uso mixto:</p>
<ul>
  <li>IVA incluido en la cuota: 350€ × 21% = 73,50€/mes</li>
  <li>Deducción del 50%: <strong>36,75€/mes → 441€/año</strong> que recuperas en la declaración trimestral.</li>
  <li>En IRPF (tipo marginal del 30%): 350€ × 50% × 30% = <strong>52,50€/mes → 630€/año</strong> de ahorro adicional.</li>
</ul>
<p>Total: más de <strong>1.000€/año</strong> de ahorro fiscal sobre una cuota de 350€/mes. El renting se convierte en una de las herramientas de optimización fiscal más accesibles para un autónomo.</p>

<h2>Documentación recomendada</h2>
<p>Para estar protegido ante una inspección de Hacienda, guarda:</p>
<ul>
  <li>Contrato de renting firmado.</li>
  <li>Facturas mensuales de la gestora (con IVA desglosado).</li>
  <li>Registro de desplazamientos profesionales (fecha, destino, motivo). No es obligatorio, pero es tu mejor defensa.</li>
</ul>

<h2>¿Renting o leasing para autónomos?</h2>
<p>El renting es operativo (gasto, fuera de balance) mientras que el leasing es financiero (activo en balance con amortización). Para la mayoría de autónomos individuales, el renting es más sencillo contablemente y fiscalmente igual de ventajoso.</p>

<p class="cta-inline">¿Buscas el renting más barato para tu actividad? <a href="/">Comparar ofertas en Myrenting →</a></p>
""",
},

# ── 4 ──────────────────────────────────────────────────────────────────────────
{
"slug":        "mejores-coches-renting-2026",
"titulo":      "Los 10 coches más baratos en renting en España (2026)",
"descripcion": "Ranking actualizado de los coches con mejor precio en renting: SUVs, berlinas y utilitarios con cuotas desde 220€/mes.",
"keywords":    "coches baratos renting España 2026, renting barato, mejor renting coche",
"categoria":   "Rankings",
"contenido":   """
<p>Si estás buscando el renting más barato sin renunciar a un coche decente, esta es tu lista. Hemos analizado las ofertas actuales de las principales gestoras en España para darte los modelos con mejor relación precio-prestaciones en 2026.</p>
<p>Todos los precios son orientativos para contratos de <strong>36 meses y 15.000 km/año para particular</strong>. El precio real varía según gestora, plazo y kilómetros.</p>

<h2>Los 10 modelos más baratos</h2>

<h3>1. Dacia Sandero — desde ~220€/mes</h3>
<p>El rey del precio en renting. Utilitario sin pretensiones pero fiable y con equipamiento suficiente para el día a día. Ideal si buscas lo más barato posible.</p>

<h3>2. Seat Ibiza — desde ~240€/mes</h3>
<p>Un escalón por encima del Sandero en acabados y tecnología, pero sigue siendo de los más económicos. Muy popular entre particulares y autónomos.</p>

<h3>3. Renault Clio — desde ~250€/mes</h3>
<p>Clásico entre los más vendidos en España. Buen equipamiento de serie, habitáculo bien resuelto y disponible en versión híbrida para ciudades con ZBE.</p>

<h3>4. Peugeot 208 — desde ~260€/mes</h3>
<p>Interior muy cuidado para su segmento, buena conectividad y disponible en versión eléctrica (e-208) con etiqueta CERO por un poco más.</p>

<h3>5. Volkswagen Polo — desde ~270€/mes</h3>
<p>Acabados y sensación de calidad por encima de la competencia en este rango de precio. Muy demandado en flotas de empresa.</p>

<h3>6. Seat Arona — desde ~290€/mes</h3>
<p>El SUV más barato de la lista. Posición de conducción elevada, maletero generoso y buena imagen para moverse por ciudad. El equilibrio perfecto.</p>

<h3>7. Volkswagen Golf — desde ~300€/mes</h3>
<p>El referente de la berlina compacta. Muy requerido en renting de empresas por su imagen profesional y alto valor residual.</p>

<h3>8. Kia Sportage — desde ~320€/mes</h3>
<p>SUV mediano con garantía de 7 años de fábrica, lo que le da un valor residual excelente y cuotas competitivas. Muy fiable según la OCU.</p>

<h3>9. Hyundai Tucson — desde ~340€/mes</h3>
<p>Disponible en versión híbrida enchufable (PHEV) con etiqueta ECO. Buen nivel de equipamiento de serie y habitáculo muy espacioso.</p>

<h3>10. Nissan Qashqai — desde ~354€/mes</h3>
<p>El SUV más demandado en renting en España. Gran red de talleres, buena disponibilidad de stock y cuotas competitivas en Ayvens y Arval.</p>

<h2>¿Cómo comparar para encontrar el precio real?</h2>
<p>Los precios cambian según gestora, plazo y kilómetros. El mismo Qashqai puede variar más de 100€/mes entre Arval y Ayvens para las mismas condiciones. Antes de llamar a nadie, compara online.</p>

<p class="cta-inline">¿Quieres ver los precios reales actualizados? <a href="/">Comparar ofertas en Myrenting →</a></p>
""",
},

# ── 5 ──────────────────────────────────────────────────────────────────────────
{
"slug":        "renting-vs-leasing",
"titulo":      "Renting vs leasing: diferencias clave y cuál te conviene",
"descripcion": "Renting y leasing no son lo mismo. Diferencias en propiedad, contabilidad, servicios incluidos y fiscalidad para empresas y autónomos.",
"keywords":    "renting vs leasing, diferencia renting leasing, leasing o renting empresa",
"categoria":   "Guías",
"contenido":   """
<p>Se usan casi como sinónimos, pero <strong>renting y leasing son productos completamente distintos</strong>. Confundirlos puede llevarte a elegir el que no se adapta a lo que necesitas. Aquí van las diferencias que importan.</p>

<h2>La diferencia fundamental: ¿quieres quedarte el coche?</h2>
<p>Esta es la pregunta clave. El <strong>renting</strong> es un alquiler puro: usas el coche durante el contrato y al terminar lo devuelves. No hay opción de compra (aunque algunas gestoras ofrecen adquirirlo por el valor de mercado si lo pides expresamente). El <strong>leasing</strong>, en cambio, es un arrendamiento financiero que siempre incluye una <strong>opción de compra al final</strong> por un valor residual pactado desde el principio.</p>

<h2>Servicios incluidos: aquí el renting gana claramente</h2>
<p>El renting incluye seguro, mantenimiento, ITV y asistencia. El leasing es un contrato financiero puro: tú eres responsable del seguro, del mantenimiento y de todo lo que le pase al coche. Si se avería, corres tú con el gasto.</p>

<h2>Contabilidad y balance</h2>
<ul>
  <li><strong>Renting:</strong> es un gasto operativo. No aparece como activo en el balance de la empresa. Ideal para pymes que quieren mantener el balance limpio.</li>
  <li><strong>Leasing:</strong> contablemente se registra como un activo (el vehículo) con su correspondiente pasivo (deuda). Aparece en el balance y se amortiza.</li>
</ul>

<h2>Fiscalidad comparada</h2>
<p>En renting, la cuota entera es gasto deducible. En leasing, solo son deducibles los intereses financieros y la amortización del activo, lo que hace el cálculo más complejo y habitualmente menos ventajoso para pymes y autónomos.</p>

<h2>¿Cuándo elegir cada uno?</h2>
<ul>
  <li>Elige <strong>renting</strong> si quieres olvidarte del coche, renovarlo cada 3-4 años y llevar la contabilidad simple.</li>
  <li>Elige <strong>leasing</strong> si tienes claro que quieres quedarte el coche al final del contrato y tienes una estructura contable que lo justifique.</li>
</ul>
<p>Para la gran mayoría de autónomos y pymes en España, el renting es la opción más práctica, más flexible y con menos sorpresas.</p>

<p class="cta-inline">¿Buscas ofertas de renting sin compromisos? <a href="/">Ver todas las ofertas en Myrenting →</a></p>
""",
},

]


# ── Función: HTML artículo individual ─────────────────────────────────────────
def html_articulo(art: dict, todos: list) -> str:
    slug      = art["slug"]
    titulo    = art["titulo"]
    desc      = art["descripcion"]
    categoria = art["categoria"]
    contenido = art["contenido"]

    related_data = json.dumps(
        [{"slug": a["slug"], "titulo": a["titulo"], "categoria": a["categoria"]}
         for a in todos],
        ensure_ascii=False
    )

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": titulo,
        "description": desc,
        "author": {"@type": "Organization", "name": "Myrenting"},
        "publisher": {"@type": "Organization", "name": "Myrenting", "url": BASE_URL},
        "datePublished": date.today().isoformat(),
        "url": f"{BASE_URL}/blog/{slug}.html"
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo} | Myrenting</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/blog/{slug}.html">
  <meta property="og:title" content="{titulo} | Myrenting">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{BASE_URL}/blog/{slug}.html">
  <meta property="og:type" content="article">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script type="application/ld+json">{schema}</script>
  <style>
    {CSS_BASE}
    .article-hero{{background:#fff;border-bottom:1.5px solid #E8E8E5;color:#111110;padding:52px 28px 44px}}
    .article-hero-inner{{max-width:780px;margin:0 auto}}
    .breadcrumb{{font-size:.78rem;color:rgba(255,255,255,.4);margin-bottom:14px}}
    .breadcrumb a{{color:rgba(255,255,255,.4);text-decoration:none}}
    .cat-pill{{display:inline-block;background:var(--accent);color:#fff;font-size:.7rem;
               font-weight:700;padding:3px 10px;border-radius:99px;margin-bottom:12px;
               text-transform:uppercase;letter-spacing:.5px}}
    .article-hero h1{{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:800;letter-spacing:-1px;
                      line-height:1.2;margin-bottom:12px}}
    .article-meta{{font-size:.82rem;color:rgba(255,255,255,.4);margin-top:10px}}
    .article-wrap{{max-width:780px;margin:48px auto;padding:0 28px}}
    .article-body{{background:var(--surface);border-radius:var(--radius);
                   border:1px solid var(--border);padding:40px;margin-bottom:32px}}
    .article-body h2{{font-size:1.2rem;font-weight:800;color:var(--ink);
                      margin:32px 0 10px;letter-spacing:-.3px}}
    .article-body h2:first-child{{margin-top:0}}
    .article-body h3{{font-size:1rem;font-weight:700;color:var(--ink);margin:20px 0 8px}}
    .article-body p{{color:var(--ink-3);margin-bottom:14px;line-height:1.8;font-size:.97rem}}
    .article-body ul,.article-body ol{{padding-left:1.4rem;margin-bottom:14px}}
    .article-body li{{color:var(--ink-3);margin-bottom:6px;line-height:1.7;font-size:.97rem}}
    .article-body strong{{color:var(--ink);font-weight:700}}
    .article-body blockquote{{border-left:3px solid var(--accent);padding:12px 16px;
                              background:var(--surface-2);border-radius:0 var(--radius-sm) var(--radius-sm) 0;
                              margin:20px 0;font-style:italic;color:var(--ink-2)}}
    .cta-inline{{background:var(--surface-2);border:1px solid var(--border);
                 border-radius:var(--radius-sm);padding:16px 20px;margin-top:24px !important}}
    .cta-inline a{{color:var(--accent);font-weight:700;text-decoration:none}}
    .cta-inline a:hover{{text-decoration:underline}}
    .related-section h2{{font-size:1rem;font-weight:800;margin-bottom:16px;letter-spacing:-.2px}}
    .related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:40px}}
    .related-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);
                   padding:16px;text-decoration:none;transition:box-shadow .2s,border-color .2s;display:block}}
    .related-card:hover{{box-shadow:0 4px 16px rgba(0,0,0,.08);border-color:var(--border-2,#d0d0dc)}}
    .related-cat{{font-size:.65rem;font-weight:700;color:var(--accent);text-transform:uppercase;
                  letter-spacing:.5px;margin-bottom:6px}}
    .related-title{{font-size:.88rem;font-weight:700;color:var(--ink);line-height:1.4}}
    @media(max-width:640px){{
      .article-hero{{padding:32px 16px 28px}}
      .article-wrap{{padding:0 16px;margin:24px auto}}
      .article-body{{padding:24px 16px}}
    }}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<nav>
  <div class="nav-inner">
    <a href="/" class="logo">Myrenting<span class="logo-dot"></span></a>
    <a href="/blog/" class="nav-back">← Blog</a>
  </div>
</nav>

<section class="article-hero">
  <div class="article-hero-inner">
    <div class="breadcrumb">
      <a href="/">Myrenting</a> › <a href="/blog/">Blog</a> › {categoria}
    </div>
    <span class="cat-pill">{categoria}</span>
    <h1>{titulo}</h1>
    <p class="article-meta">Publicado el {HOY} · myrenting.es</p>
  </div>
</section>

<div class="article-wrap">
  <article class="article-body">
    {contenido}
  </article>

  <div class="related-section">
    <h2>Otros artículos que te pueden interesar</h2>
    <div class="related-grid" id="related-grid"></div>
  </div>
</div>

<footer>
  <p>© 2026 Myrenting · mtiagconsulting · Barcelona, España</p>
  <p>
    <a href="/">Comparador</a>
    <a href="/blog/">Blog</a>
    <a href="/aviso-legal.html">Aviso Legal</a>
    <a href="/politica-privacidad.html">Privacidad</a>
    <a href="/politica-cookies.html">Cookies</a>
  </p>
</footer>

<script>
  const todos = {related_data};
  const actual = "{slug}";
  const otros = todos.filter(a => a.slug !== actual).slice(0, 3);
  const grid = document.getElementById('related-grid');
  otros.forEach(a => {{
    grid.innerHTML += `<a class="related-card" href="/blog/${{a.slug}}.html">
      <div class="related-cat">${{a.categoria}}</div>
      <div class="related-title">${{a.titulo}}</div>
    </a>`;
  }});
</script>
</body>
</html>"""


# ── Función: index del blog ────────────────────────────────────────────────────
def html_blog_index(articulos: list) -> str:
    cards = ""
    for a in articulos:
        cards += f"""
    <a class="blog-card" href="/blog/{a['slug']}.html">
      <span class="blog-cat">{a['categoria']}</span>
      <h2 class="blog-card-title">{a['titulo']}</h2>
      <p class="blog-card-desc">{a['descripcion']}</p>
      <span class="blog-read">Leer artículo →</span>
    </a>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-NHXGQF97');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog de Renting de Coches — Guías y consejos | Myrenting</title>
  <meta name="description" content="Guías, comparativas y consejos sobre renting de coches en España. Todo lo que necesitas saber antes de contratar tu renting.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/blog/">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    {CSS_BASE}
    .blog-hero{{background:#111110;color:#fff;padding:52px 28px}}
    .blog-hero-inner{{max-width:1280px;margin:0 auto}}
    .blog-hero h1{{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;letter-spacing:-1px;margin-bottom:10px}}
    .blog-hero h1 em{{font-style:normal;color:var(--accent)}}
    .blog-hero p{{color:rgba(255,255,255,.5);font-size:1rem;max-width:520px}}
    main{{max-width:1280px;margin:48px auto;padding:0 28px}}
    .blog-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px;margin-bottom:48px}}
    .blog-card{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
                padding:28px;text-decoration:none;display:flex;flex-direction:column;
                transition:box-shadow .2s,transform .2s,border-color .2s}}
    .blog-card:hover{{box-shadow:0 8px 32px rgba(0,0,0,.1);transform:translateY(-3px);border-color:var(--border-2,#d0d0dc)}}
    .blog-cat{{font-size:.68rem;font-weight:700;color:var(--accent);text-transform:uppercase;
               letter-spacing:.6px;margin-bottom:10px;display:block}}
    .blog-card-title{{font-size:1.05rem;font-weight:800;color:var(--ink);line-height:1.35;
                      margin-bottom:10px;letter-spacing:-.2px}}
    .blog-card-desc{{font-size:.875rem;color:var(--ink-3);line-height:1.6;flex:1;margin-bottom:16px}}
    .blog-read{{font-size:.82rem;font-weight:700;color:var(--accent)}}
    .cta-banner{{background:var(--accent);color:#fff;border-radius:var(--radius);
                 padding:40px;text-align:center;margin-bottom:40px}}
    .cta-banner h2{{font-size:1.3rem;font-weight:800;margin-bottom:8px}}
    .cta-banner p{{color:rgba(255,255,255,.7);margin-bottom:20px}}
    .btn-cta{{background:#fff;color:var(--accent);text-decoration:none;padding:13px 28px;
              border-radius:var(--radius-sm);font-size:.95rem;font-weight:800;display:inline-block}}
    .btn-cta:hover{{background:rgba(255,255,255,.9)}}
    @media(max-width:640px){{
      .blog-hero{{padding:36px 16px}}
      main{{padding:0 16px;margin:28px auto}}
      .blog-grid{{grid-template-columns:1fr}}
    }}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-NHXGQF97" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<nav>
  <div class="nav-inner">
    <a href="/" class="logo">Myrenting<span class="logo-dot"></span></a>
    <a href="/" class="nav-back">← Comparador</a>
  </div>
</nav>

<section class="blog-hero">
  <div class="blog-hero-inner">
    <h1>Blog sobre <em>renting de coches</em></h1>
    <p>Guías, comparativas y consejos para que contrates el renting que más te conviene.</p>
  </div>
</section>

<main>
  <div class="blog-grid">
    {cards}
  </div>
  <div class="cta-banner">
    <h2>¿Ya tienes claro lo que buscas?</h2>
    <p>Compara más de 900 ofertas de renting sin registrarte ni rellenar formularios.</p>
    <a href="/" class="btn-cta">Ver ofertas de renting →</a>
  </div>
</main>

<footer>
  <p>© 2026 Myrenting · mtiagconsulting · Barcelona, España</p>
  <p>
    <a href="/">Comparador</a>
    <a href="/blog/">Blog</a>
    <a href="/aviso-legal.html">Aviso Legal</a>
    <a href="/politica-privacidad.html">Privacidad</a>
    <a href="/politica-cookies.html">Cookies</a>
  </p>
</footer>
</body>
</html>"""


# ── Actualizar sitemap ─────────────────────────────────────────────────────────
def actualizar_sitemap(slugs: list):
    sitemap_path = BASE / "sitemap.xml"
    if not sitemap_path.exists():
        print("⚠️  sitemap.xml no encontrado — ejecuta primero generar_seo.py")
        return
    sitemap = sitemap_path.read_text(encoding="utf-8")
    # Eliminar entradas de blog anteriores
    sitemap = re.sub(r'\s*<url><loc>[^<]*/blog/[^<]*</loc>[^<]*</url>', '', sitemap)
    nuevas  = f'  <url><loc>{BASE_URL}/blog/</loc><priority>0.9</priority></url>\n'
    for s in slugs:
        nuevas += f'  <url><loc>{BASE_URL}/blog/{s}.html</loc><priority>0.7</priority></url>\n'
    sitemap = sitemap.replace('</urlset>', nuevas + '</urlset>')
    sitemap_path.write_text(sitemap, encoding="utf-8")
    print(f"✓ sitemap.xml actualizado (+{len(slugs)+1} URLs de blog)")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Myrenting · Generador de Blog estático")
    print("=" * 55)
    print(f"  Artículos: {len(ARTICULOS)}")
    print(f"  Destino:   {BLOG_DIR}")
    print("=" * 55)

    for i, art in enumerate(ARTICULOS, 1):
        html = html_articulo(art, ARTICULOS)
        path = BLOG_DIR / f"{art['slug']}.html"
        path.write_text(html, encoding="utf-8")
        print(f"  [{i}/{len(ARTICULOS)}] {art['slug']}.html ✓")

    index = html_blog_index(ARTICULOS)
    (BLOG_DIR / "index.html").write_text(index, encoding="utf-8")
    print(f"  blog/index.html ✓")

    actualizar_sitemap([a["slug"] for a in ARTICULOS])

    print("\n" + "=" * 55)
    print(f"  ✅ {len(ARTICULOS) + 1} archivos generados en blog/")
    print("=" * 55)
    print("\nPara publicar:")
    print("  git add blog/ sitemap.xml")
    print('  git commit -m "feat: blog con 5 artículos SEO"')
    print("  git push origin main")


if __name__ == "__main__":
    main()
