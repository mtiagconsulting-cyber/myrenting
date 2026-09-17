import { NextResponse } from "next/server";
import { validCrmSession } from "@/lib/crm-auth";
import { cleanCrmText, CRM_STATUSES, isCrmStatus, LOST_REASONS, NEXT_ACTIONS } from "@/lib/crm";
import { offers } from "@/data/offers";
import { vehicles } from "@/data/vehicles";
import { reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Context = { params: Promise<{ id: string }> };
type LeadRow = Record<string, unknown> & { id: string; status: string; next_action?: string | null; next_action_at?: string | null; last_contact_at?: string | null; notes?: string | null; expected_commission?: number | null; final_commission?: number | null; lost_reason?: string | null; lost_reason_other?: string | null; chosen_offer_id?: string | null };

function nullableDate(value: unknown) {
  const cleaned = cleanCrmText(value, 40);
  if (!cleaned) return null;
  const parsed = new Date(cleaned);
  return Number.isNaN(parsed.getTime()) ? undefined : parsed.toISOString();
}

async function detail(id: string) {
  const { REVIEWS_DB } = reviewEnv();
  const lead = await REVIEWS_DB.prepare("SELECT * FROM leads WHERE id = ?").bind(id).first<LeadRow>();
  if (!lead) return null;
  const [activitiesResult, proposalsResult] = await Promise.all([
    REVIEWS_DB.prepare("SELECT id, activity_type, description, metadata, actor, created_at FROM lead_activities WHERE lead_id = ? ORDER BY created_at DESC, id DESC LIMIT 300").bind(id).all(),
    REVIEWS_DB.prepare("SELECT id, offer_id, vehicle_id, created_at FROM lead_proposals WHERE lead_id = ? ORDER BY created_at DESC, id DESC").bind(id).all<{ id: number; offer_id: string; vehicle_id: string; created_at: string }>(),
  ]);
  const offerById = new Map(offers.map((offer) => [offer.id, offer]));
  const vehicleById = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));
  const proposals = (proposalsResult.results ?? []).map((proposal) => {
    const offer = offerById.get(proposal.offer_id);
    const vehicle = vehicleById.get(proposal.vehicle_id);
    return { ...proposal, offer: offer ?? null, vehicle: vehicle ? { id: vehicle.id, brand: vehicle.brand, model: vehicle.model, version: vehicle.version, slug: vehicle.slug } : null };
  });
  return { lead, activities: activitiesResult.results ?? [], proposals };
}

export async function GET(request: Request, context: Context) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { id } = await context.params;
  const data = await detail(id);
  return data ? NextResponse.json(data, { headers: { "Cache-Control": "private, no-store" } }) : NextResponse.json({ error: "Lead no encontrado" }, { status: 404 });
}

