import { NextResponse } from "next/server";
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
      final_commission, lost_reason, lead_type
    FROM leads
    ORDER BY CASE WHEN next_action_at IS NULL THEN 1 ELSE 0 END, next_action_at ASC, created_at DESC
    LIMIT 500
  `).all();
  return NextResponse.json({ leads: result.results ?? [] }, { headers: { "Cache-Control": "private, no-store" } });
}
