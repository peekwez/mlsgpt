CREATE TABLE IF NOT EXISTS rsbr.users (
    id SERIAL PRIMARY KEY,
    "Sub" TEXT,
    "Email" BIGINT,
    "Name" NUMERIC,
    "EmailVerified" BOOLEAN,
    "CreatedAt" TIMESTAMP DEFAULT (now() at time zone 'utc')
);
CREATE INDEX idx_users_email ON rsbr.users("Email");