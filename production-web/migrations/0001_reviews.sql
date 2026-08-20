CREATE TABLE IF NOT EXISTS review_invites (
  token TEXT PRIMARY KEY,
  customer_name TEXT,
  vehicle_name TEXT,
  customer_type TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  used_at TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invite_token TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_initial TEXT,
  city TEXT,
  vehicle_name TEXT,
  customer_type TEXT,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  title TEXT NOT NULL,
  comment TEXT NOT NULL,
  consent_publication INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  moderated_at TEXT,
  FOREIGN KEY (invite_token) REFERENCES review_invites(token)
);

CREATE INDEX IF NOT EXISTS reviews_status_created_idx ON reviews(status, created_at DESC);
