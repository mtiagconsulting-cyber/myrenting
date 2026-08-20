import { getCloudflareContext } from "@opennextjs/cloudflare";

interface D1Result<T = Record<string, unknown>> { results?: T[]; success?: boolean; }
interface D1Statement {
  bind(...values: unknown[]): D1Statement;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  all<T = Record<string, unknown>>(): Promise<D1Result<T>>;
  run(): Promise<D1Result>;
}
interface D1Database { prepare(query: string): D1Statement; batch(statements: D1Statement[]): Promise<D1Result[]>; }

interface ReviewEnv { REVIEWS_DB: D1Database; REVIEW_ADMIN_TOKEN?: string; }

export function reviewEnv() {
  return getCloudflareContext().env as unknown as ReviewEnv;
}

export function isReviewAdmin(request: Request, token?: string) {
  const supplied = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ?? "";
  return Boolean(token && supplied && supplied === token);
}

export const publicReviewFields = "id, first_name, last_initial, city, vehicle_name, customer_type, rating, title, comment, created_at";
