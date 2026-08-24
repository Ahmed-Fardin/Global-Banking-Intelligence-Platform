-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 11 — BANK RISK & EFFICIENCY ANALYSIS
-- ============================================================


-- ============================================================
-- ANALYTICAL SCREENING RANGES
--
-- These are project-level data-quality screening ranges.
-- They are NOT regulatory definitions.
--
-- ROE:                    -100% to 100%
-- ROA:                    -100% to 100%
-- Capital adequacy:         0% to 100%
-- Cost/income:              0% to 200%
-- Loan/deposit:             0% to 500%
-- NPL:                      0% to 100%
-- ============================================================


-- ============================================================
-- 1. VALID RISK & EFFICIENCY OVERVIEW
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    capital_adequacy_percent,
    npl_ratio,
    cost_income_ratio,
    loan_to_deposit_ratio,
    roe_percent,
    roa_percent
FROM bank_financials_usd
WHERE
    capital_adequacy_percent BETWEEN 0 AND 100
    AND npl_ratio BETWEEN 0 AND 100
    AND cost_income_ratio BETWEEN 0 AND 200
    AND loan_to_deposit_ratio BETWEEN 0 AND 500
    AND roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100
ORDER BY
    fiscal_year,
    bank_name;


-- ============================================================
-- 2. STRONGEST CAPITAL ADEQUACY
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    capital_adequacy_percent,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY capital_adequacy_percent DESC
    ) AS capital_adequacy_rank

FROM bank_financials_usd

WHERE
    capital_adequacy_percent BETWEEN 0 AND 100

ORDER BY
    fiscal_year,
    capital_adequacy_rank;


-- ============================================================
-- 3. HIGHEST VALID NPL RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    npl_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY npl_ratio DESC
    ) AS npl_rank

FROM bank_financials_usd

WHERE
    npl_ratio BETWEEN 0 AND 100

ORDER BY
    fiscal_year,
    npl_rank;


-- ============================================================
-- 4. LOWEST VALID COST-TO-INCOME RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    cost_income_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY cost_income_ratio ASC
    ) AS efficiency_rank

FROM bank_financials_usd

WHERE
    cost_income_ratio BETWEEN 0 AND 200

ORDER BY
    fiscal_year,
    efficiency_rank;


-- ============================================================
-- 5. HIGHEST VALID LOAN-TO-DEPOSIT RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    loan_to_deposit_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY loan_to_deposit_ratio DESC
    ) AS loan_deposit_rank

FROM bank_financials_usd

WHERE
    loan_to_deposit_ratio BETWEEN 0 AND 500

ORDER BY
    fiscal_year,
    loan_deposit_rank;


-- ============================================================
-- 6. PROFITABILITY VS CAPITAL ADEQUACY
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    capital_adequacy_percent,
    roe_percent,
    roa_percent

FROM bank_financials_usd

WHERE
    capital_adequacy_percent BETWEEN 0 AND 100
    AND roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100

ORDER BY
    fiscal_year,
    roe_percent DESC;


-- ============================================================
-- 7. PROFITABILITY VS NPL
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    npl_ratio,
    roe_percent,
    roa_percent,
    net_income

FROM bank_financials_usd

WHERE
    npl_ratio BETWEEN 0 AND 100
    AND roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100

ORDER BY
    fiscal_year,
    npl_ratio DESC;


-- ============================================================
-- 8. PROFITABILITY VS EFFICIENCY
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    cost_income_ratio,
    roe_percent,
    roa_percent,
    net_income

FROM bank_financials_usd

WHERE
    cost_income_ratio BETWEEN 0 AND 200
    AND roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100

ORDER BY
    fiscal_year,
    cost_income_ratio ASC;


-- ============================================================
-- 9. RISK & PROFITABILITY SCORECARD
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,

    capital_adequacy_percent,
    npl_ratio,
    cost_income_ratio,
    loan_to_deposit_ratio,
    roe_percent,
    roa_percent,

    CASE
        WHEN capital_adequacy_percent >= 15
            THEN 1
        ELSE 0
    END AS strong_capital_flag,

    CASE
        WHEN npl_ratio <= 5
            THEN 1
        ELSE 0
    END AS low_npl_flag,

    CASE
        WHEN cost_income_ratio <= 60
            THEN 1
        ELSE 0
    END AS efficient_flag,

    CASE
        WHEN roe_percent >= 10
            THEN 1
        ELSE 0
    END AS strong_roe_flag

FROM bank_financials_usd

WHERE
    capital_adequacy_percent BETWEEN 0 AND 100
    AND npl_ratio BETWEEN 0 AND 100
    AND cost_income_ratio BETWEEN 0 AND 200
    AND loan_to_deposit_ratio BETWEEN 0 AND 500
    AND roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100

ORDER BY
    fiscal_year,
    bank_name;


-- ============================================================
-- 10. COMBINED PERFORMANCE SCORE
-- ============================================================

WITH scored_banks AS (

    SELECT
        fiscal_year,
        iso3_code,
        bank_name,

        capital_adequacy_percent,
        npl_ratio,
        cost_income_ratio,
        loan_to_deposit_ratio,
        roe_percent,
        roa_percent,

        CASE
            WHEN capital_adequacy_percent >= 15
                THEN 1
            ELSE 0
        END AS capital_score,

        CASE
            WHEN npl_ratio <= 5
                THEN 1
            ELSE 0
        END AS npl_score,

        CASE
            WHEN cost_income_ratio <= 60
                THEN 1
            ELSE 0
        END AS efficiency_score,

        CASE
            WHEN roe_percent >= 10
                THEN 1
            ELSE 0
        END AS roe_score

    FROM bank_financials_usd

    WHERE
        capital_adequacy_percent BETWEEN 0 AND 100
        AND npl_ratio BETWEEN 0 AND 100
        AND cost_income_ratio BETWEEN 0 AND 200
        AND loan_to_deposit_ratio BETWEEN 0 AND 500
        AND roe_percent BETWEEN -100 AND 100
        AND roa_percent BETWEEN -100 AND 100
)

SELECT
    fiscal_year,
    iso3_code,
    bank_name,

    capital_adequacy_percent,
    npl_ratio,
    cost_income_ratio,
    loan_to_deposit_ratio,
    roe_percent,
    roa_percent,

    capital_score,
    npl_score,
    efficiency_score,
    roe_score,

    (
        capital_score
        + npl_score
        + efficiency_score
        + roe_score
    ) AS performance_score

FROM scored_banks

ORDER BY
    fiscal_year,
    performance_score DESC,
    roe_percent DESC;