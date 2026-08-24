-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 06 — BANK FINANCIAL RANKINGS
-- ============================================================

-- ------------------------------------------------------------
-- 1. BANK RANKING BY TOTAL ASSETS
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_assets,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_assets DESC NULLS LAST
    ) AS asset_rank
FROM bank_financials
WHERE total_assets IS NOT NULL
ORDER BY
    fiscal_year,
    asset_rank;


-- ------------------------------------------------------------
-- 2. BANK RANKING BY TOTAL DEPOSITS
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_deposits,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_deposits DESC NULLS LAST
    ) AS deposit_rank
FROM bank_financials
WHERE total_deposits IS NOT NULL
ORDER BY
    fiscal_year,
    deposit_rank;


-- ------------------------------------------------------------
-- 3. BANK RANKING BY TOTAL LOANS
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_loans,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_loans DESC NULLS LAST
    ) AS loan_rank
FROM bank_financials
WHERE total_loans IS NOT NULL
ORDER BY
    fiscal_year,
    loan_rank;


-- ------------------------------------------------------------
-- 4. BANK RANKING BY NET INCOME
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    net_income,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY net_income DESC NULLS LAST
    ) AS net_income_rank
FROM bank_financials
WHERE net_income IS NOT NULL
ORDER BY
    fiscal_year,
    net_income_rank;


-- ------------------------------------------------------------
-- 5. BANK RANKING BY ROE
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roe_percent,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY roe_percent DESC NULLS LAST
    ) AS roe_rank
FROM bank_financials
WHERE roe_percent IS NOT NULL
ORDER BY
    fiscal_year,
    roe_rank;


-- ------------------------------------------------------------
-- 6. BANK RANKING BY ROA
-- ------------------------------------------------------------

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roa_percent,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY roa_percent DESC NULLS LAST
    ) AS roa_rank
FROM bank_financials
WHERE roa_percent IS NOT NULL
ORDER BY
    fiscal_year,
    roa_rank;


-- ============================================================
-- END OF SQL 06
-- ============================================================