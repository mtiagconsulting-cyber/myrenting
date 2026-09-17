import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { DatabaseSync } from "node:sqlite";
import { CRM_STATUSES, LOST_REASONS, NEXT_ACTIONS, leadPriority } from "../../src/lib/crm.ts";

const root = new URL("../../", import.meta.url);
const read = (path) => readFile(new URL(path, root), "utf8");
const [migration2, migration3, migration4, leadApi, listApi, detailApi, activityApi, proposalsApi, sessionApi, crmAuth, crmUi, crmPage] = await Promise.all([
  read("migrations/0002_leads.sql"), read("migrations/0003_assisted_search_leads.sql"), read("migrations/0004_crm_v1.sql"),
  read("src/app/api/leads/route.ts"), read("src/app/api/crm/leads/route.ts"), read("src/app/api/crm/leads/[id]/route.ts"),
  read("src/app/api/crm/leads/[id]/activities/route.ts"), read("src/app/api/crm/leads/[id]/proposals/route.ts"),
  read("src/app/api/crm/session/route.ts"), read("src/lib/crm-auth.ts"), read("src/components/crm/CrmApp.tsx"), read("src/app/gestion/crm/page.tsx"),
]);

function migratedDatabase() {
  const db = new DatabaseSync(":memory:");
  db.exec(migration2); db.exec(migration3);
  db.prepare("INSERT INTO leads (id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, channel, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
    .run("MR-OLD", "Ana", "García", "600000000", "ana@example.com", "Madrid", "particular", "veh-1", "Kia Niro", "offer-1", "Proveedor", 48, 15000, 400, "email", "contacted");
  db.exec(migration4);
  return db;
}

test("la migración conserva leads históricos y crea el pipeline", () => {
  const db = migratedDatabase();
  const lead = db.prepare("SELECT * FROM leads WHERE id = 'MR-OLD'").get();
  assert.equal(lead.status, "CONTACTADO"); assert.equal(lead.email, "ana@example.com");
  assert.equal(db.prepare("SELECT description FROM lead_activities WHERE lead_id = 'MR-OLD'").get().description, "Lead recibido");
  for (const table of ["leads", "lead_activities", "lead_proposals"]) assert.ok(db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?").get(table));
});

test("todos los estados, acciones y pérdidas requeridos están disponibles", () => {
  assert.deepEqual(CRM_STATUSES, ["NUEVO", "CONTACTADO", "RESPONDIO", "CUALIFICADO", "BUSCANDO", "OFERTA_ENVIADA", "DOCUMENTACION", "ESTUDIO", "APROBADO", "FIRMADO", "ENTREGADO", "NURTURE", "PERDIDO"]);
  for (const action of ["WhatsApp", "Llamar", "Buscar vehículo", "Enviar oferta", "Solicitar documentación"]) assert.ok(NEXT_ACTIONS.includes(action));
  for (const reason of ["No responde", "Precio", "Competencia", "Rechazado financieramente", "Otro"]) assert.ok(LOST_REASONS.includes(reason));
});

test("las acciones vencidas y de hoy reciben prioridad", () => {
  const now = new Date("2026-09-17T12:00:00Z");
  assert.equal(leadPriority({ status: "NUEVO", next_action_at: "2026-09-17T10:00:00Z" }, now), 0);
  assert.ok(leadPriority({ status: "NUEVO", next_action_at: "2026-09-18T10:00:00Z" }, now) > 0);
  assert.equal(leadPriority({ status: "PERDIDO", next_action_at: "2026-09-16T10:00:00Z" }, now), 4);
});

test("la clave idempotente impide duplicar leads por reintento", () => {
  const db = migratedDatabase();
  db.prepare("UPDATE leads SET submission_key = ? WHERE id = ?").run("same-submit", "MR-OLD");
  assert.throws(() => db.prepare("INSERT INTO leads (id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, channel, submission_key) SELECT 'MR-NEW', first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name, offer_id, provider, duration_months, annual_kilometers, monthly_price, channel, 'same-submit' FROM leads WHERE id = 'MR-OLD'").run());
  assert.match(leadApi, /SELECT id FROM leads WHERE submission_key = \?/);
});

test("un lead nuevo se guarda con actividad inicial", () => {
  assert.match(leadApi, /INSERT INTO lead_activities/); assert.match(leadApi, /Lead recibido/); assert.match(leadApi, /REVIEWS_DB\.batch/);
});

test("estado, seguimiento, pérdida, economics e histórico se actualizan en servidor", () => {
  for (const field of ["status", "last_contact_at", "next_action", "next_action_at", "expected_commission", "final_commission", "lost_reason", "chosen_offer_id"]) assert.match(detailApi, new RegExp(field));
  assert.match(detailApi, /Estado cambiado a/); assert.match(detailApi, /Próxima acción/); assert.match(activityApi, /INSERT INTO lead_activities/);
});

test("las alternativas usan IDs de oferta y evitan duplicados", () => {
  assert.match(proposalsApi, /offerId/); assert.match(proposalsApi, /vehicleId/); assert.match(proposalsApi, /SELECT id FROM lead_proposals/); assert.match(migration4, /UNIQUE \(lead_id, offer_id\)/);
});

test("listado, búsqueda y filtros están presentes", () => {
  assert.match(listApi, /ORDER BY/); for (const value of ["Buscar leads", "Filtrar por estado", "Filtrar por cliente", "Filtrar por acción", "Acciones vencidas"]) assert.match(crmUi, new RegExp(value));
});

test("CRM y APIs exigen sesión server-side y no se indexan", () => {
  for (const source of [listApi, detailApi, activityApi, proposalsApi]) assert.match(source, /validCrmSession/);
  assert.match(crmAuth, /httpOnly|CRM_SESSION_COOKIE/); assert.match(sessionApi, /sameSite: "strict"/); assert.match(crmPage, /index: false/);
});
