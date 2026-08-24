-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 09 — GLOBAL BANKING YEARLY TRENDS
-- USD MONETARY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. YEARLY GLOBAL SUMMARY
-- ============================================================

SELECT
    fiscal_year,

    COUNT(DISTINCT bank_name)
        AS bank_count,

    COUNT(DISTINCT iso3_code)
        AS country_count,

    SUM(total_assets)
        AS total_assets_usd,

    SUM(total_deposits)
        AS total_deposits_usd,

    SUM(total_loans)
        AS total_loans_usd,

    SUM(net_income)
        AS total_net_income_usd,

    AVG(roe_percent)
        AS average_roe_percent,

    AVG(roa_percent)
        AS average_roa_percent

FROM bank_financials_usd

GROUP BY
    fiscal_year

ORDER BY
    fiscal_year;


-- ============================================================
-- 2. YEAR-OVER-YEAR NET INCOME CHANGE
-- ============================================================

WITH yearly_data AS (

    SELECT
        fiscal_year,

        SUM(net_income)
            AS total_net_income_usd

    FROM bank_financials_usd

    GROUP BY
        fiscal_year
),

with_previous_year AS (

    SELECT
        fiscal_year,
        total_net_income_usd,

        LAG(total_net_income_usd)
            OVER (
                ORDER BY fiscal_year
            )
            AS previous_year_net_income_usd

    FROM yearly_data
)

SELECT
    fiscal_year,
    total_net_income_usd,
    previous_year_net_income_usd,

    CASE
        WHEN previous_year_net_income_usd IS NULL
            THEN NULL

        WHEN previous_year_net_income_usd = 0
            THEN NULL

        ELSE
            (
                (
                    total_net_income_usd
                    - previous_year_net_income_usd
                )
                /
                ABS(previous_year_net_income_usd)
            ) * 100
    END AS net_income_growth_percent

FROM with_previous_year

ORDER BY
    fiscal_year;


-- ============================================================
-- 3. YEARLY PROFITABILITY / RISK INDICATORS
-- ============================================================

SELECT
    fiscal_year,

    AVG(roe_percent)
        AS average_roe_percent,

    AVG(roa_percent)
        AS average_roa_percent,

    AVG(capital_adequacy_percent)
        AS average_capital_adequacy_percent,

    AVG(cost_income_ratio)
        AS average_cost_income_ratio,

    AVG(loan_to_deposit_ratio)
        AS average_loan_to_deposit_ratio,

    AVG(npl_ratio)
        AS average_npl_ratio

FROM bank_financials_usd

WHERE
    roe_percent BETWEEN -100 AND 100
    AND roa_percent BETWEEN -100 AND 100
    AND capital_adequacy_percent BETWEEN 0 AND 100
    AND cost_income_ratio BETWEEN 0 AND 200
    AND loan_to_deposit_ratio BETWEEN 0 AND 500
    AND npl_ratio BETWEEN 0 AND 100

GROUP BY
    fiscal_year

ORDER BY
    fiscal_year;