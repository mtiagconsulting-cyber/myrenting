ALTER TABLE leads RENAME TO leads_before_crm;

CREATE TABLE leads (
  id TEXT PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  city TEXT NOT NULL,
  customer_type TEXT NOT NULL,
  vehicle_id TEXT NOT NULL,
  vehicle_name TEXT NOT NULL,
  offer_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  duration_months INTEGER NOT NULL,
  annual_kilometers INTEGER NOT NULL,
  monthly_price REAL NOT NULL,
  price_includes_vat INTEGER NOT NULL DEFAULT 0,
  initial_payment REAL NOT NULL DEFAULT 0,
  channel TEXT NOT NULL CHECK (channel IN ('email', 'whatsapp')),
  page_url TEXT,
  status TEXT NOT NULL DEFAULT 'NUEVO' CHECK (status IN ('NUEVO', 'CONTACTADO', 'RESPONDIO', 'CUALIFICADO', 'BUSCANDO', 'OFERTA_ENVIADA', 'DOCUMENTACION', 'ESTUDIO', 'APROBADO', 'FIRMADO', 'ENTREGADO', 'NURTURE', 'PERDIDO')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  lead_type TEXT NOT NULL DEFAULT 'vehicle_offer',
  search_type TEXT,
  brand TEXT,
  model TEXT,
  vehicle_type TEXT,
  budget_range TEXT,
  purchase_timing TEXT,
  source_page TEXT,
  referrer TEXT,
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_content TEXT,
  utm_term TEXT,
  legal_accepted INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_contact_at TEXT,
  next_action TEXT,
  next_action_at TEXT,
  expected_commission REAL,
  final_commission REAL,
  notes TEXT,
  lost_reason TEXT,
  lost_reason_other TEXT,
  chosen_offer_id TEXT,
  submission_key TEXT
);

INSERT INTO leads (
  id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name,
  offer_id, provider, duration_months, annual_kilometers, monthly_price, price_includes_vat,
  initial_payment, channel, page_url, status, created_at, lead_type, search_type, brand, model,
  vehicle_type, budget_range, purchase_timing, source_page, referrer, utm_source, utm_medium,
  utm_campaign, utm_content, utm_term, legal_accepted, updated_at
)
SELECT
  id, first_name, last_name, phone, email, city, customer_type, vehicle_id, vehicle_name,
  offer_id, provider, duration_months, annual_kilometers, monthly_price, price_includes_vat,
  initial_payment, channel, page_url,
  CASE status
    WHEN 'contacted' THEN 'CONTACTADO'
    WHEN 'qualified' THEN 'CUALIFICADO'
    WHEN 'won' THEN 'FIRMADO'
    WHEN 'lost' THEN 'PERDIDO'
    ELSE 'NUEVO'
  END,
  created_at, lead_type, search_type, brand, model, vehicle_type, budget_range, purchase_timing,
  source_page, referrer, utm_source, utm_medium, utm_campaign, utm_content, utm_term,
  legal_accepted, created_at
FROM leads_before_crm;

DROP TABLE leads_before_crm;

CREATE UNIQUE INDEX leads_submission_key_idx ON leads(submission_key) WHERE submission_key IS NOT NULL;
CREATE INDEX leads_created_idx ON leads(created_at DESC);
CREATE INDEX leads_status_created_idx ON leads(status, created_at DESC);
CREATE INDEX leads_next_action_idx ON leads(next_action_at) WHERE next_action_at IS NOT NULL;
CREATE INDEX leads_type_created_idx ON leads(lead_type, created_at DESC);
CREATE INDEX leads_email_idx ON leads(email);

CREATE TABLE lead_activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id TEXT NOT NULL,
  activity_type TEXT NOT NULL,
  description TEXT NOT NULL,
  metadata TEXT,
  actor TEXT NOT NULL DEFAULT 'admin',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX lead_activities_lead_created_idx ON lead_activities(lead_id, created_at DESC);

CREATE TABLE lead_proposals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id TEXT NOT NULL,
  offer_id TEXT NOT NULL,
  vehicle_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  UNIQUE (lead_id, offer_id)
);

CREATE INDEX lead_proposals_lead_idx ON lead_proposals(lead_id, created_at DESC);

INSERT INTO lead_activities (lead_id, activity_type, description, actor, created_at)
SELECT id, 'lead_received', 'Lead recibido', 'system', created_at FROM leads;
