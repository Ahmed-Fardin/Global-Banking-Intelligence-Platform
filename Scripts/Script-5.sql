ALTER TABLE countries
ALTER COLUMN currency_id DROP NOT NULL;

SELECT COUNT(*)
FROM countries;

SELECT COUNT(*)
FROM countries;


SELECT COUNT(*)
FROM countries
WHERE region_id IS NULL;


SELECT COUNT(*)
FROM countries
WHERE currency_id IS NULL;


SELECT
    c.country_name,
    r.region_name,
    cu.currency_code,
    cu.currency_name

FROM countries c

LEFT JOIN regions r
ON c.region_id = r.region_id

LEFT JOIN currencies cu
ON c.currency_id = cu.currency_id

ORDER BY c.country_name;