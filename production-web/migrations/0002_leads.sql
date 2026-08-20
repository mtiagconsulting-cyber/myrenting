CREATE TABLE IF NOT EXISTS leads (
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
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'won', 'lost')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS leads_created_idx ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS leads_status_created_idx ON leads(status, created_at DESC);
