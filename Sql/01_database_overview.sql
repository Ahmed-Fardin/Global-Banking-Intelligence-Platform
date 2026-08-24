-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- 01 — DATABASE OVERVIEW
-- ============================================================

-- ============================================================
-- 1. DATABASE
-- ============================================================

SELECT current_database() AS database_name;


-- ============================================================
-- 2. CORE TABLES
-- ============================================================

SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'countries',
      'banks',
      'bank_financials'
  )
ORDER BY table_name;


-- ============================================================
-- 3. TABLE ROW COUNTS
-- ============================================================

SELECT
    'countries' AS table_name,
    COUNT(*) AS row_count
FROM countries

UNION ALL

SELECT
    'banks' AS table_name,
    COUNT(*) AS row_count
FROM banks

UNION ALL

SELECT
    'bank_financials' AS table_name,
    COUNT(*) AS row_count
FROM bank_financials;


-- ============================================================
-- 4. BANK FINANCIAL DATASET OVERVIEW
-- ============================================================

SELECT
    COUNT(*) AS financial_records,
    COUNT(DISTINCT bank_name) AS unique_banks,
    COUNT(DISTINCT iso3_code) AS unique_countries,
    MIN(fiscal_year) AS first_fiscal_year,
    MAX(fiscal_year) AS last_fiscal_year,
    COUNT(DISTINCT fiscal_year) AS fiscal_year_count
FROM bank_financials;


-- ============================================================
-- 5. FINANCIAL RECORDS BY YEAR
-- ============================================================

SELECT
    fiscal_year,
    COUNT(*) AS financial_records,
    COUNT(DISTINCT bank_name) AS unique_banks,
    COUNT(DISTINCT iso3_code) AS unique_countries
FROM bank_financials
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- ============================================================
-- 6. BANK TABLE COLUMNS
-- ============================================================

SELECT
    ordinal_position,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'banks'
ORDER BY ordinal_position;


-- ============================================================
-- 7. BANK FINANCIAL TABLE COLUMNS
-- ============================================================

SELECT
    ordinal_position,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'bank_financials'
ORDER BY ordinal_position;


-- ============================================================
-- 8. EXISTING VIEWS
-- ============================================================

SELECT
    table_schema,
    table_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;