export async function PATCH(request: Request, context: Context) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { id } = await context.params;
  const { REVIEWS_DB } = reviewEnv();
  const current = await REVIEWS_DB.prepare("SELECT * FROM leads WHERE id = ?").bind(id).first<LeadRow>();
  if (!current) return NextResponse.json({ error: "Lead no encontrado" }, { status: 404 });
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const status = body.status === undefined ? current.status : String(body.status);
  if (!isCrmStatus(status)) return NextResponse.json({ error: `Estado no válido. Usa: ${CRM_STATUSES.join(", ")}` }, { status: 400 });
  const nextAction = body.nextAction === undefined ? current.next_action ?? null : cleanCrmText(body.nextAction, 80) || null;
  if (nextAction && !NEXT_ACTIONS.includes(nextAction as (typeof NEXT_ACTIONS)[number])) return NextResponse.json({ error: "Próxima acción no válida" }, { status: 400 });
  const nextActionAt = body.nextActionAt === undefined ? current.next_action_at ?? null : nullableDate(body.nextActionAt);
  const lastContactAt = body.lastContactAt === undefined ? current.last_contact_at ?? null : nullableDate(body.lastContactAt);
  if (nextActionAt === undefined || lastContactAt === undefined) return NextResponse.json({ error: "Fecha no válida" }, { status: 400 });
  const lostReason = body.lostReason === undefined ? current.lost_reason ?? null : cleanCrmText(body.lostReason, 100) || null;
  const lostReasonOther = body.lostReasonOther === undefined ? current.lost_reason_other ?? null : cleanCrmText(body.lostReasonOther, 500) || null;
  if (status === "PERDIDO" && (!lostReason || !LOST_REASONS.includes(lostReason as (typeof LOST_REASONS)[number]) || (lostReason === "Otro" && !lostReasonOther))) return NextResponse.json({ error: "Selecciona un motivo de pérdida válido" }, { status: 400 });
  const numberOrNull = (value: unknown, fallback: number | null | undefined) => value === undefined ? fallback ?? null : value === null || value === "" ? null : Number(value);
  const expectedCommission = numberOrNull(body.expectedCommission, current.expected_commission);
  const finalCommission = numberOrNull(body.finalCommission, current.final_commission);
  if ((expectedCommission !== null && (!Number.isFinite(expectedCommission) || expectedCommission < 0)) || (finalCommission !== null && (!Number.isFinite(finalCommission) || finalCommission < 0))) return NextResponse.json({ error: "La comisión debe ser un importe válido" }, { status: 400 });
  const notes = body.notes === undefined ? current.notes ?? null : cleanCrmText(body.notes, 5000) || null;
  const chosenOfferId = body.chosenOfferId === undefined ? current.chosen_offer_id ?? null : cleanCrmText(body.chosenOfferId, 220) || null;
  if (chosenOfferId) {
    const proposed = await REVIEWS_DB.prepare("SELECT id FROM lead_proposals WHERE lead_id = ? AND offer_id = ?").bind(id, chosenOfferId).first();
    if (!proposed) return NextResponse.json({ error: "La oferta elegida debe estar entre las alternativas propuestas" }, { status: 400 });
  }

  const statements = [REVIEWS_DB.prepare(`UPDATE leads SET status = ?, last_contact_at = ?, next_action = ?, next_action_at = ?, expected_commission = ?, final_commission = ?, notes = ?, lost_reason = ?, lost_reason_other = ?, chosen_offer_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`).bind(status, lastContactAt, nextAction, nextActionAt, expectedCommission, finalCommission, notes, status === "PERDIDO" ? lostReason : null, status === "PERDIDO" ? lostReasonOther : null, chosenOfferId, id)];
  const activity = (type: string, description: string, metadata?: Record<string, unknown>) => statements.push(REVIEWS_DB.prepare("INSERT INTO lead_activities (lead_id, activity_type, description, metadata) VALUES (?, ?, ?, ?)").bind(id, type, description, metadata ? JSON.stringify(metadata) : null));
  if (status !== current.status) activity("status_changed", `Estado cambiado a ${status}`, { from: current.status, to: status });
  if (status === "PERDIDO" && (lostReason !== (current.lost_reason ?? null) || lostReasonOther !== (current.lost_reason_other ?? null))) activity("lead_lost", `Lead perdido: ${lostReason}`, { reason: lostReason, detail: lostReasonOther });
  if (lastContactAt !== (current.last_contact_at ?? null)) activity("contact_recorded", "Último contacto actualizado", { at: lastContactAt });
  if (nextAction !== (current.next_action ?? null) || nextActionAt !== (current.next_action_at ?? null)) activity("follow_up_scheduled", nextAction ? `Próxima acción: ${nextAction}` : "Próxima acción eliminada", { action: nextAction, at: nextActionAt });
  if (notes !== (current.notes ?? null)) activity("notes_updated", "Notas comerciales actualizadas");
  if (expectedCommission !== (current.expected_commission ?? null) || finalCommission !== (current.final_commission ?? null)) activity("economics_updated", "Datos económicos actualizados");
  if (chosenOfferId !== (current.chosen_offer_id ?? null)) activity("offer_selected", chosenOfferId ? "Oferta final seleccionada" : "Oferta final eliminada", { offerId: chosenOfferId });
  await REVIEWS_DB.batch(statements);
  return NextResponse.json(await detail(id));
}
