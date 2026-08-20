import { NextResponse } from "next/server";
import { isReviewAdmin, reviewEnv } from "@/lib/reviews-db";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const { REVIEWS_DB, REVIEW_ADMIN_TOKEN } = reviewEnv();
  if (!isReviewAdmin(request, REVIEW_ADMIN_TOKEN)) return NextResponse.json({ error: "No autorizado" }, { status: 401 });
  const body = await request.json().catch(() => ({})) as Record<string, unknown>;
  const customerName = String(body.customerName ?? "").trim().slice(0, 100);
  const vehicleName = String(body.vehicleName ?? "").trim().slice(0, 120);
  const customerType = String(body.customerType ?? "").trim().slice(0, 30);
  if (!customerName) return NextResponse.json({ error: "Indica el nombre del cliente." }, { status: 400 });
  const token = crypto.randomUUID();
  await REVIEWS_DB.prepare("INSERT INTO review_invites (token, customer_name, vehicle_name, customer_type) VALUES (?, ?, ?, ?)").bind(token, customerName, vehicleName, customerType).run();
  const url = `${new URL(request.url).origin}/opinar?token=${token}`;
  return NextResponse.json({ token, url });
}
