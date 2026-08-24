-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- 03 — BANK PERFORMANCE ANALYSIS
-- ============================================================


-- ============================================================
-- 1. LATEST AVAILABLE PERFORMANCE FOR EACH BANK
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.total_assets,
    f.total_deposits,
    f.total_loans,
    f.shareholders_equity,
    f.operating_income,
    f.net_income,
    f.roe_percent,
    f.roa_percent,
    f.capital_adequacy_percent,
    f.cost_income_ratio,
    f.loan_to_deposit_ratio,
    f.npl_ratio,
    f.employees,
    f.branches,
    f.reporting_currency
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
ORDER BY
    f.total_assets DESC NULLS LAST;


-- ============================================================
-- 2. TOP 10 BANKS BY TOTAL ASSETS
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.total_assets
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.total_assets IS NOT NULL
ORDER BY f.total_assets DESC
LIMIT 10;


-- ============================================================
-- 3. TOP 10 BANKS BY NET INCOME
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.net_income
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.net_income IS NOT NULL
ORDER BY f.net_income DESC
LIMIT 10;


-- ============================================================
-- 4. TOP 10 BANKS BY ROE
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.roe_percent
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.roe_percent IS NOT NULL
ORDER BY f.roe_percent DESC
LIMIT 10;


-- ============================================================
-- 5. TOP 10 BANKS BY ROA
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.roa_percent
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.roa_percent IS NOT NULL
ORDER BY f.roa_percent DESC
LIMIT 10;


-- ============================================================
-- 6. TOP 10 BANKS BY DEPOSITS
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.total_deposits
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.total_deposits IS NOT NULL
ORDER BY f.total_deposits DESC
LIMIT 10;


-- ============================================================
-- 7. TOP 10 BANKS BY LOANS
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.total_loans
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
WHERE f.total_loans IS NOT NULL
ORDER BY f.total_loans DESC
LIMIT 10;


-- ============================================================
-- 8. COMPLETE BANK/YEAR PERFORMANCE
-- ============================================================

SELECT
    iso3_code,
    bank_name,
    fiscal_year,
    total_assets,
    total_deposits,
    total_loans,
    shareholders_equity,
    operating_income,
    net_income,
    roe_percent,
    roa_percent,
    capital_adequacy_percent,
    cost_income_ratio,
    loan_to_deposit_ratio,
    npl_ratio,
    employees,
    branches
FROM bank_financials
ORDER BY
    bank_name,
    fiscal_year;


-- ============================================================
-- 9. BANK ASSET GROWTH — 2020 TO 2025
-- ============================================================

WITH bank_period AS (
    SELECT
        iso3_code,
        bank_name,

        MAX(
            total_assets
        ) FILTER (
            WHERE fiscal_year = 2020
        ) AS assets_2020,

        MAX(
            total_assets
        ) FILTER (
            WHERE fiscal_year = 2025
        ) AS assets_2025

    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    iso3_code,
    bank_name,
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

FROM bank_period
WHERE
    assets_2020 IS NOT NULL
    AND assets_2025 IS NOT NULL
ORDER BY
    asset_growth_percent DESC NULLS LAST;


-- ============================================================
-- 10. BANK FINANCIAL SCORECARD
-- ============================================================

WITH latest_bank_year AS (
    SELECT
        iso3_code,
        bank_name,
        MAX(fiscal_year) AS latest_year
    FROM bank_financials
    GROUP BY
        iso3_code,
        bank_name
)
SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year,
    f.total_assets,
    f.total_deposits,
    f.total_loans,
    f.net_income,
    f.roe_percent,
    f.roa_percent,
    f.capital_adequacy_percent,
    f.cost_income_ratio,
    f.loan_to_deposit_ratio,
    f.npl_ratio
FROM bank_financials AS f
INNER JOIN latest_bank_year AS l
    ON f.iso3_code = l.iso3_code
   AND f.bank_name = l.bank_name
   AND f.fiscal_year = l.latest_year
ORDER BY
    f.net_income DESC NULLS LAST;