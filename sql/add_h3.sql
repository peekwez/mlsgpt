CREATE TABLE IF NOT EXISTS rsbr.h3_index (
	id SERIAL PRIMARY KEY,
	"ListingID" BIGINT,
	"H3IndexR00" TEXT,
    "H3IndexR01" TEXT,
    "H3IndexR02" TEXT,
    "H3IndexR03" TEXT,
    "H3IndexR04" TEXT,
    "H3IndexR05" TEXT,
    "H3IndexR06" TEXT,
    "H3IndexR07" TEXT,
    "H3IndexR08" TEXT,
    "H3IndexR09" TEXT,
    "H3IndexR10" TEXT,
    "H3IndexR11" TEXT,
    "H3IndexR12" TEXT,
    "H3IndexR13" TEXT,
    "H3IndexR14" TEXT,
    "H3IndexR15" TEXT,
	"CreatedAt" TIMESTAMP DEFAULT (now() at time zone 'utc')
);
	
ALTER TABLE rsbr.h3_index
ADD CONSTRAINT fk_h3_index_ListingID
FOREIGN KEY ("ListingID")
REFERENCES rsbr.property ("ListingID");

CREATE INDEX idx_h3_ListingID
ON rsbr.h3_index ("ListingID");

CREATE INDEX idx_h3_H3IndexR00
ON rsbr.h3_index ("H3IndexR00");

CREATE INDEX idx_h3_H3IndexR01
ON rsbr.h3_index ("H3IndexR01");

CREATE INDEX idx_h3_H3IndexR02
ON rsbr.h3_index ("H3IndexR02");

CREATE INDEX idx_h3_H3IndexR03
ON rsbr.h3_index ("H3IndexR03");

CREATE INDEX idx_h3_H3IndexR04
ON rsbr.h3_index ("H3IndexR04");

CREATE INDEX idx_h3_H3IndexR05
ON rsbr.h3_index ("H3IndexR05");

CREATE INDEX idx_h3_H3IndexR06
ON rsbr.h3_index ("H3IndexR06");

CREATE INDEX idx_h3_H3IndexR07
ON rsbr.h3_index ("H3IndexR07");

CREATE INDEX idx_h3_H3IndexR08
ON rsbr.h3_index ("H3IndexR08");

CREATE INDEX idx_h3_H3IndexR09
ON rsbr.h3_index ("H3IndexR09");

CREATE INDEX idx_h3_H3IndexR10
ON rsbr.h3_index ("H3IndexR10");

CREATE INDEX idx_h3_H3IndexR11
ON rsbr.h3_index ("H3IndexR11");

CREATE INDEX idx_h3_H3IndexR12
ON rsbr.h3_index ("H3IndexR12");

CREATE INDEX idx_h3_H3IndexR13
ON rsbr.h3_index ("H3IndexR13");

CREATE INDEX idx_h3_H3IndexR14
ON rsbr.h3_index ("H3IndexR14");

CREATE INDEX idx_h3_H3IndexR15
ON rsbr.h3_index ("H3IndexR15")

-- Path: sql/add_h3.sql