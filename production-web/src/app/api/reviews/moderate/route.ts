import { NextResponse } from "next/server";
import { isReviewAdmin, reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const { REVIEWS_DB, REVIEW_ADMIN_TOKEN } = reviewEnv();
  if (!isReviewAdmin(request, REVIEW_ADMIN_TOKEN)) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const result = await REVIEWS_DB.prepare("SELECT * FROM reviews ORDER BY created_at DESC LIMIT 200").all();
  return NextResponse.json({ reviews: result.results ?? [] });
}

export async function PATCH(request: Request) {
  const { REVIEWS_DB, REVIEW_ADMIN_TOKEN } = reviewEnv();
  if (!isReviewAdmin(request, REVIEW_ADMIN_TOKEN)) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const id = Number(body.id);
  const status = String(body.status ?? "");
  if (!Number.isInteger(id) || !["approved", "rejected"].includes(status)) return NextResponse.json({ error: "Solicitud no válida" }, { status: 400 });
  await REVIEWS_DB.prepare("UPDATE reviews SET status = ?, moderated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(status, id).run();
  return NextResponse.json({ ok: true });
}
