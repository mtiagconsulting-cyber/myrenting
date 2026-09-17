import { NextResponse } from "next/server";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { validCrmSession } from "@/lib/crm-auth";
import { cleanCrmText } from "@/lib/crm";
import { reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";
type Context = { params: Promise<{ id: string }> };

export async function POST(request: Request, context: Context) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { id } = await context.params;
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const offerId = cleanCrmText(body.offerId, 220);
  const offer = offers.find((item) => item.id === offerId);
  const vehicle = offer ? vehicles.find((item) => item.id === offer.vehicleId) : null;
  if (!offer || !vehicle) return NextResponse.json({ error: "Oferta no encontrada en el inventario actual" }, { status: 400 });
  const { REVIEWS_DB } = reviewEnv();
  const lead = await REVIEWS_DB.prepare("SELECT id FROM leads WHERE id = ?").bind(id).first();
  if (!lead) return NextResponse.json({ error: "Lead no encontrado" }, { status: 404 });
  const existing = await REVIEWS_DB.prepare("SELECT id FROM lead_proposals WHERE lead_id = ? AND offer_id = ?").bind(id, offer.id).first();
  if (existing) return NextResponse.json({ ok: true, duplicate: true });
  await REVIEWS_DB.batch([
    REVIEWS_DB.prepare("INSERT OR IGNORE INTO lead_proposals (lead_id, offer_id, vehicle_id) VALUES (?, ?, ?)").bind(id, offer.id, vehicle.id),
    REVIEWS_DB.prepare("INSERT INTO lead_activities (lead_id, activity_type, description, metadata) VALUES (?, 'proposal_added', ?, ?)").bind(id, `${vehicle.brand} ${vehicle.model} añadido como alternativa`, JSON.stringify({ offerId: offer.id, vehicleId: vehicle.id })),
    REVIEWS_DB.prepare("UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(id),
  ]);
  return NextResponse.json({ ok: true });
}

export async function DELETE(request: Request, context: Context) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { id } = await context.params;
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const offerId = cleanCrmText(body.offerId, 220);
  if (!offerId) return NextResponse.json({ error: "Oferta no válida" }, { status: 400 });
  const { REVIEWS_DB } = reviewEnv();
  await REVIEWS_DB.batch([
    REVIEWS_DB.prepare("DELETE FROM lead_proposals WHERE lead_id = ? AND offer_id = ?").bind(id, offerId),
    REVIEWS_DB.prepare("INSERT INTO lead_activities (lead_id, activity_type, description, metadata) VALUES (?, 'proposal_removed', 'Alternativa eliminada', ?)").bind(id, JSON.stringify({ offerId })),
    REVIEWS_DB.prepare("UPDATE leads SET updated_at = CURRENT_TIMESTAMP, chosen_offer_id = CASE WHEN chosen_offer_id = ? THEN NULL ELSE chosen_offer_id END WHERE id = ?").bind(offerId, id),
  ]);
  return NextResponse.json({ ok: true });
}
