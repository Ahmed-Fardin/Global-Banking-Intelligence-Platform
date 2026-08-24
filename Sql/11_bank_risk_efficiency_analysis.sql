-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 11 — BANK RISK & EFFICIENCY ANALYSIS
-- ============================================================

-- ============================================================
-- 1. BANK RISK & EFFICIENCY OVERVIEW
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
FROM bank_financials
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
        ORDER BY capital_adequacy_percent DESC NULLS LAST
    ) AS capital_adequacy_rank

FROM bank_financials

WHERE capital_adequacy_percent IS NOT NULL

ORDER BY
    fiscal_year,
    capital_adequacy_rank;


-- ============================================================
-- 3. HIGHEST NPL RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    npl_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY npl_ratio DESC NULLS LAST
    ) AS npl_rank

FROM bank_financials

WHERE npl_ratio IS NOT NULL

ORDER BY
    fiscal_year,
    npl_rank;


-- ============================================================
-- 4. LOWEST COST-TO-INCOME RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    cost_income_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY cost_income_ratio ASC NULLS LAST
    ) AS efficiency_rank

FROM bank_financials

WHERE cost_income_ratio IS NOT NULL

ORDER BY
    fiscal_year,
    efficiency_rank;


-- ============================================================
-- 5. HIGHEST LOAN-TO-DEPOSIT RATIOS
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    loan_to_deposit_ratio,

    RANK() OVER (
        PARTITION BY fiscal_year
        ORDER BY loan_to_deposit_ratio DESC NULLS LAST
    ) AS loan_deposit_rank

FROM bank_financials

WHERE loan_to_deposit_ratio IS NOT NULL

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

FROM bank_financials

WHERE
    capital_adequacy_percent IS NOT NULL
    AND roe_percent IS NOT NULL
    AND roa_percent IS NOT NULL

ORDER BY
    fiscal_year,
    roe_percent DESC;


-- ============================================================
-- 7. PROFITABILITY VS NPL RATIO
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,
    bank_name,
    npl_ratio,
    roe_percent,
    roa_percent,
    net_income

FROM bank_financials

WHERE
    npl_ratio IS NOT NULL
    AND roe_percent IS NOT NULL
    AND roa_percent IS NOT NULL

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

FROM bank_financials

WHERE
    cost_income_ratio IS NOT NULL
    AND roe_percent IS NOT NULL
    AND roa_percent IS NOT NULL

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

FROM bank_financials

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

    FROM bank_financials

    WHERE
        capital_adequacy_percent IS NOT NULL
        AND npl_ratio IS NOT NULL
        AND cost_income_ratio IS NOT NULL
        AND roe_percent IS NOT NULL
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