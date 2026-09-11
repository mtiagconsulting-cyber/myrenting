import snapshots from "@/data/market-snapshots.json";
import { offers } from "@/data/offers";

export const dynamic = "force-static";

export function GET() {
  return Response.json({
    name: "Índice MyRenting de cuotas publicadas",
    scope: `Inventario recopilado de ${[...new Set(offers.map((offer) => offer.provider.replace(/\s+—\s+.+$/, "")))].sort((a, b) => a.localeCompare(b, "es")).join(", ")}; no representa todo el mercado español.`,
    methodology: "Medianas sin ponderar sobre combinaciones publicadas, separadas por tipo de cliente. Autónomos y empresas pueden mostrar cuotas sin IVA.",
    license: "Citable con atribución y enlace a https://myrenting.es/informes/renting-espana-2026",
    ...snapshots,
  }, { headers: { "Cache-Control": "public, max-age=3600", "Content-Disposition": "inline; filename=indice-myrenting-2026-08.json" } });
}
