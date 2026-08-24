-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 07 — BANK PROFITABILITY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. BANK PROFITABILITY BY YEAR
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    net_income,
    roe_percent,
    roa_percent,
    shareholders_equity
FROM bank_financials_usd
ORDER BY
    fiscal_year,
    net_income DESC NULLS LAST;


-- ============================================================
-- 2. TOP 10 BY NET INCOME
-- ============================================================

WITH ranked_banks AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        net_income,
        roe_percent,
        roa_percent,

        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY net_income DESC NULLS LAST
        ) AS rank

    FROM bank_financials_usd

    WHERE net_income IS NOT NULL
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    net_income,
    roe_percent,
    roa_percent,
    rank
FROM ranked_banks
WHERE rank <= 10
ORDER BY
    fiscal_year,
    rank;


-- ============================================================
-- 3. TOP 10 BY ROE
-- ============================================================

WITH ranked_banks AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        roe_percent,
        net_income,

        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY roe_percent DESC NULLS LAST
        ) AS rank

    FROM bank_financials_usd

    WHERE
        roe_percent IS NOT NULL
        AND roe_percent BETWEEN -100 AND 100
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roe_percent,
    net_income,
    rank
FROM ranked_banks
WHERE rank <= 10
ORDER BY
    fiscal_year,
    rank;


-- ============================================================
-- 4. TOP 10 BY ROA
-- ============================================================

WITH ranked_banks AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        roa_percent,
        net_income,

        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY roa_percent DESC NULLS LAST
        ) AS rank

    FROM bank_financials_usd

    WHERE
        roa_percent IS NOT NULL
        AND roa_percent BETWEEN -100 AND 100
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roa_percent,
    net_income,
    rank
FROM ranked_banks
WHERE rank <= 10
ORDER BY
    fiscal_year,
    rank;