// Cloudflare Pages Function (middleware).
// Bloquea la ficha del Kia Niro para visitantes del área de Barcelona (Barcelonès).
// El resto de España y el extranjero la ven con normalidad.
//
// Nota: la geolocalización por IP no es 100% precisa (VPN, IP de operador móvil).
// Cloudflare expone país siempre; ciudad/región según plan. Ajustable abajo.

const PROTEGIDAS = ["/renting-kia-niro.html", "/renting-kia-niro"];

// Municipios del Barcelonès (+ Barcelona ciudad) para el bloqueo.
const CIUDADES_BLOQUEADAS = [
  "barcelona", "l'hospitalet de llobregat", "hospitalet de llobregat", "hospitalet",
  "badalona", "santa coloma de gramenet", "sant adria de besos", "sant adrià de besòs"
];

function bloqueado(cf) {
  const city = (cf && cf.city ? cf.city : "").toLowerCase();
  // Coincidencia por ciudad (Barcelonès). Para ampliar a toda Cataluña,
  // descomenta la línea de región de abajo.
  if (CIUDADES_BLOQUEADAS.some(c => city.includes(c))) return true;
  // const region = (cf && cf.region ? cf.region : "").toLowerCase();
  // if (region.includes("catal")) return true;
  return false;
}

const HTML_BLOQUEO = `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Oferta no disponible en tu zona | MyRenting</title>
<style>body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f6f3ee;color:#1c2233;display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center;padding:24px}
.box{max-width:520px}.ic{width:64px;height:64px;border-radius:16px;background:#e8380d;color:#fff;font-weight:900;font-size:30px;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}
h1{font-size:26px;font-weight:850;letter-spacing:-.5px;margin:0 0 10px}p{color:#5a6072;font-size:16px;line-height:1.6;margin:0 0 22px}
a{display:inline-block;background:#e8380d;color:#fff;text-decoration:none;padding:13px 26px;border-radius:99px;font-weight:700}</style>
</head><body><div class="box"><div class="ic">M</div>
<h1>Esta oferta no está disponible en tu zona</h1>
<p>Esta promoción del Kia Niro no está disponible actualmente en el área de Barcelona. Puedes ver el resto de nuestras ofertas de renting con entrega en toda España.</p>
<a href="/">Ver todas las ofertas &rarr;</a></div></body></html>`;

export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);
  if (PROTEGIDAS.includes(url.pathname)) {
    if (bloqueado(request.cf || {})) {
      return new Response(HTML_BLOQUEO, {
        status: 200,
        headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" }
      });
    }
  }
  return next();
}
