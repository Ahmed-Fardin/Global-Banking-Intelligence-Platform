# GBIP Data Dictionary

## 1. Project

GBIP stands for Global Banking Intelligence Platform.

GBIP is a banking analytics project built around a multi-country and multi-year banking dataset covering 2020 to 2025.

The project combines:

- Python for data preparation and processing
- PostgreSQL for storage, cleaning, validation, SQL analysis and views
- Power BI for the final interactive dashboard

The final dashboard is organized around:

1. Global Overview
2. Regional Analysis
3. Country Profile
4. Bank Profile
5. Bank Rankings
6. Risk and Stability

---

## 2. Main Analytical Dataset

### public.bank_financials_usd

This is the main financial dataset used for the final cross-country banking analysis.

The dataset contains bank-level annual financial records normalized to USD.

### Why USD normalization exists

Banks report financial values in their own reporting currencies. Directly comparing local-currency assets, deposits, loans or income across countries would not be meaningful.

The USD-normalized dataset allows cross-country monetary comparisons.

Ratios such as ROA, ROE, NPL ratio and capital adequacy are percentages and do not require currency conversion.

---

## 3. Core Identification Fields

### bank_name

The bank's name.

Used for:

- bank identification
- bank rankings
- bank profile analysis
- bank level filtering
- joins to the bank dimension

### iso3_code

Three-letter country code associated with the bank.

Used for:

- country filtering
- regional analysis
- country aggregation
- country level comparisons

### fiscal_year

Financial reporting year.

The project analysis period is 2020 through 2025.

Used for:

- yearly trends
- year slicers
- bank growth
- historical comparisons
- year-over-year analysis

### reporting_currency

The original reporting currency associated with the bank's financial data.

Used to preserve the source currency context before or alongside USD normalization.

### source

Identifies the source or origin category of the record.

Used for source validation and audit checks.

---

## 4. Bank Reference Fields

### bank_id

Unique bank identifier used by the dimensional model where available.

Used to connect bank records to DimBank and to support stable filtering without relying only on bank names.

### bank_type

Classification of the bank.

Used for bank segmentation and reference information.

### founded_year

Year associated with the bank's establishment.

Used as reference information and for data quality checks against fiscal years.

### swift_code

SWIFT/BIC identifier where available.

Used as a bank reference field and for consistency checks.

### official_website

Official bank website where available.

Used as reference information.

### is_active

Bank active status.

Used to distinguish active and inactive institutions where available.

---

## 5. Bank Operational Fields

### employees

Reported or generated employee count.

Used for operational scale analysis and data quality checks.

### branches

Reported or generated branch count.

Used for operational scale analysis and data quality checks.

### bank_rank

Bank ranking field where available.

Used for ranking analysis and validation.

---

## 6. Main Financial Fields

### total_assets

Total assets of the bank.

Used for:

- bank size
- global bank rankings
- country banking size
- regional analysis
- growth analysis

The USD-normalized value is used for cross-country monetary comparisons.

### total_deposits

Total deposits.

Used for:

- bank rankings
- country analysis
- global trends
- liquidity and funding analysis

### total_loans

Total loans.

Used for:

- bank rankings
- country analysis
- global trends
- growth analysis
- loan-to-deposit analysis

### shareholders_equity

Shareholders' equity.

Used for:

- capital structure analysis
- ROE calculation checks
- balance sheet validation

A specific data quality rule checks for records where shareholders equity is greater than total assets because this is normally inconsistent with the basic balance sheet relationship.

### operating_income

Operating income.

Used as a profitability and operating performance field.

### net_income

Net income attributable to the bank.

Used for:

- profitability rankings
- country profitability
- global income trends
- bank growth
- Power BI bank rankings

---

## 7. Banking Performance Ratios

### roe_percent

Return on Equity.

It measures profitability relative to shareholders equity.

Conceptually:

Net Income / Shareholders Equity x 100

Used for:

- profitability rankings
- bank comparisons
- country averages
- Power BI rankings

The project includes a SQL validation that compares stored ROE with a calculated ROE.

### roa_percent

Return on Assets.

It measures profitability relative to total assets.

Conceptually:

Net Income / Total Assets x 100

Used for:

- profitability rankings
- bank comparisons
- country averages
- Power BI rankings

The project includes a SQL validation that compares stored ROA with a calculated ROA.

### npl_ratio

Non-performing loan ratio.

Used as a credit-risk indicator.

Used for:

- risk rankings
- Top Risk Banks
- Risk and Stability dashboard analysis

NPL data required special validation during the project because some values were inconsistent or implausible.

### capital_adequacy_percent

Capital adequacy percentage.

