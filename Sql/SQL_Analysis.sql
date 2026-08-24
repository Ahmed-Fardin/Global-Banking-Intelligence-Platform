-- GBIP SQL Analysis
-- Global Banking Intelligence Platform
-- Analysis period 2020 to 2025
-- PostgreSQL analysis and validation

-- Main financial table
-- public.bank_financials_usd
-- USD values are used for cross country monetary comparisons

-- 01 Bank Rankings

-- Question 1
-- Which banks have the highest total assets in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        total_assets,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY total_assets DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    total_assets
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- Question 2
-- Which banks have the highest total deposits in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        total_deposits,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY total_deposits DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    total_deposits
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- Question 3
-- Which banks have the highest total loans in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        total_loans,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY total_loans DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    total_loans
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- Question 4
-- Which banks have the highest net income in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        net_income,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY net_income DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    net_income
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- Question 5
-- Which banks have the highest ROE in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        roe_percent,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY roe_percent DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    roe_percent
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- Question 6
-- Which banks have the highest ROA in each year

WITH ranked AS (
    SELECT
        fiscal_year,
        bank_name,
        iso3_code,
        roa_percent,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY roa_percent DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    fiscal_year,
    bank_rank,
    bank_name,
    iso3_code,
    roa_percent
FROM ranked
WHERE bank_rank <= 10
ORDER BY fiscal_year, bank_rank;


-- 02 Bank Profitability

-- Question 1
-- Which banks are the most profitable

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    net_income,
    roe_percent,
    roa_percent
FROM public.bank_financials_usd
ORDER BY net_income DESC
LIMIT 20;


-- Question 2
-- Which banks generate the highest net income

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    net_income
FROM public.bank_financials_usd
ORDER BY net_income DESC
LIMIT 20;


-- Question 3
-- Which banks have the highest ROE

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roe_percent
FROM public.bank_financials_usd
ORDER BY roe_percent DESC
LIMIT 20;


-- Question 4
-- Which banks have the highest ROA

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roa_percent
FROM public.bank_financials_usd
ORDER BY roa_percent DESC
LIMIT 20;


-- Question 5
-- Which banks consistently appear among the top performers

WITH yearly_rank AS (
    SELECT
        fiscal_year,
        bank_name,
        net_income,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY net_income DESC
        ) AS bank_rank
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    COUNT(*) AS years_in_top_10,
    MIN(bank_rank) AS best_rank,
    AVG(bank_rank) AS average_rank
FROM yearly_rank
WHERE bank_rank <= 10
GROUP BY bank_name
ORDER BY years_in_top_10 DESC, average_rank;


-- 03 Country Financial Performance

-- Question 1
-- How many banks are represented in each country

SELECT
    iso3_code,
    COUNT(DISTINCT bank_name) AS bank_count
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY bank_count DESC;


-- Question 2
-- What are the total assets of banks in each country

SELECT
    iso3_code,
    SUM(total_assets) AS total_assets_usd
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY total_assets_usd DESC;


-- Question 3
-- What are the total deposits of banks in each country

SELECT
    iso3_code,
    SUM(total_deposits) AS total_deposits_usd
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY total_deposits_usd DESC;


-- Question 4
-- What are the total loans of banks in each country

SELECT
    iso3_code,
    SUM(total_loans) AS total_loans_usd
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY total_loans_usd DESC;


-- Question 5
-- What is the total net income of banks in each country

SELECT
    iso3_code,
    SUM(net_income) AS total_net_income_usd
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY total_net_income_usd DESC;


-- Question 6
-- What is the average ROE of banks in each country

SELECT
    iso3_code,
    ROUND(AVG(roe_percent), 2) AS average_roe
FROM public.bank_financials_usd
GROUP BY iso3_code
ORDER BY average_roe DESC;


-- Question 7
-- Which countries rank highest by bank net income

WITH country_income AS (
    SELECT
        iso3_code,
        SUM(net_income) AS total_net_income_usd
    FROM public.bank_financials_usd
    GROUP BY iso3_code
)
SELECT
    RANK() OVER (
        ORDER BY total_net_income_usd DESC
    ) AS country_rank,
    iso3_code,
    total_net_income_usd
FROM country_income
ORDER BY country_rank;


-- 04 Global Banking Trends

-- Question 1
-- How does the banking dataset change from 2020 to 2025

SELECT
    fiscal_year,
    COUNT(DISTINCT bank_name) AS banks,
    COUNT(DISTINCT iso3_code) AS countries
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 2
-- How do total assets change over time

SELECT
    fiscal_year,
    SUM(total_assets) AS total_assets_usd
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 3
-- How do total deposits change over time

SELECT
    fiscal_year,
    SUM(total_deposits) AS total_deposits_usd
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 4
-- How do total loans change over time

SELECT
    fiscal_year,
    SUM(total_loans) AS total_loans_usd
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 5
-- How does total net income change over time

SELECT
    fiscal_year,
    SUM(net_income) AS total_net_income_usd
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 6
-- How does average ROE change over time

SELECT
    fiscal_year,
    ROUND(AVG(roe_percent), 2) AS average_roe
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 7
-- How does average ROA change over time

SELECT
    fiscal_year,
    ROUND(AVG(roa_percent), 2) AS average_roa
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 8
-- What is the year over year change in total net income

WITH yearly AS (
    SELECT
        fiscal_year,
        SUM(net_income) AS total_net_income_usd
    FROM public.bank_financials_usd
    GROUP BY fiscal_year
)
SELECT
    fiscal_year,
    total_net_income_usd,
    LAG(total_net_income_usd) OVER (
        ORDER BY fiscal_year
    ) AS previous_year_net_income_usd,
    total_net_income_usd
        - LAG(total_net_income_usd) OVER (
            ORDER BY fiscal_year
        ) AS change_usd,
    ROUND(
        (
            total_net_income_usd
            / NULLIF(
                LAG(total_net_income_usd) OVER (
                    ORDER BY fiscal_year
                ),
                0
            ) - 1
        ) * 100,
        2
    ) AS change_percent
FROM yearly
ORDER BY fiscal_year;


-- 05 Bank Growth

-- Question 1
-- Which banks have the highest asset growth

WITH bank_years AS (
    SELECT
        bank_name,
        iso3_code,
        fiscal_year,
        total_assets,
        LAG(total_assets) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_assets
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    previous_assets,
    ROUND(
        (total_assets / NULLIF(previous_assets, 0) - 1) * 100,
        2
    ) AS asset_growth_percent
FROM bank_years
WHERE previous_assets IS NOT NULL
ORDER BY asset_growth_percent DESC
LIMIT 20;


-- Question 2
-- Which banks have the highest loan growth

WITH bank_years AS (
    SELECT
        bank_name,
        iso3_code,
        fiscal_year,
        total_loans,
        LAG(total_loans) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_loans
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_loans,
    previous_loans,
    ROUND(
        (total_loans / NULLIF(previous_loans, 0) - 1) * 100,
        2
    ) AS loan_growth_percent
FROM bank_years
WHERE previous_loans IS NOT NULL
ORDER BY loan_growth_percent DESC
LIMIT 20;


-- Question 3
-- Which banks have the highest net income growth

WITH bank_years AS (
    SELECT
        bank_name,
        iso3_code,
        fiscal_year,
        net_income,
        LAG(net_income) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_net_income
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    net_income,
    previous_net_income,
    ROUND(
        (net_income / NULLIF(previous_net_income, 0) - 1) * 100,
        2
    ) AS net_income_growth_percent
FROM bank_years
WHERE previous_net_income IS NOT NULL
ORDER BY net_income_growth_percent DESC
LIMIT 20;


-- Question 4
-- How has each banks financial position changed over time

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    total_deposits,
    total_loans,
    net_income,
    roe_percent,
    roa_percent
FROM public.bank_financials_usd
ORDER BY bank_name, fiscal_year;


-- Question 5
-- Which banks show sustained growth across multiple years

WITH growth AS (
    SELECT
        bank_name,
        fiscal_year,
        total_assets,
        LAG(total_assets) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_assets
    FROM public.bank_financials_usd
),
positive_growth AS (
    SELECT
        bank_name,
        fiscal_year
    FROM growth
    WHERE previous_assets IS NOT NULL
      AND total_assets > previous_assets
)
SELECT
    bank_name,
    COUNT(*) AS years_with_asset_growth
FROM positive_growth
GROUP BY bank_name
HAVING COUNT(*) >= 3
ORDER BY years_with_asset_growth DESC;


-- 06 Bank Risk and Efficiency

-- Question 1
-- Which banks have the strongest capital adequacy

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    capital_adequacy_percent
FROM public.bank_financials_usd
ORDER BY capital_adequacy_percent DESC
LIMIT 20;


-- Question 2
-- Which banks have the highest NPL ratios

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    npl_ratio
FROM public.bank_financials_usd
ORDER BY npl_ratio DESC
LIMIT 20;


-- Question 3
-- Which banks have the lowest cost to income ratios

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    cost_income_ratio
FROM public.bank_financials_usd
WHERE cost_income_ratio IS NOT NULL
ORDER BY cost_income_ratio ASC
LIMIT 20;


-- Question 4
-- Which banks have high loan to deposit ratios

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    loan_to_deposit_ratio
FROM public.bank_financials_usd
ORDER BY loan_to_deposit_ratio DESC
LIMIT 20;


-- Question 5
-- How does capital adequacy relate to profitability

SELECT
    ROUND(AVG(capital_adequacy_percent), 2) AS average_capital_adequacy,
    ROUND(AVG(roe_percent), 2) AS average_roe,
    ROUND(AVG(roa_percent), 2) AS average_roa
FROM public.bank_financials_usd;


-- Question 6
-- How does NPL performance relate to profitability

SELECT
    ROUND(AVG(npl_ratio), 2) AS average_npl,
    ROUND(AVG(roe_percent), 2) AS average_roe,
    ROUND(AVG(roa_percent), 2) AS average_roa
FROM public.bank_financials_usd;


-- Question 7
-- Which banks combine strong profitability with strong risk indicators

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    net_income,
    roe_percent,
    roa_percent,
    npl_ratio,
    capital_adequacy_percent,
    cost_income_ratio
FROM public.bank_financials_usd
WHERE roe_percent >= (
        SELECT PERCENTILE_CONT(0.75)
        WITHIN GROUP (ORDER BY roe_percent)
        FROM public.bank_financials_usd
    )
  AND npl_ratio <= (
        SELECT PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY npl_ratio)
        FROM public.bank_financials_usd
    )
  AND capital_adequacy_percent >= (
        SELECT PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY capital_adequacy_percent)
        FROM public.bank_financials_usd
    )
ORDER BY roe_percent DESC;


-- Question 8
-- Which banks show concerning combinations of profitability efficiency and risk

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roe_percent,
    roa_percent,
    npl_ratio,
    capital_adequacy_percent,
    cost_income_ratio,
    loan_to_deposit_ratio
FROM public.bank_financials_usd
WHERE npl_ratio >= (
        SELECT PERCENTILE_CONT(0.90)
        WITHIN GROUP (ORDER BY npl_ratio)
        FROM public.bank_financials_usd
    )
   OR capital_adequacy_percent <= (
        SELECT PERCENTILE_CONT(0.10)
        WITHIN GROUP (ORDER BY capital_adequacy_percent)
        FROM public.bank_financials_usd
    )
   OR cost_income_ratio >= (
        SELECT PERCENTILE_CONT(0.90)
        WITHIN GROUP (ORDER BY cost_income_ratio)
        FROM public.bank_financials_usd
    )
   OR loan_to_deposit_ratio >= (
        SELECT PERCENTILE_CONT(0.90)
        WITHIN GROUP (ORDER BY loan_to_deposit_ratio)
        FROM public.bank_financials_usd
    )
ORDER BY npl_ratio DESC;


-- 07 Data Quality Checks

-- Question 1
-- Which records have shareholders equity greater than total assets

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    shareholders_equity,
    total_assets
FROM public.bank_financials_usd
WHERE shareholders_equity > total_assets
ORDER BY shareholders_equity - total_assets DESC;


-- Question 2
-- Which records have missing key financial values

SELECT
    bank_name,
    iso3_code,
    fiscal_year
FROM public.bank_financials_usd
WHERE total_assets IS NULL
   OR total_deposits IS NULL
   OR total_loans IS NULL
   OR net_income IS NULL
ORDER BY fiscal_year, bank_name;


-- Question 3
-- Which banks have duplicate bank year records

SELECT
    bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.bank_financials_usd
GROUP BY bank_name, fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC, bank_name, fiscal_year;


-- 07 Data Quality Checks

-- This section documents the deeper validation performed on the PostgreSQL
-- financial dataset before it was used by Power BI.


-- Question 1
-- Are there duplicate records when bank names are compared without case differences

SELECT
    LOWER(TRIM(bank_name)) AS normalized_bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.bank_financials_usd
GROUP BY LOWER(TRIM(bank_name)), fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC;


-- Question 2
-- Are there bank names with leading or trailing spaces

SELECT DISTINCT
    bank_name
FROM public.bank_financials_usd
WHERE bank_name <> TRIM(bank_name)
ORDER BY bank_name;


-- Question 3
-- Are there country codes with incorrect length

SELECT DISTINCT
    iso3_code
FROM public.bank_financials_usd
WHERE iso3_code IS NOT NULL
  AND LENGTH(TRIM(iso3_code)) <> 3
ORDER BY iso3_code;


-- Question 4
-- Are country codes stored in inconsistent case

SELECT DISTINCT
    iso3_code
FROM public.bank_financials_usd
WHERE iso3_code IS NOT NULL
  AND iso3_code <> UPPER(iso3_code)
ORDER BY iso3_code;


-- Question 5
-- Are there blank text values that should be treated as missing values

SELECT
    COUNT(*) FILTER (WHERE TRIM(bank_name) = '') AS blank_bank_names,
    COUNT(*) FILTER (WHERE TRIM(iso3_code) = '') AS blank_country_codes,
    COUNT(*) FILTER (WHERE TRIM(reporting_currency) = '') AS blank_currencies,
    COUNT(*) FILTER (WHERE TRIM(source) = '') AS blank_sources
FROM public.bank_financials_usd;


-- Question 6
-- How many distinct values exist for the main categorical fields

SELECT
    COUNT(DISTINCT bank_name) AS banks,
    COUNT(DISTINCT iso3_code) AS countries,
    COUNT(DISTINCT fiscal_year) AS years,
    COUNT(DISTINCT reporting_currency) AS currencies,
    COUNT(DISTINCT source) AS sources
FROM public.bank_financials_usd;


-- Question 7
-- Are the same bank names associated with multiple countries

SELECT
    bank_name,
    COUNT(DISTINCT iso3_code) AS country_count,
    ARRAY_AGG(DISTINCT iso3_code ORDER BY iso3_code) AS country_codes
FROM public.bank_financials_usd
GROUP BY bank_name
HAVING COUNT(DISTINCT iso3_code) > 1
ORDER BY country_count DESC, bank_name;


-- Question 8
-- Are the same bank names associated with multiple reporting currencies

SELECT
    bank_name,
    COUNT(DISTINCT reporting_currency) AS currency_count,
    ARRAY_AGG(DISTINCT reporting_currency ORDER BY reporting_currency) AS currencies
FROM public.bank_financials_usd
WHERE reporting_currency IS NOT NULL
GROUP BY bank_name
HAVING COUNT(DISTINCT reporting_currency) > 1
ORDER BY currency_count DESC, bank_name;


-- Question 9
-- Are banks associated with more than one fiscal year record for the same year

SELECT
    bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.bank_financials_usd
GROUP BY bank_name, fiscal_year
HAVING COUNT(*) > 1
ORDER BY bank_name, fiscal_year;


-- Question 10
-- Are there gaps inside a bank's available year sequence

WITH years AS (
    SELECT
        bank_name,
        fiscal_year,
        LAG(fiscal_year) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_year
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    previous_year,
    fiscal_year,
    fiscal_year - previous_year AS year_gap
FROM years
WHERE previous_year IS NOT NULL
  AND fiscal_year - previous_year > 1
ORDER BY year_gap DESC, bank_name;


-- Question 11
-- Are there records where the reporting year is earlier than the bank founding year

SELECT
    bank_name,
    fiscal_year,
    founded_year
FROM public.bank_financials_usd
WHERE founded_year IS NOT NULL
  AND fiscal_year < founded_year
ORDER BY fiscal_year, bank_name;


-- Question 12
-- Are founded years outside a reasonable historical range

SELECT
    bank_name,
    founded_year
FROM public.bank_financials_usd
WHERE founded_year IS NOT NULL
  AND (
      founded_year < 1000
      OR founded_year > EXTRACT(YEAR FROM CURRENT_DATE)
  )
ORDER BY founded_year, bank_name;


-- Question 13
-- Are employee counts negative

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    employees
FROM public.bank_financials_usd
WHERE employees < 0
ORDER BY employees, bank_name;


-- Question 14
-- Are branch counts negative

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    branches
FROM public.bank_financials_usd
WHERE branches < 0
ORDER BY branches, bank_name;


-- Question 15
-- Are financial amounts recorded with unexpected negative values

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    total_deposits,
    total_loans,
    shareholders_equity,
    operating_income,
    net_income
FROM public.bank_financials_usd
WHERE total_assets < 0
   OR total_deposits < 0
   OR total_loans < 0
   OR shareholders_equity < 0
   OR operating_income < 0
ORDER BY fiscal_year, bank_name;


-- Question 16
-- Are net income values negative

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    net_income
FROM public.bank_financials_usd
WHERE net_income < 0
ORDER BY net_income, bank_name;


-- Question 17
-- Are operating income values negative

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    operating_income
FROM public.bank_financials_usd
WHERE operating_income < 0
ORDER BY operating_income, bank_name;


-- Question 18
-- Are deposits and loans both zero while assets are positive

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    total_deposits,
    total_loans
FROM public.bank_financials_usd
WHERE total_assets > 0
  AND total_deposits = 0
  AND total_loans = 0
ORDER BY total_assets DESC;


-- Question 19
-- Are shareholders equity values zero while assets are positive

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    shareholders_equity
FROM public.bank_financials_usd
WHERE total_assets > 0
  AND shareholders_equity = 0
ORDER BY total_assets DESC;


-- Question 20
-- Does the basic accounting relationship between assets and equity look plausible

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    shareholders_equity,
    total_assets - shareholders_equity AS liabilities_plus_other_assets_gap
FROM public.bank_financials_usd
WHERE shareholders_equity > total_assets
ORDER BY shareholders_equity - total_assets DESC;


-- Question 21
-- Are deposits unusually close to or greater than total assets

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    total_deposits,
    ROUND(
        total_deposits / NULLIF(total_assets, 0) * 100,
        2
    ) AS deposits_to_assets_percent
FROM public.bank_financials_usd
WHERE total_assets > 0
  AND total_deposits / NULLIF(total_assets, 0) > 1
ORDER BY deposits_to_assets_percent DESC;


-- Question 22
-- Are loans unusually large compared with total assets

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    total_assets,
    total_loans,
    ROUND(
        total_loans / NULLIF(total_assets, 0) * 100,
        2
    ) AS loans_to_assets_percent
FROM public.bank_financials_usd
WHERE total_assets > 0
  AND total_loans / NULLIF(total_assets, 0) > 1
ORDER BY loans_to_assets_percent DESC;


-- Question 23
-- Do stored ROA values closely match the calculated ROA

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roa_percent,
    ROUND(
        net_income / NULLIF(total_assets, 0) * 100,
        2
    ) AS calculated_roa,
    ROUND(
        roa_percent
        - (net_income / NULLIF(total_assets, 0) * 100),
        2
    ) AS difference
FROM public.bank_financials_usd
WHERE total_assets > 0
ORDER BY ABS(
    roa_percent
    - (net_income / NULLIF(total_assets, 0) * 100)
) DESC;


-- Question 24
-- Do stored ROE values closely match the calculated ROE

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roe_percent,
    ROUND(
        net_income / NULLIF(shareholders_equity, 0) * 100,
        2
    ) AS calculated_roe,
    ROUND(
        roe_percent
        - (net_income / NULLIF(shareholders_equity, 0) * 100),
        2
    ) AS difference
FROM public.bank_financials_usd
WHERE shareholders_equity > 0
ORDER BY ABS(
    roe_percent
    - (net_income / NULLIF(shareholders_equity, 0) * 100)
) DESC;


-- Question 25
-- Do stored loan to deposit ratios closely match the calculated ratio

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    loan_to_deposit_ratio,
    ROUND(
        total_loans / NULLIF(total_deposits, 0) * 100,
        2
    ) AS calculated_ratio,
    ROUND(
        loan_to_deposit_ratio
        - (total_loans / NULLIF(total_deposits, 0) * 100),
        2
    ) AS difference
FROM public.bank_financials_usd
WHERE total_deposits > 0
ORDER BY ABS(
    loan_to_deposit_ratio
    - (total_loans / NULLIF(total_deposits, 0) * 100)
) DESC;


-- Question 26
-- Are cost to income ratios outside a plausible percentage range

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    cost_income_ratio
FROM public.bank_financials_usd
WHERE cost_income_ratio < 0
   OR cost_income_ratio > 500
ORDER BY cost_income_ratio DESC;


-- Question 27
-- Are capital adequacy values negative or unusually high

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    capital_adequacy_percent
FROM public.bank_financials_usd
WHERE capital_adequacy_percent < 0
   OR capital_adequacy_percent > 100
ORDER BY capital_adequacy_percent DESC;


-- Question 28
-- Are NPL ratios negative or above 100 percent

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    npl_ratio
FROM public.bank_financials_usd
WHERE npl_ratio < 0
   OR npl_ratio > 100
ORDER BY npl_ratio DESC;


-- Question 29
-- Are ROA values unusually high

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roa_percent
FROM public.bank_financials_usd
WHERE ABS(roa_percent) > 20
ORDER BY ABS(roa_percent) DESC;


-- Question 30
-- Are ROE values unusually high

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    roe_percent
FROM public.bank_financials_usd
WHERE ABS(roe_percent) > 100
ORDER BY ABS(roe_percent) DESC;


-- Question 31
-- Are employee counts unusually high or low compared with bank assets

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    employees,
    total_assets,
    ROUND(
        total_assets / NULLIF(employees, 0),
        2
    ) AS assets_per_employee
FROM public.bank_financials_usd
WHERE employees > 0
ORDER BY assets_per_employee DESC;


-- Question 32
-- Are branch counts unusually high or low compared with bank size

SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    branches,
    total_assets,
    ROUND(
        total_assets / NULLIF(branches, 0),
        2
    ) AS assets_per_branch
FROM public.bank_financials_usd
WHERE branches > 0
ORDER BY assets_per_branch DESC;


-- Question 33
-- Which banks have extreme asset changes between consecutive years

WITH yearly AS (
    SELECT
        bank_name,
        iso3_code,
        fiscal_year,
        total_assets,
        LAG(total_assets) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_assets
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    previous_assets,
    total_assets,
    ROUND(
        (total_assets / NULLIF(previous_assets, 0) - 1) * 100,
        2
    ) AS asset_growth_percent
FROM yearly
WHERE previous_assets IS NOT NULL
  AND ABS(
      (total_assets / NULLIF(previous_assets, 0) - 1) * 100
  ) > 100
ORDER BY ABS(
    (total_assets / NULLIF(previous_assets, 0) - 1) * 100
) DESC;


-- Question 34
-- Which banks have extreme net income changes between consecutive years

WITH yearly AS (
    SELECT
        bank_name,
        iso3_code,
        fiscal_year,
        net_income,
        LAG(net_income) OVER (
            PARTITION BY bank_name
            ORDER BY fiscal_year
        ) AS previous_net_income
    FROM public.bank_financials_usd
)
SELECT
    bank_name,
    iso3_code,
    fiscal_year,
    previous_net_income,
    net_income,
    ROUND(
        (net_income / NULLIF(previous_net_income, 0) - 1) * 100,
        2
    ) AS net_income_growth_percent
FROM yearly
WHERE previous_net_income IS NOT NULL
  AND previous_net_income <> 0
  AND ABS(
      (net_income / NULLIF(previous_net_income, 0) - 1) * 100
  ) > 200
ORDER BY ABS(
    (net_income / NULLIF(previous_net_income, 0) - 1) * 100
) DESC;


-- Question 35
-- Do banks have a single reporting currency across all annual records

SELECT
    bank_name,
    COUNT(DISTINCT reporting_currency) AS currency_count,
    ARRAY_AGG(DISTINCT reporting_currency ORDER BY reporting_currency) AS currencies
FROM public.bank_financials_usd
GROUP BY bank_name
HAVING COUNT(DISTINCT reporting_currency) > 1
ORDER BY currency_count DESC;


-- Question 36
-- Are source fields consistent for the same bank and year

SELECT
    bank_name,
    fiscal_year,
    COUNT(DISTINCT source) AS source_count,
    ARRAY_AGG(DISTINCT source ORDER BY source) AS sources
FROM public.bank_financials_usd
GROUP BY bank_name, fiscal_year
HAVING COUNT(DISTINCT source) > 1
ORDER BY source_count DESC;


-- Question 37
-- Are SWIFT codes inconsistent for the same bank

SELECT
    bank_name,
    COUNT(DISTINCT swift_code) AS swift_code_count,
    ARRAY_AGG(DISTINCT swift_code ORDER BY swift_code) AS swift_codes
FROM public.bank_financials_usd
WHERE swift_code IS NOT NULL
GROUP BY bank_name
HAVING COUNT(DISTINCT swift_code) > 1
ORDER BY swift_code_count DESC;


-- Question 38
-- Are SWIFT codes missing for banks that otherwise have records

SELECT
    bank_name,
    iso3_code,
    COUNT(*) AS records,
    COUNT(swift_code) AS records_with_swift
FROM public.bank_financials_usd
GROUP BY bank_name, iso3_code
HAVING COUNT(swift_code) = 0
ORDER BY bank_name;


-- Question 39
-- Are official websites missing

SELECT
    bank_name,
    iso3_code,
    COUNT(*) AS records,
    COUNT(official_website) AS records_with_website
FROM public.bank_financials_usd
GROUP BY bank_name, iso3_code
HAVING COUNT(official_website) = 0
ORDER BY bank_name;


-- Question 40
-- Are active status values consistent for the same bank

SELECT
    bank_name,
    COUNT(DISTINCT is_active) AS active_status_count,
    ARRAY_AGG(DISTINCT is_active ORDER BY is_active) AS active_status_values
FROM public.bank_financials_usd
GROUP BY bank_name
HAVING COUNT(DISTINCT is_active) > 1
ORDER BY bank_name;


-- Question 41
-- Are bank types consistent for the same bank

SELECT
    bank_name,
    COUNT(DISTINCT bank_type) AS bank_type_count,
    ARRAY_AGG(DISTINCT bank_type ORDER BY bank_type) AS bank_types
FROM public.bank_financials_usd
GROUP BY bank_name
HAVING COUNT(DISTINCT bank_type) > 1
ORDER BY bank_name;


-- Question 42
-- Are bank ranks duplicated within the same country and year

SELECT
    iso3_code,
    fiscal_year,
    bank_rank,
    COUNT(*) AS bank_count
FROM public.bank_financials_usd
WHERE bank_rank IS NOT NULL
GROUP BY iso3_code, fiscal_year, bank_rank
HAVING COUNT(*) > 1
ORDER BY fiscal_year, iso3_code, bank_rank;


-- Question 43
-- Are bank ranks missing for some records

SELECT
    fiscal_year,
    COUNT(*) AS total_records,
    COUNT(bank_rank) AS records_with_rank,
    COUNT(*) - COUNT(bank_rank) AS records_without_rank
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;


-- Question 44
-- Does the bank dimension contain duplicate bank names

SELECT
    bank_name,
    COUNT(*) AS record_count
FROM public."DimBank"
GROUP BY bank_name
HAVING COUNT(*) > 1
ORDER BY record_count DESC, bank_name;


-- Question 45
-- Does the country dimension contain duplicate ISO3 codes

SELECT
    iso3_code,
    COUNT(*) AS record_count
FROM public."DimCountry"
GROUP BY iso3_code
HAVING COUNT(*) > 1
ORDER BY record_count DESC, iso3_code;


-- Question 46
-- Does the year dimension contain duplicate fiscal years

SELECT
    fiscal_year,
    COUNT(*) AS record_count
FROM public."DimYear"
GROUP BY fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC, fiscal_year;


-- Question 47
-- Are all financial years represented in the year dimension

SELECT DISTINCT
    f.fiscal_year
FROM public.bank_financials_usd f
LEFT JOIN public."DimYear" y
    ON y.fiscal_year = f.fiscal_year
WHERE y.fiscal_year IS NULL
ORDER BY f.fiscal_year;


-- Question 48
-- Are all financial banks represented in the bank dimension

SELECT DISTINCT
    f.bank_name
FROM public.bank_financials_usd f
LEFT JOIN public."DimBank" b
    ON LOWER(TRIM(b.bank_name)) = LOWER(TRIM(f.bank_name))
WHERE b.bank_name IS NULL
ORDER BY f.bank_name;


-- Question 49
-- Are all financial countries represented in the country dimension

SELECT DISTINCT
    f.iso3_code
FROM public.bank_financials_usd f
LEFT JOIN public."DimCountry" c
    ON UPPER(TRIM(c.iso3_code)) = UPPER(TRIM(f.iso3_code))
WHERE c.iso3_code IS NULL
ORDER BY f.iso3_code;


-- Question 50
-- Is the final USD dataset internally consistent across years

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT bank_name) AS banks,
    COUNT(DISTINCT iso3_code) AS countries,
    COUNT(DISTINCT fiscal_year) AS years,
    COUNT(*) FILTER (
        WHERE total_assets IS NULL
           OR total_deposits IS NULL
           OR total_loans IS NULL
           OR net_income IS NULL
    ) AS incomplete_core_records,
    COUNT(*) FILTER (
        WHERE total_assets <= 0
           OR total_deposits < 0
           OR total_loans < 0
    ) AS invalid_core_values,
    COUNT(*) FILTER (
        WHERE fiscal_year < 2020
           OR fiscal_year > 2025
    ) AS invalid_year_records
FROM public.bank_financials_usd;


-- 07A Data Quality Summary

-- Question 1
-- How many records pass the main quality conditions

SELECT
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE bank_name IS NOT NULL
          AND TRIM(bank_name) <> ''
          AND iso3_code IS NOT NULL
          AND LENGTH(TRIM(iso3_code)) = 3
          AND fiscal_year BETWEEN 2020 AND 2025
          AND total_assets > 0
          AND total_deposits >= 0
          AND total_loans >= 0
    ) AS records_passing_core_checks,
    COUNT(*) FILTER (
        WHERE bank_name IS NULL
           OR TRIM(bank_name) = ''
           OR iso3_code IS NULL
           OR LENGTH(TRIM(iso3_code)) <> 3
           OR fiscal_year NOT BETWEEN 2020 AND 2025
           OR total_assets <= 0
           OR total_deposits < 0
           OR total_loans < 0
    ) AS records_failing_core_checks
FROM public.bank_financials_usd;


-- Question 2
-- What percentage of records pass the core validation rules

SELECT
    ROUND(
        COUNT(*) FILTER (
            WHERE bank_name IS NOT NULL
              AND TRIM(bank_name) <> ''
              AND iso3_code IS NOT NULL
              AND LENGTH(TRIM(iso3_code)) = 3
              AND fiscal_year BETWEEN 2020 AND 2025
              AND total_assets > 0
              AND total_deposits >= 0
              AND total_loans >= 0
        )::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS core_data_quality_pass_rate
FROM public.bank_financials_usd;


-- Question 3
-- Which banks require the most data quality attention

WITH issues AS (
    SELECT
        bank_name,
        iso3_code,
        SUM(
            CASE WHEN bank_name IS NULL OR TRIM(bank_name) = '' THEN 1 ELSE 0 END
        ) AS missing_bank_name,
        SUM(
            CASE WHEN iso3_code IS NULL OR LENGTH(TRIM(iso3_code)) <> 3 THEN 1 ELSE 0 END
        ) AS invalid_country_code,
        SUM(
            CASE WHEN fiscal_year NOT BETWEEN 2020 AND 2025 THEN 1 ELSE 0 END
        ) AS invalid_year,
        SUM(
            CASE WHEN total_assets IS NULL OR total_assets <= 0 THEN 1 ELSE 0 END
        ) AS invalid_assets,
        SUM(
            CASE WHEN total_deposits IS NULL OR total_deposits < 0 THEN 1 ELSE 0 END
        ) AS invalid_deposits,
        SUM(
            CASE WHEN total_loans IS NULL OR total_loans < 0 THEN 1 ELSE 0 END
        ) AS invalid_loans
    FROM public.bank_financials_usd
    GROUP BY bank_name, iso3_code
)
SELECT
    bank_name,
    iso3_code,
    missing_bank_name,
    invalid_country_code,
    invalid_year,
    invalid_assets,
    invalid_deposits,
    invalid_loans,
    missing_bank_name
      + invalid_country_code
      + invalid_year
      + invalid_assets
      + invalid_deposits
      + invalid_loans AS total_issues
FROM issues
WHERE missing_bank_name
      + invalid_country_code
      + invalid_year
      + invalid_assets
      + invalid_deposits
      + invalid_loans > 0
ORDER BY total_issues DESC, bank_name;

-- 08 PostgreSQL Views
-- Views were used to create reusable analytical layers for Power BI.

-- Question 1
-- Which analytical views exist in the public schema

SELECT
    table_schema,
    table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- Question 2
-- What SQL definitions are stored behind the analytical views

SELECT
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;

-- Question 3
-- What tables are used by the GBIP analytical views

SELECT
    view_schema,
    view_name,
    table_schema,
    table_name
FROM information_schema.view_table_usage
WHERE view_schema = 'public'
ORDER BY view_name, table_name;

-- Question 4
-- Which project views are available for bank financial analysis

SELECT
    table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name IN (
      'vw_bank_financial_performance',
      'vw_bank_yearly_performance',
      'vw_country_financial_summary',
      'vw_global_banking_yearly_summary',
      'vw_latest_bank_financials'
  )
ORDER BY table_name;

-- Question 5
-- Does the latest bank financial view contain one record per bank

SELECT
    bank_name,
    COUNT(*) AS record_count
FROM public.vw_latest_bank_financials
GROUP BY bank_name
HAVING COUNT(*) > 1
ORDER BY record_count DESC, bank_name;

-- Question 6
-- Does the yearly bank performance view contain one record per bank and year

SELECT
    bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.vw_bank_yearly_performance
GROUP BY bank_name, fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC, bank_name, fiscal_year;

-- Question 7
-- Does the country financial summary contain one record per country and year

SELECT
    iso3_code,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.vw_country_financial_summary
GROUP BY iso3_code, fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC;

-- Question 8
-- Does the global yearly summary contain one record per year

SELECT
    fiscal_year,
    COUNT(*) AS record_count
FROM public.vw_global_banking_yearly_summary
GROUP BY fiscal_year
HAVING COUNT(*) > 1
ORDER BY fiscal_year;

-- Question 9
-- Does the bank financial performance view contain duplicate bank year records

SELECT
    bank_name,
    fiscal_year,
    COUNT(*) AS record_count
FROM public.vw_bank_financial_performance
GROUP BY bank_name, fiscal_year
HAVING COUNT(*) > 1
ORDER BY record_count DESC, bank_name, fiscal_year;

-- Question 10
-- How many rows are available in each main analytical view

SELECT 'vw_bank_financial_performance' AS view_name,
       COUNT(*) AS row_count
FROM public.vw_bank_financial_performance
UNION ALL
SELECT 'vw_bank_yearly_performance', COUNT(*)
FROM public.vw_bank_yearly_performance
UNION ALL
SELECT 'vw_country_financial_summary', COUNT(*)
FROM public.vw_country_financial_summary
UNION ALL
SELECT 'vw_global_banking_yearly_summary', COUNT(*)
FROM public.vw_global_banking_yearly_summary
UNION ALL
SELECT 'vw_latest_bank_financials', COUNT(*)
FROM public.vw_latest_bank_financials
ORDER BY view_name;

-- 09 PostgreSQL Schema and Database Validation

-- Question 1
-- What columns and data types exist in the main financial table

SELECT
    column_name,
    data_type,
    numeric_precision,
    numeric_scale,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'bank_financials_usd'
ORDER BY ordinal_position;

-- Question 2
-- How large is the final financial dataset

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT bank_name) AS bank_count,
    COUNT(DISTINCT iso3_code) AS country_count,
    COUNT(DISTINCT fiscal_year) AS year_count
FROM public.bank_financials_usd;

-- Question 3
-- Which tables exist in the public schema

SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_type, table_name;

-- Question 4
-- Which foreign key constraints exist in the public schema

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
   AND ccu.constraint_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- Question 5
-- Which indexes exist on the main financial table

SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'bank_financials_usd'
ORDER BY indexname;

-- Question 6
-- What objects depend on the main financial table

SELECT
    dependent_ns.nspname AS dependent_schema,
    dependent_view.relname AS dependent_object
FROM pg_depend d
JOIN pg_rewrite r
    ON d.objid = r.oid
JOIN pg_class dependent_view
    ON r.ev_class = dependent_view.oid
JOIN pg_namespace dependent_ns
    ON dependent_view.relnamespace = dependent_ns.oid
JOIN pg_class source_table
    ON d.refobjid = source_table.oid
JOIN pg_namespace source_ns
    ON source_table.relnamespace = source_ns.oid
WHERE source_ns.nspname = 'public'
  AND source_table.relname = 'bank_financials_usd'
ORDER BY dependent_schema, dependent_object;

-- 10 PostgreSQL Analysis Workflow
-- PostgreSQL was used as the main preparation and analytical layer before Power BI.

-- Question 1
-- What is the yearly coverage of the final dataset

SELECT
    fiscal_year,
    COUNT(*) AS records,
    COUNT(DISTINCT bank_name) AS banks,
    COUNT(DISTINCT iso3_code) AS countries
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- Question 2
-- Which banks have complete six year coverage

SELECT
    bank_name,
    iso3_code,
    COUNT(DISTINCT fiscal_year) AS years_available
FROM public.bank_financials_usd
GROUP BY bank_name, iso3_code
HAVING COUNT(DISTINCT fiscal_year) = 6
ORDER BY bank_name;

-- Question 3
-- Which countries have complete six year coverage

SELECT
    iso3_code,
    COUNT(DISTINCT fiscal_year) AS years_available
FROM public.bank_financials_usd
GROUP BY iso3_code
HAVING COUNT(DISTINCT fiscal_year) = 6
ORDER BY iso3_code;

-- Question 4
-- What is the yearly global banking summary

SELECT
    fiscal_year,
    COUNT(DISTINCT bank_name) AS banks,
    COUNT(DISTINCT iso3_code) AS countries,
    SUM(total_assets) AS total_assets_usd,
    SUM(total_deposits) AS total_deposits_usd,
    SUM(total_loans) AS total_loans_usd,
    SUM(net_income) AS total_net_income_usd,
    AVG(roe_percent) AS average_roe,
    AVG(roa_percent) AS average_roa
FROM public.bank_financials_usd
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- Question 5
-- Which banks changed asset rank the most between 2020 and 2025

WITH rankings AS (
    SELECT
        bank_name,
        fiscal_year,
        RANK() OVER (
            PARTITION BY fiscal_year
            ORDER BY total_assets DESC
        ) AS asset_rank
    FROM public.bank_financials_usd
    WHERE fiscal_year IN (2020, 2025)
),
pivoted AS (
    SELECT
        bank_name,
        MAX(asset_rank) FILTER (WHERE fiscal_year = 2020) AS rank_2020,
        MAX(asset_rank) FILTER (WHERE fiscal_year = 2025) AS rank_2025
    FROM rankings
    GROUP BY bank_name
)
SELECT
    bank_name,
    rank_2020,
    rank_2025,
    rank_2020 - rank_2025 AS rank_change
FROM pivoted
WHERE rank_2020 IS NOT NULL
  AND rank_2025 IS NOT NULL
ORDER BY ABS(rank_change) DESC;

-- Question 6
-- Which countries have the largest banking asset base in 2025

SELECT
    iso3_code,
    SUM(total_assets) AS total_assets_usd,
    COUNT(DISTINCT bank_name) AS bank_count
FROM public.bank_financials_usd
WHERE fiscal_year = 2025
GROUP BY iso3_code
ORDER BY total_assets_usd DESC
LIMIT 20;

-- Question 7
-- Which countries have the highest banking net income in 2025

SELECT
    iso3_code,
    SUM(net_income) AS total_net_income_usd,
    COUNT(DISTINCT bank_name) AS bank_count
FROM public.bank_financials_usd
WHERE fiscal_year = 2025
GROUP BY iso3_code
ORDER BY total_net_income_usd DESC
LIMIT 20;

-- End of GBIP SQL Analysis