-- CREATE EXTENSION IF NOT EXISTS pgcrypto CASCADE;

-- CREATE EXTENSION IF NOT EXISTS vector CASCADE;

-- CREATE TABLE IF NOT EXISTS rsbr.embedding (
-- 	id SERIAL PRIMARY KEY,
-- 	"ListingID" BIGINT,
-- 	"PublicRemarks" TEXT,
-- 	"Embedding" vector(1536),
-- 	"CreatedAt" TIMESTAMP DEFAULT (now() at time zone 'utc')
-- )
	
-- ALTER TABLE rsbr.embedding
-- ADD CONSTRAINT fk_embedding_ListingID
-- FOREIGN KEY ("ListingID")
-- REFERENCES rsbr.property ("ListingID");

-- CREATE INDEX idx_embedding_ListingID
-- ON rsbr.embedding ("ListingID")