-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 10 — BANK GROWTH ANALYSIS
-- USD MONETARY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. BANK YEARLY FINANCIAL POSITION
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_assets,
    total_deposits,
    total_loans,
    net_income
FROM bank_financials_usd
ORDER BY
    bank_name,
    fiscal_year;


-- ============================================================
-- 2. YEAR-OVER-YEAR ASSET GROWTH
-- ============================================================

WITH bank_history AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        total_assets,

        LAG(total_assets)
            OVER (
                PARTITION BY iso3_code, bank_name
                ORDER BY fiscal_year
            ) AS previous_year_assets

    FROM bank_financials_usd
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_assets,
    previous_year_assets,

    CASE
        WHEN previous_year_assets IS NULL
            THEN NULL
        WHEN previous_year_assets = 0
            THEN NULL
        ELSE
            (
                (
                    total_assets
                    - previous_year_assets
                )
                / ABS(previous_year_assets)
            ) * 100
    END AS asset_growth_percent

FROM bank_history

ORDER BY
    bank_name,
    fiscal_year;


-- ============================================================
-- 3. YEAR-OVER-YEAR LOAN GROWTH
-- ============================================================

WITH bank_history AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        total_loans,

        LAG(total_loans)
            OVER (
                PARTITION BY iso3_code, bank_name
                ORDER BY fiscal_year
            ) AS previous_year_loans

    FROM bank_financials_usd
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_loans,
    previous_year_loans,

    CASE
        WHEN previous_year_loans IS NULL
            THEN NULL
        WHEN previous_year_loans = 0
            THEN NULL
        ELSE
            (
                (
                    total_loans
                    - previous_year_loans
                )
                / ABS(previous_year_loans)
            ) * 100
    END AS loan_growth_percent

FROM bank_history

ORDER BY
    bank_name,
    fiscal_year;


-- ============================================================
-- 4. YEAR-OVER-YEAR NET INCOME GROWTH
-- ============================================================

WITH bank_history AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,
        net_income,

        LAG(net_income)
            OVER (
                PARTITION BY iso3_code, bank_name
                ORDER BY fiscal_year
            ) AS previous_year_net_income

    FROM bank_financials_usd
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    net_income,
    previous_year_net_income,

    CASE
        WHEN previous_year_net_income IS NULL
            THEN NULL
        WHEN previous_year_net_income = 0
            THEN NULL
        ELSE
            (
                (
                    net_income
                    - previous_year_net_income
                )
                / ABS(previous_year_net_income)
            ) * 100
    END AS net_income_growth_percent

FROM bank_history

ORDER BY
    bank_name,
    fiscal_year;