import { NextResponse } from "next/server";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { validCrmSession } from "@/lib/crm-auth";
import { reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { REVIEWS_DB } = reviewEnv();
  const result = await REVIEWS_DB.prepare(`
    SELECT id, created_at, updated_at, first_name, last_name, phone, email, city,
      customer_type, vehicle_name, offer_id, provider, channel, status,
      last_contact_at, next_action, next_action_at, expected_commission,
      final_commission, lost_reason, lead_type, chosen_offer_id
    FROM leads
    ORDER BY CASE WHEN next_action_at IS NULL THEN 1 ELSE 0 END, next_action_at ASC, created_at DESC
    LIMIT 500
  `).all();
  const offerById = new Map(offers.map((offer) => [offer.id, offer]));
  const vehicleById = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
  const leads = (result.results ?? []).map((lead) => {
    const chosenOfferId = typeof lead.chosen_offer_id === "string" ? lead.chosen_offer_id : "";
    const chosenOffer = offerById.get(chosenOfferId);
    const chosenVehicle = chosenOffer ? vehicleById.get(chosenOffer.vehicleId) : null;
    return {
      ...lead,
      chosen_vehicle_name: chosenVehicle ? `${chosenVehicle.brand} ${chosenVehicle.model}` : null,
    };
  });
  return NextResponse.json({ leads }, { headers: { "Cache-Control": "private, no-store" } });
}
