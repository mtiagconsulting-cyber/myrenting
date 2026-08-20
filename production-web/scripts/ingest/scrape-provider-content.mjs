import fs from "node:fs/promises";
import path from "node:path";
import * as cheerio from "cheerio";

const OUTPUT = path.resolve("outputs/provider-content.json");
const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36";
const clean = (value = "") => value.replace(/\s+/g, " ").trim();

async function get(url) {
  const response = await fetch(url, {
    headers: { "user-agent": USER_AGENT, "accept-language": "es-ES,es;q=0.9" },
    signal: AbortSignal.timeout(30_000),
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${url}`);
  return cheerio.load(await response.text());
}

async function mRentingContent() {
  const faqUrl = "https://m-renting.com/content/preguntas-frecuentes";
  const $ = await get(faqUrl);
  const faqs = $(".elementor-accordion-item")
    .map((_, item) => ({
      question: clean($(item).find(".elementor-accordion-title").text()),
      source_answer: clean($(item).find(".elementor-accordion-content").text()),
    }))
    .get()
    .filter((item) => item.question && item.source_answer);
  return {
    provider: "M-Automoción / M-Renting",
    faq_source_url: faqUrl,
    faqs,
    coverage_note: "Las coberturas se extraen por oferta porque pueden variar entre vehículos y públicos.",
  };
}

async function quadisContent() {
  const offerUrl = "https://www.quadis.es/coches-renting/mg/zs/zs-hybrid-business/522422";
  const faqUrl =
    "https://www.quadis.es/preguntas-frecuentes/renting/que-es-mejor-comprar-o-hacer-renting";
  const offer = await get(offerUrl);
  const faq = await get(faqUrl);
  const bodyText = clean(offer("body").text());
  const coverageMatch = bodyText.match(/¿Qué incluye el renting\?\s*(.*?)\s*Precios válidos/i);
  const coverageText = coverageMatch?.[1] || "";
  const knownCoverage = [
    "Mantenimiento y reparaciones mecánicas",
    "Neumáticos incluidos según plazo y kilómetros contratados",
    "Seguro a todo riesgo",
    "Gestión de multas e impuestos municipales incluidos",
    "Asistencia en carretera 24 / 365",
    "Sin entrada",
  ].filter((item) => coverageText.toLowerCase().includes(item.toLowerCase()));
  const faqBlock = faq(".more-faqs-dropdown-content-title").first().parent();
  return {
    provider: "Quadis Empresas",
    coverage_source_url: offerUrl,
    coverage: knownCoverage,
    coverage_note: "Cobertura general mostrada en una ficha pública; validar excepciones en cada oferta.",
    faq_source_url: faqUrl,
    faqs: [
      {
        question: clean(faqBlock.find(".more-faqs-dropdown-content-title").first().text()),
        source_answer: clean(faqBlock.children("span").first().text()),
      },
    ].filter((item) => item.question && item.source_answer),
  };
}

const providers = [await mRentingContent(), await quadisContent()];
await fs.mkdir(path.dirname(OUTPUT), { recursive: true });
await fs.writeFile(
  OUTPUT,
  `${JSON.stringify(
    {
      generated_at: new Date().toISOString(),
      image_policy: "No se descargan ni almacenan imágenes o URLs de imágenes",
      publication_policy: "Reescribir y resumir antes de publicar; conservar atribución y enlace a la fuente",
      providers,
    },
    null,
    2,
  )}\n`,
);
console.log(`Contenido de ${providers.length} proveedores guardado en ${OUTPUT}`);
