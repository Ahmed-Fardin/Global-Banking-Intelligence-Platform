-- ============================================================
-- GLOBAL BANKING INTELLIGENCE
-- SQL 08 — COUNTRY FINANCIAL PERFORMANCE
-- USD MONETARY ANALYSIS
-- ============================================================


-- ============================================================
-- 1. COUNTRY FINANCIAL PERFORMANCE
-- ============================================================

SELECT
    fiscal_year,
    iso3_code,

    COUNT(DISTINCT bank_name)
        AS bank_count,

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
    fiscal_year,
    iso3_code

ORDER BY
    fiscal_year,
    total_assets_usd DESC NULLS LAST;


-- ============================================================
-- 2. COUNTRY NET INCOME RANKING
-- ============================================================

WITH country_performance AS (

    SELECT
        fiscal_year,
        iso3_code,

        SUM(net_income)
            AS total_net_income_usd

    FROM bank_financials_usd

    GROUP BY
        fiscal_year,
        iso3_code
),

ranked_countries AS (

    SELECT
        fiscal_year,
        iso3_code,
        total_net_income_usd,

        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY total_net_income_usd DESC NULLS LAST
        ) AS net_income_rank

    FROM country_performance
)

SELECT
    fiscal_year,
    iso3_code,
    total_net_income_usd,
    net_income_rank
FROM ranked_countries
ORDER BY
    fiscal_year,
    net_income_rank;


-- ============================================================
-- 3. COUNTRY AVERAGE ROE RANKING
-- ============================================================

WITH country_performance AS (

    SELECT
        fiscal_year,
        iso3_code,

        AVG(roe_percent)
            AS average_roe_percent

    FROM bank_financials_usd

    WHERE
        roe_percent IS NOT NULL
        AND roe_percent BETWEEN -100 AND 100

    GROUP BY
        fiscal_year,
        iso3_code
),

ranked_countries AS (

    SELECT
        fiscal_year,
        iso3_code,
        average_roe_percent,

        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY average_roe_percent DESC
        ) AS roe_rank

    FROM country_performance
)

SELECT
    fiscal_year,
    iso3_code,
    average_roe_percent,
    roe_rank
FROM ranked_countries
ORDER BY
    fiscal_year,
    roe_rank;