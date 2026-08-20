import { NextResponse } from "next/server";
import { publicReviewFields, reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";

export async function GET() {
  const { REVIEWS_DB } = reviewEnv();
  const result = await REVIEWS_DB.prepare(`SELECT ${publicReviewFields} FROM reviews WHERE status = 'approved' AND consent_publication = 1 ORDER BY created_at DESC LIMIT 100`).all();
  return NextResponse.json({ reviews: result.results ?? [] });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body || body.website) return NextResponse.json({ ok: true });
  const token = String(body.token ?? "").trim();
  const firstName = String(body.firstName ?? "").trim().slice(0, 60);
  const lastInitial = String(body.lastName ?? "").trim().slice(0, 1).toUpperCase();
  const city = String(body.city ?? "").trim().slice(0, 80);
  const title = String(body.title ?? "").trim().slice(0, 100);
  const comment = String(body.comment ?? "").trim().slice(0, 1500);
  const rating = Number(body.rating);
  const consent = body.consent === true;
  if (!token || !firstName || !title || comment.length < 30 || !Number.isInteger(rating) || rating < 1 || rating > 5 || !consent) {
    return NextResponse.json({ error: "Revisa los campos obligatorios y escribe al menos 30 caracteres." }, { status: 400 });
  }
  const { REVIEWS_DB } = reviewEnv();
  const invite = await REVIEWS_DB.prepare("SELECT token, vehicle_name, customer_type, used_at FROM review_invites WHERE token = ?").bind(token).first<{ token: string; vehicle_name: string | null; customer_type: string | null; used_at: string | null }>();
  if (!invite || invite.used_at) return NextResponse.json({ error: "Este enlace no es válido o ya se ha utilizado." }, { status: 400 });
  try {
    await REVIEWS_DB.batch([
      REVIEWS_DB.prepare("INSERT INTO reviews (invite_token, first_name, last_initial, city, vehicle_name, customer_type, rating, title, comment, consent_publication) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)").bind(token, firstName, lastInitial, city, invite.vehicle_name, invite.customer_type, rating, title, comment),
      REVIEWS_DB.prepare("UPDATE review_invites SET used_at = CURRENT_TIMESTAMP WHERE token = ? AND used_at IS NULL").bind(token),
    ]);
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "No se pudo guardar la opinión. Comprueba que el enlace no se haya utilizado." }, { status: 409 });
  }
}
