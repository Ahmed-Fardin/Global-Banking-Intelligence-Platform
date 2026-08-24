-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 06 — BANK FINANCIAL RANKINGS
-- USD MONETARY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. TOTAL ASSETS RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_assets,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_assets DESC NULLS LAST
    ) AS asset_rank
FROM bank_financials_usd
WHERE total_assets IS NOT NULL
ORDER BY
    fiscal_year,
    asset_rank;


-- ============================================================
-- 2. TOTAL DEPOSITS RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_deposits,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_deposits DESC NULLS LAST
    ) AS deposit_rank
FROM bank_financials_usd
WHERE total_deposits IS NOT NULL
ORDER BY
    fiscal_year,
    deposit_rank;


-- ============================================================
-- 3. TOTAL LOANS RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    total_loans,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY total_loans DESC NULLS LAST
    ) AS loan_rank
FROM bank_financials_usd
WHERE total_loans IS NOT NULL
ORDER BY
    fiscal_year,
    loan_rank;


-- ============================================================
-- 4. NET INCOME RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    net_income,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY net_income DESC NULLS LAST
    ) AS net_income_rank
FROM bank_financials_usd
WHERE net_income IS NOT NULL
ORDER BY
    fiscal_year,
    net_income_rank;


-- ============================================================
-- 5. ROE RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roe_percent,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY roe_percent DESC NULLS LAST
    ) AS roe_rank
FROM bank_financials_usd
WHERE
    roe_percent IS NOT NULL
    AND roe_percent BETWEEN -100 AND 100
ORDER BY
    fiscal_year,
    roe_rank;


-- ============================================================
-- 6. ROA RANKING
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    roa_percent,
    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY roa_percent DESC NULLS LAST
    ) AS roa_rank
FROM bank_financials_usd
WHERE
    roa_percent IS NOT NULL
    AND roa_percent BETWEEN -100 AND 100
ORDER BY
    fiscal_year,
    roa_rank;