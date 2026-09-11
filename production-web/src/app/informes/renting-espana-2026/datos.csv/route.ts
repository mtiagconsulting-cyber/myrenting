import { inventoryUpdatedAt, offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { offerPriceExVat, offerPriceIncVat } from "@/lib/offer-pricing";

export const dynamic = "force-static";

function csv(value: string | number) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

export function GET() {
  const vehicleById = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
  const header = ["fecha_actualizacion", "marca", "modelo", "version", "combustible", "potencia_cv", "cambio", "proveedor", "perfil", "precio_sin_iva", "precio_con_iva", "duracion_meses", "km_ano", "entrada", "disponibilidad"];
  const rows = offers.flatMap((offer) => {
    const vehicle = vehicleById.get(offer.vehicleId);
    if (!vehicle) return [];
    return [[inventoryUpdatedAt, vehicle.brand, vehicle.model, vehicle.version, vehicle.fuel, vehicle.power > 0 ? vehicle.power : "", vehicle.transmission ?? "", offer.provider, offer.audience, offerPriceExVat(offer).toFixed(2), offerPriceIncVat(offer).toFixed(2), offer.duration, offer.kilometers, offer.initialPayment, offer.availability]];
  });
  const body = [header, ...rows].map((row) => row.map(csv).join(",")).join("\n");
  return new Response(body, { headers: { "Content-Type": "text/csv; charset=utf-8", "Cache-Control": "public, max-age=3600", "Content-Disposition": "attachment; filename=indice-myrenting-ofertas.csv" } });
}
