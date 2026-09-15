import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../../", import.meta.url);
const read = (path) => readFile(new URL(path, root), "utf8");
const [component, api, migration, home, listing] = await Promise.all([
  read("src/components/leads/AssistedSearchCTA.tsx"), read("src/app/api/leads/route.ts"),
  read("migrations/0003_assisted_search_leads.sql"), read("src/app/page.tsx"), read("src/components/seo/SeoListingPage.tsx"),
]);

test("el wizard implementa los cinco pasos y conserva el contexto", () => {
  for (const copy of ["¿Qué coche estás buscando?", "¿Cuánto quieres pagar", "¿Cuántos kilómetros", "¿Para quién es el coche?", "Ya sabemos qué buscar."]) assert.match(component, new RegExp(copy.replace(/[?¿.]/g, "\\$&")));
  assert.match(component, /initialForm\(context\)/);
  assert.match(component, /Paso \{step\} de 5/);
  assert.match(component, /setStep\(\(current\) => current - 1\)/);
  assert.match(component, /event\.key !== "Tab"/);
  assert.match(component, /trigger\?\.focus/);
});

test("el funnel registra todos los eventos GA4 requeridos", () => {
  for (const event of ["assisted_search_cta_view", "assisted_search_started", "assisted_search_step_", "assisted_search_contact_view", "assisted_search_lead"]) assert.match(component, new RegExp(event));
  for (const dimension of ["source_page", "brand", "model", "customer_type", "budget_range"]) assert.match(component, new RegExp(dimension));
});

test("los leads asistidos se validan, guardan y recomiendan hasta tres coches", () => {
  assert.match(api, /body\.leadType === "assisted_search"/);
  assert.match(api, /legalAccepted/);
  assert.match(api, /\.slice\(0, 3\)/);
  assert.match(api, /lead_type/);
  assert.match(api, /const metadata = JSON\.stringify/);
  assert.match(api, /vehicle_id, vehicle_name, offer_id/);
  assert.match(component, /formsubmit\.co\/ajax\/mtiagconsulting@gmail\.com/);
  for (const column of ["search_type", "brand", "model", "vehicle_type", "budget_range", "purchase_timing", "source_page", "referrer", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]) assert.match(migration, new RegExp(column));
});

test("el lanzamiento inicial no sustituye CTAs ni se extiende a todas las páginas", () => {
  assert.match(home, /AssistedSearchCTA/);
  assert.match(listing, /canonical === "\/renting"/);
  for (const path of ["kia/niro", "peugeot/208", "bmw/serie-1", "hyundai/tucson", "volkswagen/t-roc", "nissan/qashqai"]) assert.match(listing, new RegExp(path));
  assert.match(listing, /<VehicleGrid items=\{listings\}/);
});
