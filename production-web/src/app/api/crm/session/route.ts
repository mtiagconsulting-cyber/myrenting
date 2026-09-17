import { NextResponse } from "next/server";
import { createCrmSession, CRM_SESSION_COOKIE, validCrmPassword, validCrmSession } from "@/lib/crm-auth";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const authenticated = await validCrmSession(request);
  return NextResponse.json({ authenticated }, { status: authenticated ? 200 : 401 });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({})) as { password?: unknown };
  if (!(await validCrmPassword(String(body.password ?? "")))) return NextResponse.json({ error: "Clave incorrecta" }, { status: 401 });
  const session = await createCrmSession();
  const response = NextResponse.json({ authenticated: true });
  response.cookies.set(CRM_SESSION_COOKIE, session.value, { httpOnly: true, secure: true, sameSite: "strict", path: "/", maxAge: session.maxAge });
  return response;
}

export async function DELETE() {
  const response = NextResponse.json({ authenticated: false });
  response.cookies.set(CRM_SESSION_COOKIE, "", { httpOnly: true, secure: true, sameSite: "strict", path: "/", maxAge: 0 });
  return response;
}
