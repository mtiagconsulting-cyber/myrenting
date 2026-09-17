import { NextResponse } from "next/server";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { validCrmSession } from "@/lib/crm-auth";

export const runtime = "nodejs";

export async function GET(request: Request) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const vehicleById = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
  const catalogue = offers.map((offer) => {
    const vehicle = vehicleById.get(offer.vehicleId);
    return vehicle ? { offerId: offer.id, vehicleId: vehicle.id, name: `${vehicle.brand} ${vehicle.model} ${vehicle.version}`, provider: offer.provider, audience: offer.audience, duration: offer.duration, kilometers: offer.kilometers, monthlyPrice: offer.monthlyPrice, priceIncludesVat: offer.priceIncludesVat } : null;
  }).filter(Boolean);
  return NextResponse.json({ catalogue }, { headers: { "Cache-Control": "private, max-age=300" } });
}
