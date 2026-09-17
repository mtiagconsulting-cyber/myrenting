import { reviewEnv } from "@/lib/reviews-db";

export const CRM_SESSION_COOKIE = "myrenting_crm_session";
const SESSION_SECONDS = 60 * 60 * 12;

function secret() {
  const env = reviewEnv();
  return env.CRM_ADMIN_TOKEN || env.REVIEW_ADMIN_TOKEN || "";
}

function bytes(value: string) { return new TextEncoder().encode(value); }
function toBase64Url(buffer: ArrayBuffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer))).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}

async function digest(value: string) {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", bytes(value)));
}

export async function secureEqual(first: string, second: string) {
  const [a, b] = await Promise.all([digest(first), digest(second)]);
  if (a.length !== b.length) return false;
  let difference = 0;
  for (let index = 0; index < a.length; index += 1) difference |= a[index] ^ b[index];
  return difference === 0;
}

async function signature(payload: string, keyValue: string) {
  const key = await crypto.subtle.importKey("raw", bytes(keyValue), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return toBase64Url(await crypto.subtle.sign("HMAC", key, bytes(payload)));
}

export async function createCrmSession() {
  const key = secret();
  if (!key) throw new Error("CRM_ADMIN_TOKEN no configurado");
  const expires = Math.floor(Date.now() / 1000) + SESSION_SECONDS;
  const payload = String(expires);
  return { value: `${payload}.${await signature(payload, key)}`, maxAge: SESSION_SECONDS };
}

export async function validCrmPassword(password: string) {
  const key = secret();
  return Boolean(key) && secureEqual(password, key);
}

export async function validCrmSession(request: Request) {
  const cookie = request.headers.get("cookie")?.split(";").map((item) => item.trim()).find((item) => item.startsWith(`${CRM_SESSION_COOKIE}=`))?.slice(CRM_SESSION_COOKIE.length + 1) ?? "";
  const [expiresText, supplied] = cookie.split(".");
  const key = secret();
  const expires = Number(expiresText);
  if (!key || !supplied || !Number.isFinite(expires) || expires <= Date.now() / 1000) return false;
  return secureEqual(supplied, await signature(expiresText, key));
}
