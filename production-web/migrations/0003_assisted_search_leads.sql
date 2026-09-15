ALTER TABLE leads ADD COLUMN lead_type TEXT NOT NULL DEFAULT 'vehicle_offer';
ALTER TABLE leads ADD COLUMN search_type TEXT;
ALTER TABLE leads ADD COLUMN brand TEXT;
ALTER TABLE leads ADD COLUMN model TEXT;
ALTER TABLE leads ADD COLUMN vehicle_type TEXT;
ALTER TABLE leads ADD COLUMN budget_range TEXT;
ALTER TABLE leads ADD COLUMN purchase_timing TEXT;
ALTER TABLE leads ADD COLUMN source_page TEXT;
ALTER TABLE leads ADD COLUMN referrer TEXT;
ALTER TABLE leads ADD COLUMN utm_source TEXT;
ALTER TABLE leads ADD COLUMN utm_medium TEXT;
ALTER TABLE leads ADD COLUMN utm_campaign TEXT;
ALTER TABLE leads ADD COLUMN utm_content TEXT;
ALTER TABLE leads ADD COLUMN utm_term TEXT;
ALTER TABLE leads ADD COLUMN legal_accepted INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS leads_type_created_idx ON leads(lead_type, created_at DESC);