Used as an indicator of capital strength and banking stability.

Used in:

- Risk and Stability
- Top Risk Banks
- bank comparisons
- risk analysis

### cost_income_ratio

Cost-to-income ratio.

Used as an efficiency indicator.

Used to identify banks with comparatively high operating cost burden.

### loan_to_deposit_ratio

Loan-to-deposit ratio.

Used to compare lending against deposit funding.

Conceptually:

Total Loans / Total Deposits x 100

The project includes a SQL validation comparing the stored ratio with the calculated ratio.

---

## 8. Dimension Tables

### DimBank

The bank dimension provides the common bank identity used by Power BI.

It is important because the same bank filter needs to affect multiple financial sources.

The dashboard ranking visual uses DimBank bank identity as the bank axis.

### DimYear

The year dimension provides the common fiscal year context.

It supports:

- year slicers
- yearly comparisons
- historical analysis
- ranking by selected year

### DimCountry

Country reference dimension.

Used for:

- country names
- ISO3 mapping
- country filtering
- country level dashboard analysis

### Regions

Regional reference data used to group countries into regions.

Used for regional filtering and Regional Analysis.

### Currency reference data

Currency lookup information used to preserve currency context and support normalization and reporting.

---

## 9. Analytical View

### public.gbip_bank_analysis

This is a PostgreSQL view rather than a physical table.

It combines banking financial information with reference information used by the analytical layer.

The view was used heavily during SQL analysis and Power BI modeling.

Important lesson from the project:

The view itself cannot be updated directly. When a source value needed correction, the underlying physical table had to be updated.

The project encountered this specifically while correcting bank financial values.

---

## 10. Power BI Ranking Metric

### Selected Ranking Metric

The Power BI ranking selector dynamically switches between:

- Total Assets
- Net Income
- ROE
- ROA
- Deposits
- Loans
- Capital Adequacy
- NPL Ratio

The final model uses the appropriate source field for each metric.

NPL required separate filter handling because its corrected source was in public.bank_financials_usd.

---

## 11. Main Analytical Questions

The SQL analysis layer answers questions about:

### Bank rankings

- Which banks have the highest assets?
- Which banks have the highest deposits?
- Which banks have the highest loans?
- Which banks generate the highest net income?
- Which banks have the highest ROE?
- Which banks have the highest ROA?

### Profitability

- Which banks are most profitable?
- Which banks consistently rank highly?
- How do ROE and ROA differ across banks?

### Country performance

- How many banks are represented in each country?
- Which countries have the largest banking asset base?
- Which countries generate the highest banking income?

### Global trends

- How does banking change from 2020 to 2025?
- How do assets, deposits and loans change?
- How does profitability change?

### Growth

- Which banks have the highest asset growth?
- Which banks have the highest loan growth?
- Which banks have the highest net income growth?
- Which banks show sustained growth?

### Risk and efficiency

- Which banks have the strongest capital adequacy?
- Which banks have the highest NPL ratios?
- Which banks have the lowest cost-to-income ratios?
- Which banks have high loan-to-deposit ratios?
- Which banks combine profitability with stronger risk indicators?

---

## 12. Data Quality Fields and Rules

The project includes extensive validation for:

- duplicate bank/year records
- missing bank names
- missing country codes
- invalid ISO3 codes
- missing fiscal years
- incomplete six-year bank coverage
- invalid financial values
- negative financial values
- zero-value anomalies
- shareholders equity greater than assets
- deposits greater than assets
- loans greater than assets
- ROA calculation differences
- ROE calculation differences
- loan-to-deposit calculation differences
- invalid NPL ratios
- unusual ROA
- unusual ROE
- unusual capital adequacy
- extreme cost-to-income ratios
- extreme year-over-year asset changes
- extreme year-over-year net income changes
- inconsistent currencies
- inconsistent source values
- inconsistent SWIFT codes
- missing websites
- inconsistent bank types
- inconsistent active status
- duplicate dimension records
- fact-to-dimension mismatches

---

## 13. Important Data Interpretation Rules

1. Monetary values should be compared across countries using the USD-normalized dataset.

2. Ratios should be interpreted as percentages.

3. A high NPL ratio generally represents higher credit risk.

4. Capital adequacy is a capital strength indicator and should not be interpreted as a profitability measure.

5. ROE and ROA should be interpreted together with the underlying assets, equity and income values.

6. SQL validation is used to identify anomalies rather than automatically assuming every unusual value is wrong.

7. Synthetic values are part of the project's dataset construction because complete official bank-level financial data was not consistently available across all target countries and years.

8. The project should distinguish between source-derived facts, generated data and corrected data when documenting the final dataset.
