-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- 05 — GLOBAL BANKING TRENDS
-- ============================================================


-- ============================================================
-- 1. GLOBAL YEARLY SUMMARY
-- ============================================================

SELECT
    fiscal_year,
    COUNT(DISTINCT bank_name) AS bank_count,
    COUNT(DISTINCT iso3_code) AS country_count,
    SUM(total_assets) AS total_assets,
    SUM(total_deposits) AS total_deposits,
    SUM(total_loans) AS total_loans,
    SUM(net_income) AS total_net_income,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy,
    AVG(cost_income_ratio)
        AS average_cost_income_ratio,
    AVG(loan_to_deposit_ratio)
        AS average_loan_to_deposit_ratio
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 2. GLOBAL ASSET GROWTH
-- ============================================================

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(total_assets) AS total_assets
    FROM bank_financials
    GROUP BY fiscal_year
),
growth AS (
    SELECT
        fiscal_year,
        total_assets,
        LAG(total_assets)
            OVER (
                ORDER BY fiscal_year
            ) AS previous_assets
    FROM yearly
)
SELECT
    fiscal_year,
    total_assets,
    previous_assets,
    total_assets - previous_assets
        AS asset_growth,
    CASE
        WHEN previous_assets IS NOT NULL
         AND previous_assets <> 0
        THEN (
            (total_assets - previous_assets)
            / previous_assets
        ) * 100
    END AS asset_growth_percent
FROM growth
ORDER BY fiscal_year;


-- ============================================================
-- 3. GLOBAL DEPOSIT GROWTH
-- ============================================================

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(total_deposits) AS total_deposits
    FROM bank_financials
    GROUP BY fiscal_year
),
growth AS (
    SELECT
        fiscal_year,
        total_deposits,
        LAG(total_deposits)
            OVER (
                ORDER BY fiscal_year
            ) AS previous_deposits
    FROM yearly
)
SELECT
    fiscal_year,
    total_deposits,
    previous_deposits,
    total_deposits - previous_deposits
        AS deposit_growth,
    CASE
        WHEN previous_deposits IS NOT NULL
         AND previous_deposits <> 0
        THEN (
            (total_deposits - previous_deposits)
            / previous_deposits
        ) * 100
    END AS deposit_growth_percent
FROM growth
ORDER BY fiscal_year;


-- ============================================================
-- 4. GLOBAL LOAN GROWTH
-- ============================================================

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(total_loans) AS total_loans
    FROM bank_financials
    GROUP BY fiscal_year
),
growth AS (
    SELECT
        fiscal_year,
        total_loans,
        LAG(total_loans)
            OVER (
                ORDER BY fiscal_year
            ) AS previous_loans
    FROM yearly
)
SELECT
    fiscal_year,
    total_loans,
    previous_loans,
    total_loans - previous_loans
        AS loan_growth,
    CASE
        WHEN previous_loans IS NOT NULL
         AND previous_loans <> 0
        THEN (
            (total_loans - previous_loans)
            / previous_loans
        ) * 100
    END AS loan_growth_percent
FROM growth
ORDER BY fiscal_year;


-- ============================================================
-- 5. GLOBAL NET INCOME TREND
-- ============================================================

SELECT
    fiscal_year,
    SUM(net_income) AS total_net_income,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 6. GLOBAL RISK TREND
-- ============================================================

SELECT
    fiscal_year,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 7. GLOBAL EFFICIENCY TREND
-- ============================================================

SELECT
    fiscal_year,
    AVG(cost_income_ratio)
        AS average_cost_income_ratio,
    AVG(loan_to_deposit_ratio)
        AS average_loan_to_deposit_ratio
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 8. GLOBAL BANKING KPI DATASET
-- ============================================================

SELECT
    fiscal_year,
    COUNT(DISTINCT bank_name) AS bank_count,
    COUNT(DISTINCT iso3_code) AS country_count,
    SUM(total_assets) AS total_assets,
    SUM(total_deposits) AS total_deposits,
    SUM(total_loans) AS total_loans,
    SUM(net_income) AS total_net_income,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa,
    AVG(npl_ratio) AS average_npl_ratio,
    AVG(capital_adequacy_percent)
        AS average_capital_adequacy,
    AVG(cost_income_ratio)
        AS average_cost_income_ratio,
    AVG(loan_to_deposit_ratio)
        AS average_loan_to_deposit_ratio
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 9. 2020 TO 2025 GLOBAL ASSET CHANGE
-- ============================================================

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(total_assets) AS total_assets
    FROM bank_financials
    GROUP BY fiscal_year
),
period AS (
    SELECT
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
    FROM yearly
)
SELECT
    assets_2020,
    assets_2025,
    assets_2025 - assets_2020
        AS absolute_change,
    CASE
        WHEN assets_2020 IS NOT NULL
         AND assets_2020 <> 0
        THEN (
            (assets_2025 - assets_2020)
            / assets_2020
        ) * 100
    END AS percentage_change
FROM period;


-- ============================================================
-- 10. 2020 TO 2025 GLOBAL NET INCOME CHANGE
-- ============================================================

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(net_income) AS total_net_income
    FROM bank_financials
    GROUP BY fiscal_year
),
period AS (
    SELECT
        MAX(
            total_net_income
        ) FILTER (
            WHERE fiscal_year = 2020
        ) AS income_2020,

        MAX(
            total_net_income
        ) FILTER (
            WHERE fiscal_year = 2025
        ) AS income_2025
    FROM yearly
)
SELECT
    income_2020,
    income_2025,
    income_2025 - income_2020
        AS absolute_change,
    CASE
        WHEN income_2020 IS NOT NULL
         AND income_2020 <> 0
        THEN (
            (income_2025 - income_2020)
            / income_2020
        ) * 100
    END AS percentage_change
FROM period;