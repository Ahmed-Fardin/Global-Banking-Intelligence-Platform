-- ==========================================================
-- FOREIGN KEY: COUNTRIES → REGIONS
-- ==========================================================

ALTER TABLE countries
ADD CONSTRAINT fk_countries_regions
FOREIGN KEY (region_id)
REFERENCES regions(region_id);


-- ==========================================================
-- FOREIGN KEY: COUNTRIES → CURRENCIES
-- ==========================================================

ALTER TABLE countries
ADD CONSTRAINT fk_countries_currencies
FOREIGN KEY (currency_id)
REFERENCES currencies(currency_id);

-- ==========================================================
-- FOREIGN KEY: BANKS → COUNTRIES
-- ==========================================================

ALTER TABLE banks
ADD CONSTRAINT fk_banks_countries
FOREIGN KEY (country_id)
REFERENCES countries(country_id);

-- ==========================================================
-- FOREIGN KEY: COUNTRY_METRICS → COUNTRIES
-- ==========================================================

ALTER TABLE country_metrics
ADD CONSTRAINT fk_country_metrics_countries
FOREIGN KEY (country_id)
REFERENCES countries(country_id);

-- ==========================================================
-- FOREIGN KEY: BANKING_SECTOR_METRICS → COUNTRIES
-- ==========================================================

ALTER TABLE banking_sector_metrics
ADD CONSTRAINT fk_banking_sector_metrics_countries
FOREIGN KEY (country_id)
REFERENCES countries(country_id);

-- ==========================================================
-- FOREIGN KEY: BANK_FINANCIALS → BANKS
-- ==========================================================

ALTER TABLE bank_financials
ADD CONSTRAINT fk_bank_financials_banks
FOREIGN KEY (bank_id)
REFERENCES banks(bank_id);







SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name;
