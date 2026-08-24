-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- 04 — COUNTRY PERFORMANCE ANALYSIS
-- ============================================================


-- ============================================================
-- 1. COUNTRY PERFORMANCE — LATEST AVAILABLE YEAR
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    COUNT(DISTINCT bank_name) AS bank_count,
    SUM(total_assets) AS total_assets,
    SUM(total_deposits) AS total_deposits,
    SUM(total_loans) AS total_loans,
    SUM(net_income) AS total_net_income,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY total_assets DESC NULLS LAST;


-- ============================================================
-- 2. TOP 10 COUNTRIES BY ASSETS
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    SUM(total_assets) AS total_assets
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY total_assets DESC NULLS LAST
LIMIT 10;


-- ============================================================
-- 3. TOP 10 COUNTRIES BY DEPOSITS
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    SUM(total_deposits) AS total_deposits
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY total_deposits DESC NULLS LAST
LIMIT 10;


-- ============================================================
-- 4. TOP 10 COUNTRIES BY LOANS
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    SUM(total_loans) AS total_loans
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY total_loans DESC NULLS LAST
LIMIT 10;


-- ============================================================
-- 5. TOP 10 COUNTRIES BY NET INCOME
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    SUM(net_income) AS total_net_income
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY total_net_income DESC NULLS LAST
LIMIT 10;


-- ============================================================
-- 6. COUNTRY PROFITABILITY
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa,
    SUM(net_income) AS total_net_income
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY average_roe DESC NULLS LAST;


-- ============================================================
-- 7. COUNTRY RISK
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY average_npl_ratio DESC NULLS LAST;


-- ============================================================
-- 8. COUNTRY BANKING DEPTH
-- ============================================================

WITH latest_year AS (
    SELECT MAX(fiscal_year) AS fiscal_year
    FROM bank_financials
)
SELECT
    iso3_code,
    COUNT(DISTINCT bank_name) AS bank_count
FROM bank_financials
WHERE fiscal_year = (
    SELECT fiscal_year
    FROM latest_year
)
GROUP BY iso3_code
ORDER BY bank_count DESC;


-- ============================================================
-- 9. COUNTRY PERFORMANCE BY YEAR
-- ============================================================

SELECT
    iso3_code,
    fiscal_year,
    COUNT(DISTINCT bank_name) AS bank_count,
    SUM(total_assets) AS total_assets,
    SUM(total_deposits) AS total_deposits,
    SUM(total_loans) AS total_loans,
    SUM(net_income) AS total_net_income,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy
FROM bank_financials
GROUP BY
    iso3_code,
    fiscal_year
ORDER BY
    iso3_code,
    fiscal_year;


-- ============================================================
-- 10. COUNTRY ASSET GROWTH — 2020 TO 2025
-- ============================================================

WITH country_period AS (
    SELECT
        iso3_code,

        SUM(total_assets) FILTER (
            WHERE fiscal_year = 2020
        ) AS assets_2020,

        SUM(total_assets) FILTER (
            WHERE fiscal_year = 2025
        ) AS assets_2025

    FROM bank_financials
    GROUP BY iso3_code
)
SELECT
    iso3_code,
    assets_2020,
    assets_2025,

    assets_2025 - assets_2020
        AS absolute_asset_growth,

    CASE
        WHEN assets_2020 IS NOT NULL
         AND assets_2020 <> 0
        THEN (
            (assets_2025 - assets_2020)
            / assets_2020
        ) * 100
    END AS asset_growth_percent

FROM country_period
WHERE
    assets_2020 IS NOT NULL
    AND assets_2025 IS NOT NULL
ORDER BY
    asset_growth_percent DESC NULLS LAST;