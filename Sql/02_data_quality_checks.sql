-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- 02 — DATA QUALITY CHECKS
-- ============================================================


-- ============================================================
-- 1. TOTAL FINANCIAL RECORDS
-- ============================================================

SELECT
    COUNT(*) AS financial_records
FROM bank_financials;


-- ============================================================
-- 2. UNIQUE BANKS
-- ============================================================

SELECT
    COUNT(DISTINCT bank_name) AS unique_banks
FROM bank_financials;


-- ============================================================
-- 3. UNIQUE COUNTRIES
-- ============================================================

SELECT
    COUNT(DISTINCT iso3_code) AS unique_countries
FROM bank_financials;


-- ============================================================
-- 4. FISCAL YEAR COVERAGE
-- ============================================================

SELECT
    MIN(fiscal_year) AS first_year,
    MAX(fiscal_year) AS last_year,
    COUNT(DISTINCT fiscal_year) AS year_count
FROM bank_financials;


-- ============================================================
-- 5. RECORDS BY YEAR
-- ============================================================

SELECT
    fiscal_year,
    COUNT(*) AS record_count
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 6. DUPLICATE BANK/YEAR RECORDS
-- ============================================================

SELECT
    iso3_code,
    bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM bank_financials
GROUP BY
    iso3_code,
    bank_name,
    fiscal_year
HAVING COUNT(*) > 1
ORDER BY
    iso3_code,
    bank_name,
    fiscal_year;


-- ============================================================
-- 7. NULL KEY VALUES
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE iso3_code IS NULL
    ) AS null_iso3,

    COUNT(*) FILTER (
        WHERE bank_name IS NULL
    ) AS null_bank_name,

    COUNT(*) FILTER (
        WHERE fiscal_year IS NULL
    ) AS null_fiscal_year
FROM bank_financials;


-- ============================================================
-- 8. BLANK TEXT KEY VALUES
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE TRIM(iso3_code) = ''
    ) AS blank_iso3,

    COUNT(*) FILTER (
        WHERE TRIM(bank_name) = ''
    ) AS blank_bank_name
FROM bank_financials;


-- ============================================================
-- 9. MISSING FINANCIAL VALUES
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE total_assets IS NULL
    ) AS missing_total_assets,

    COUNT(*) FILTER (
        WHERE total_deposits IS NULL
    ) AS missing_total_deposits,

    COUNT(*) FILTER (
        WHERE total_loans IS NULL
    ) AS missing_total_loans,

    COUNT(*) FILTER (
        WHERE shareholders_equity IS NULL
    ) AS missing_shareholders_equity,

    COUNT(*) FILTER (
        WHERE operating_income IS NULL
    ) AS missing_operating_income,

    COUNT(*) FILTER (
        WHERE net_income IS NULL
    ) AS missing_net_income
FROM bank_financials;


-- ============================================================
-- 10. MISSING RATIO VALUES
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE roe_percent IS NULL
    ) AS missing_roe,

    COUNT(*) FILTER (
        WHERE roa_percent IS NULL
    ) AS missing_roa,

    COUNT(*) FILTER (
        WHERE capital_adequacy_percent IS NULL
    ) AS missing_capital_adequacy,

    COUNT(*) FILTER (
        WHERE cost_income_ratio IS NULL
    ) AS missing_cost_income,

    COUNT(*) FILTER (
        WHERE loan_to_deposit_ratio IS NULL
    ) AS missing_loan_to_deposit,

    COUNT(*) FILTER (
        WHERE npl_ratio IS NULL
    ) AS missing_npl
FROM bank_financials;


-- ============================================================
-- 11. MISSING INTEGER VALUES
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE employees IS NULL
    ) AS missing_employees,

    COUNT(*) FILTER (
        WHERE branches IS NULL
    ) AS missing_branches
FROM bank_financials;


-- ============================================================
-- 12. FINANCIAL RECORDS WITHOUT BANK MASTER
-- ============================================================

SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year
FROM bank_financials AS f
LEFT JOIN banks AS b
    ON f.iso3_code = b.iso3_code
   AND f.bank_name = b.bank_name
WHERE b.bank_id IS NULL
ORDER BY
    f.iso3_code,
    f.bank_name,
    f.fiscal_year;


-- ============================================================
-- 13. FINANCIAL RECORDS WITHOUT COUNTRY MASTER
-- ============================================================

SELECT
    f.iso3_code,
    f.bank_name,
    f.fiscal_year
FROM bank_financials AS f
LEFT JOIN countries AS c
    ON f.iso3_code = c.iso3_code
WHERE c.iso3_code IS NULL
ORDER BY
    f.iso3_code,
    f.bank_name,
    f.fiscal_year;