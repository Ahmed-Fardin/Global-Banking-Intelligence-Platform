SELECT COUNT(*) AS total_regions
FROM regions;

SELECT COUNT(*) AS total_currencies
FROM currencies;

SELECT *
FROM regions
ORDER BY region_name;

SELECT *
FROM currencies
ORDER BY currency_code;

ALTER TABLE countries
ALTER COLUMN currency_id DROP NOT NULL;

ALTER TABLE countries
ADD COLUMN official_website TEXT;







