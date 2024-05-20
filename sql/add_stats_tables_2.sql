CREATE TABLE IF NOT EXISTS rsbr.city_stats (
    id SERIAL PRIMARY KEY,
    "City" TEXT,
    "InventoryCount" BIGINT,
    "AveragePrice" NUMERIC,
    "MedianPrice" NUMERIC,
    "MinimumPrice" NUMERIC,
    "MaximumPrice" NUMERIC,
    "AverageDaysOnMarket" NUMERIC,
    "MedianDaysOnMarket" NUMERIC,
    "MinimumDaysOnMarket" NUMERIC,
    "MaximumDaysOnMarket" NUMERIC,
    "AveragePricePerSqft" NUMERIC
);
CREATE INDEX idx_city_stats_city ON rsbr.city_stats("City");

CREATE TABLE IF NOT EXISTS rsbr.city_type_stats (
    id SERIAL PRIMARY KEY,
    "City" TEXT,
    "Type" TEXT,
    "InventoryCount" BIGINT,
    "AveragePrice" NUMERIC,
    "MedianPrice" NUMERIC,
    "MinimumPrice" NUMERIC,
    "MaximumPrice" NUMERIC,
    "AverageDaysOnMarket" NUMERIC,
    "MedianDaysOnMarket" NUMERIC,
    "MinimumDaysOnMarket" NUMERIC,
    "MaximumDaysOnMarket" NUMERIC,
    "AveragePricePerSqft" NUMERIC
);
CREATE INDEX idx_city_type_stats_city ON rsbr.city_type_stats("City");
CREATE INDEX idx_city_type_stats_type ON rsbr.city_type_stats("Type");

CREATE TABLE IF NOT EXISTS rsbr.city_property_type_stats (
    id SERIAL PRIMARY KEY,
    "City" TEXT,
    "PropertyType" TEXT,
    "InventoryCount" BIGINT,
    "AveragePrice" NUMERIC,
    "MedianPrice" NUMERIC,
    "MinimumPrice" NUMERIC,
    "MaximumPrice" NUMERIC,
    "AverageDaysOnMarket" NUMERIC,
    "MedianDaysOnMarket" NUMERIC,
    "MinimumDaysOnMarket" NUMERIC,
    "MaximumDaysOnMarket" NUMERIC,
    "AveragePricePerSqft" NUMERIC
);
CREATE INDEX idx_city_property_type_stats_city ON rsbr.city_property_type_stats("City");
CREATE INDEX idx_city_property_type_stats_property_type ON rsbr.city_property_type_stats("PropertyType");

CREATE TABLE IF NOT EXISTS rsbr.city_bedrooms_stats (
    id SERIAL PRIMARY KEY,
    "City" TEXT,
    "BedroomsTotal" BIGINT,
    "InventoryCount" BIGINT,
    "AveragePrice" NUMERIC,
    "MedianPrice" NUMERIC,
    "MinimumPrice" NUMERIC,
    "MaximumPrice" NUMERIC,
    "AverageDaysOnMarket" NUMERIC,
    "MedianDaysOnMarket" NUMERIC,
    "MinimumDaysOnMarket" NUMERIC,
    "MaximumDaysOnMarket" NUMERIC,
    "AveragePricePerSqft" NUMERIC
);
CREATE INDEX idx_city_bedrooms_stats_city ON rsbr.city_bedrooms_stats("City");
CREATE INDEX idx_city_bedrooms_stats_bedrooms ON rsbr.city_bedrooms_stats("BedroomsTotal");

CREATE TABLE IF NOT EXISTS rsbr.stats_info (
    id SERIAL PRIMARY KEY,
    "Attribute" TEXT,
    "Values" TEXT[]
)