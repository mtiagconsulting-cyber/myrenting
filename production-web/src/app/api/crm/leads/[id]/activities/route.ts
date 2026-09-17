import { NextResponse } from "next/server";
import { validCrmSession } from "@/lib/crm-auth";
import { cleanCrmText } from "@/lib/crm";
import { reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";
type Context = { params: Promise<{ id: string }> };
const TYPES = ["note", "whatsapp", "call", "email", "provider", "document", "other"];

export async function POST(request: Request, context: Context) {
  if (!(await validCrmSession(request))) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const { id } = await context.params;
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const type = cleanCrmText(body.type, 30);
  const description = cleanCrmText(body.description, 2000);
  if (!TYPES.includes(type) || !description) return NextResponse.json({ error: "Indica el tipo y la descripción" }, { status: 400 });
  const { REVIEWS_DB } = reviewEnv();
  const lead = await REVIEWS_DB.prepare("SELECT id FROM leads WHERE id = ?").bind(id).first();
  if (!lead) return NextResponse.json({ error: "Lead no encontrado" }, { status: 404 });
  await REVIEWS_DB.batch([
    REVIEWS_DB.prepare("INSERT INTO lead_activities (lead_id, activity_type, description) VALUES (?, ?, ?)").bind(id, type, description),
    REVIEWS_DB.prepare("UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(id),
  ]);
  return NextResponse.json({ ok: true });
}
