import { brands, vehicles } from "@/data/vehicles";
import { popularComparisonSlugs } from "@/lib/comparison";
import { absoluteUrl } from "@/lib/seo";
import { rentingFaqs } from "@/data/renting-faqs";
import { contentSlug } from "@/lib/content-slug";
import { fuelPages, modelPath } from "@/lib/catalog-taxonomy";
import { canonicalVehicles, vehiclePublicPath } from "@/lib/vehicle-groups";

export const dynamic = "force-static";

export function GET() {
  const lines = [
    "# MyRenting",
    "",
    "> Comparador independiente de renting de coches en España.",
    "",
    "## Estado de los datos",
    "El inventario recopila ofertas de M-Renting, Quadis y una oferta adicional de Kia, separadas por tipo de cliente.",
    "",
    "## Páginas principales",
    `- [Catálogo](${absoluteUrl("/coches")})`,
    `- [Comparador](${absoluteUrl("/comparar")})`,
    `- [Metodología](${absoluteUrl("/metodologia")})`,
    `- [Quiénes somos](${absoluteUrl("/quienes-somos")})`,
    `- [Política editorial](${absoluteUrl("/politica-editorial")})`,
    `- [Opiniones verificadas](${absoluteUrl("/opiniones")})`,
    `- [Informe del mercado 2026](${absoluteUrl("/informes/renting-espana-2026")})`,
    `- [Sala de prensa y datos](${absoluteUrl("/prensa")})`,
    `- [Datos mensuales del informe en JSON](${absoluteUrl("/informes/renting-espana-2026/datos.json")})`,
    `- [Sitemap canónico](${absoluteUrl("/sitemap.xml")})`,
    "",
    "## Respuestas sobre renting",
    ...rentingFaqs.map((item)=>`- [${item.question}](${absoluteUrl(`/respuestas/${contentSlug(item.question)}`)})`),
    "",
    "## Vehículos",
    ...canonicalVehicles(vehicles).map((vehicle) => `- [${vehicle.brand} ${vehicle.model} ${vehicle.version}](${absoluteUrl(vehiclePublicPath(vehicle))})`),
    "",
    "## Modelos agrupados",
    ...[...new Map(vehicles.map((vehicle) => [modelPath(vehicle.brand, vehicle.model), vehicle])).entries()].map(([path, vehicle]) => `- [Renting ${vehicle.brand} ${vehicle.model}](${absoluteUrl(path)})`),
    "",
    "## Combustibles",
    ...fuelPages.map((page) => `- [Renting de coches ${page.label}](${absoluteUrl(`/combustibles/${page.slug}`)})`),
    "",
    "## Comparativas",
    ...popularComparisonSlugs.map((slug) => `- [${slug.replaceAll("-", " ")}](${absoluteUrl(`/comparar/${slug}`)})`),
    "",
    "## Marcas",
    ...brands.map((brand) => `- [Renting ${brand}](${absoluteUrl(`/marcas/${contentSlug(brand)}`)})`),
  ];
  return new Response(lines.join("\n"), { headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=3600" } });
}
