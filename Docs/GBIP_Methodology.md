# GBIP Methodology

## 1\. Project Overview

GBIP stands for Global Banking Intelligence Platform.

The project was developed as an end-to-end banking analytics and business intelligence platform.

The original objective was to build a system that could move from a global banking view into regional, country and individual bank analysis while covering:

* Banking size
* Profitability
* Growth
* Risk
* Stability
* Efficiency
* Bank rankings
* Country and regional comparisons

The final project combines:

* Python
* PostgreSQL
* SQL
* Power BI
* DAX
* Public banking data
* Reference datasets
* Synthetic values only where required by unavailable public data

The main financial analysis covers 2020 to 2025.

\---

# 2\. Original Project Objective

The project began as an attempt to create a global banking intelligence platform rather than a simple Power BI dashboard.

The intended questions included:

* Which countries have the largest banking sectors?
* Which banks are the largest?
* Which banks generate the highest net income?
* Which banks have the strongest ROE and ROA?
* Which banks are growing?
* How are banking systems changing over time?
* Which banks have higher credit risk?
* Which banks have stronger capital positions?
* How do banking systems compare across regions?
* How can a user move from global results into country and bank-level detail?

This led to the decision to build a complete data pipeline instead of connecting raw CSV files directly to Power BI.

The final architecture became:

```text
Public and Reference Data
        ↓
Python Data Processing
        ↓
Raw and Processed Data
        ↓
PostgreSQL
        ↓
SQL Analysis and Validation
        ↓
PostgreSQL Views
        ↓
Power BI Data Model
        ↓
DAX
        ↓
GBIP Dashboard
```

\---

# 3\. Data Availability Challenge

A major challenge was obtaining consistent official bank-level financial data across a large number of countries and across six years.

The project encountered:

* Missing bank-level financial values
* Missing reporting years
* Different reporting currencies
* Different reporting formats
* Different levels of public disclosure
* Different financial reporting structures
* Countries where the required bank-level data was not publicly available
* Sources that could not be extracted consistently

The problem was therefore not simply finding banking data.

The real challenge was finding **comparable bank-level data with sufficient year and metric coverage**.

Because the project required broad analytical coverage from 2020 to 2025, a hybrid dataset approach was adopted.

\---

# 4\. Hybrid Dataset Methodology

GBIP is a **hybrid dataset**, not a fully synthetic dataset.

It contains three practical categories of information:

1. Original publicly available values
2. Synthetic values used only where the required original bank-level data was unavailable
3. Values remaining as `Pending Public Data` where the original value could not be obtained in the raw dataset

Synthetic values were therefore **not used for every country, bank or financial field**.

Whenever an original public value was available, it was retained.

Synthetic completion was used only where the required public data was unavailable and the final analytical dataset required a value for the intended analysis.

This distinction is important when interpreting the final dashboard.

\---

# 5\. Original Data Preservation

The project deliberately preserved the original collected financial datasets separately from the processed analytical dataset.

The main original financial files are:

```text
bank\_financials
bank\_financials\_usd
```

These original datasets contain:

* Original collected financial values
* Missing values marked as `Pending Public Data`
* No synthetic replacement values
* No generated replacement values

The processed analytical dataset is separate.

This creates a clear distinction:

```text
Original Collected Data
        ↓
Public Data Gaps
        ↓
Pending Public Data
        ↓
Processed Analytical Dataset
        ↓
Synthetic Completion Where Required
```

This preservation was important because it allows the project to retain the original collected evidence instead of overwriting unavailable values with generated numbers.

\---

# 6\. Python Financial Data Extraction

Python was used during the data-collection and preparation stages to extract and process bank financial information from publicly available sources.

Python was particularly useful for sources where bank financial information could be obtained in a sufficiently consistent structure.

However, automated extraction was only practical for a **limited number of countries**.

The project encountered major differences between countries in:

* Source structure
* Public availability
* Financial reporting format
* Data accessibility
* Bank-level coverage
* Year coverage
* Metric availability

Therefore, Python extraction was **not used as the universal method for collecting every country's bank financials**.

Where automated Python extraction was feasible, it was used to reduce manual collection and structure the financial information.

For other countries, the project used other available public-data collection methods.

Where the required original information still could not be obtained, the raw dataset retained:

`Pending Public Data`

Synthetic values were introduced only in the processed analytical dataset where required.

The overall collection process was therefore:

```text
Public Financial Sources
        ↓
Python Extraction Where Feasible
        +
Other Public Data Collection
        +
Reference Data
        ↓
Original Raw Dataset
        ↓
Pending Public Data for Unavailable Values
        ↓
Synthetic Completion Where Required
        ↓
Processed Analytical Dataset
```

Python was therefore one part of the overall data-collection workflow rather than the source of every financial record.

\---

# 7\. Reference Data Collection

The project also assembled reference data required to create a global banking model.

Reference information included:

* Countries
* ISO3 country codes
* Regions
* Currency information
* Bank reference information
* Country economic information

Country and regional reference data became particularly important because the final dashboard needed both country and regional filtering.

A regional classification was incorporated so countries could be grouped into broader geographic regions.

\---

# 8\. Initial PostgreSQL Database Development

PostgreSQL was selected as the main database and analytical storage layer.

The project created a GBIP PostgreSQL database and progressively developed the schema around banking and reference data.

PostgreSQL was used for:

* Data storage
* Relational modeling
* Data cleaning
* Data validation
* Financial analysis
* Aggregations
* Ranking
* Growth analysis
* Views
* Dependency inspection
* Source-level corrections
* Preparing data for Power BI

The decision to use PostgreSQL was important because the project needed a repeatable analytical layer outside Power BI.

\---

# 9\. Database Architecture

The database evolved around financial data and supporting reference tables.

Important objects included:

* `bank\_financials`
* `bank\_financials\_usd`
* `banks`
* `countries`
* `regions`
* `country\_economic\_data`
* Currency/reference data
* Development and backup objects used during the project

Temporary and backup objects were part of the development process but are not treated as part of the final conceptual architecture.

The final PostgreSQL ERD was generated from the database and saved as part of the project documentation.

\---

# 10\. Dimension Model

The final analytical model uses common dimensions for filtering and identity.

## DimBank

Provides a common bank identity for the Power BI model.

It became particularly important because different financial metrics and supporting datasets did not always originate from the same table.

## DimCountry

Provides common country context for:

* Country filtering
* Geographic analysis
* Country-level reporting
* Bank-to-country mapping

## DimYear

Provides common fiscal-year context for:

* Year filtering
* Historical comparisons
* Year-over-year analysis
* Ranking by selected year

## Regions

Provides country-to-region classification for Regional Analysis.

## Currency Reference

Preserves currency context and supports financial normalization.

\---

# 11\. Financial Data Grain

The main financial dataset was designed around annual bank records.

The intended grain is:

**One bank for one fiscal year.**

The main analysis period is:

```text
2020
2021
2022
2023
2024
2025
```

This grain is important because bank rankings, growth calculations and year-over-year comparisons depend on bank-year records.

\---

# 12\. USD Normalization

Banks report financial values in different currencies.

Directly comparing local-currency assets, deposits, loans or income between countries would not produce meaningful monetary comparisons.

The project therefore created:

`public.bank\_financials\_usd`

The USD-normalized financial fields include:

* Total Assets
* Total Deposits
* Total Loans
* Shareholders Equity
* Operating Income
* Net Income

The purpose was to provide a common monetary basis for cross-country comparisons.

Percentage-based ratios such as ROA, ROE, NPL and capital adequacy do not require monetary currency conversion.

\---

# 13\. PostgreSQL Data Loading and Processing

The prepared datasets were loaded into PostgreSQL.

PostgreSQL became the central layer for:

* Storing the financial data
* Joining reference information
* Checking data quality
* Running analytical SQL
* Creating reusable views
* Preparing data for Power BI

The project deliberately avoided performing all transformation and validation directly inside Power BI.

This made it possible to investigate source data independently from dashboard behavior.

\---

# 14\. SQL Analysis Development

A substantial amount of the project work was performed in PostgreSQL through SQL.

SQL was used for more than basic retrieval.

It was used for:

* Bank rankings
* Profitability analysis
* Country analysis
* Global trends
* Growth analysis
* Risk analysis
* Efficiency analysis
* Year-over-year calculations
* Data-quality validation
* Dimension validation
* View inspection
* Schema inspection
* Dependency analysis

Window functions, aggregations, conditional logic, filtering and calculated comparisons were used throughout the analysis.

\---

# 15\. Bank Ranking Analysis

SQL was used to answer:

* Which banks have the highest total assets?
* Which banks have the highest deposits?
* Which banks have the highest loans?
* Which banks generate the highest net income?
* Which banks have the highest ROE?
* Which banks have the highest ROA?

These analyses formed the basis for the Power BI Bank Rankings page.

\---

# 16\. Profitability Analysis

Profitability analysis focused on:

* Net income
* ROE
* ROA

The project used both stored ratio values and calculated relationships to validate profitability.

The SQL layer compared stored ratios with ratios calculated from the underlying financial values.

This was especially useful when unrealistic profitability values appeared in Power BI.

\---

# 17\. Country and Regional Analysis

Bank-level financial data was aggregated to:

* Country
* Region
* Global

levels.

Country analysis included:

* Bank count
* Total assets
* Deposits
* Loans
* Net income
* Profitability

Regional analysis was added because country-level data alone could not support the intended regional filtering and comparison.

\---

# 18\. Growth Analysis

The SQL layer was used to measure:

* Asset growth
* Loan growth
* Net income growth
* Year-over-year changes
* Sustained growth

Window functions such as `LAG` were used to compare consecutive years.

The same logic was also used to identify unusually large year-over-year movements that could indicate data problems.

\---

# 19\. Risk and Efficiency Analysis

Risk and stability analysis focused on:

* NPL ratio
* Capital adequacy
* Cost-to-income ratio
* Loan-to-deposit ratio

These metrics were used in the final Risk and Stability dashboard.

The objective was to evaluate banks beyond simple size and profitability.

\---

# 20\. Data Quality as a Separate Workstream

Data quality became one of the largest parts of the PostgreSQL work.

The project did not assume that a complete dataset was automatically correct.

SQL checks were developed for:

* Duplicate records
* Missing values
* Missing years
* Invalid country codes
* Incomplete bank histories
* Negative financial values
* Financial relationships
* Ratio inconsistencies
* Extreme values
* Dimension mismatches
* Source inconsistencies

The final SQL analysis file contains more than fifty detailed data-quality checks plus summary checks.

\---

# 21\. Duplicate Bank-Year Validation

The intended financial grain is:

```text
One Bank + One Fiscal Year = One Financial Record
```

Duplicate bank-year records could distort:

* Assets
* Deposits
* Loans
* Net income
* Bank counts
* Rankings
* Power BI measures

PostgreSQL was therefore used to identify duplicate bank-year combinations.

\---

# 22\. Missing Year Validation

The project checked for gaps in a bank's annual sequence.

For example:

```text
2020
2021
2022
2024
2025
```

contains a missing 2023 record.

SQL window functions were used to identify gaps between consecutive fiscal years.

This was important because growth calculations depend on reliable year-to-year coverage.

\---

# 23\. Financial Consistency Checks

The project checked for:

* Negative assets
* Negative deposits
* Negative loans
* Negative equity
* Negative operating income
* Zero-value anomalies
* Shareholders equity greater than assets
* Deposits greater than assets
* Loans greater than assets

The objective was to identify records requiring investigation before the dashboard used them.

\---

# 24\. Shareholders Equity Greater Than Assets

One of the specific problems identified through SQL was:

```text
Shareholders Equity > Total Assets
```

The basic accounting relationship is:

```text
Assets = Liabilities + Equity
```

Therefore, equity greater than total assets was treated as an inconsistent record requiring investigation.

The affected source records were corrected in the physical financial dataset.

The project followed the principle of correcting the source data instead of creating a special DAX workaround.

\---

# 25\. Net Income Problem

Net income became one of the major debugging cases.

At one stage, Power BI displayed incorrect net income rankings.

The investigation moved through the entire pipeline:

```text
Power BI Visual
      ↓
DAX Measure
      ↓
Power BI Model
      ↓
PostgreSQL View
      ↓
bank\_financials\_usd
```

The PostgreSQL source revealed incorrect values.

A major example was BNP Paribas, where net income appeared around:

```text
153 billion
```

instead of the intended project value around:

```text
15.3 billion
```

The source financial value was corrected.

The correction was made at the data layer instead of hiding the problem inside a DAX measure.

\---

# 26\. ROE Problem

ROE produced several unrealistic results during development.

Some banks displayed extremely high ROE values.

The project investigated:

* Net income
* Shareholders equity
* Stored ROE
* Calculated ROE
* Power BI filter context

The SQL layer compares stored ROE with:

```text
Net Income / Shareholders Equity × 100
```

This helped determine whether a problem originated in:

* Source data
* Calculation
* Filtering
* Visualization

\---

# 27\. ROA Problem

ROA produced another synthetic-data anomaly.

BNP Paribas had an ROA around 5 percent while other major banks in the project were around the 1 percent range.

Because this was a synthetic project value rather than an official reported figure, the value was adjusted to a more realistic project value.

The final project value used for the affected records was approximately:

```text
0.75%
```

This value must not be interpreted as an official reported BNP Paribas ROA.

\---

# 28\. NPL Problem

NPL was one of the more difficult Power BI metrics.

The NPL source and the sources used by some other ranking metrics did not always share the same filtering path.

The project investigated:

* Bank dimension
* Financial source
* Bank identity
* Fiscal year
* DAX filter context
* PostgreSQL source values

The final NPL logic used the corrected source and appropriate filter transfer.

NPL was therefore treated separately from metrics that naturally shared the main financial source.

\---

# 29\. Power BI Relationship Problems

A major class of issues occurred when a visual displayed the same metric for multiple banks.

For example:

```text
Bank A   100
Bank B   100
Bank C   100
Bank D   100
```

even though the source values were different.

This indicated that the bank filter was not reaching the metric source.

The project investigated:

* DimBank
* Bank identifiers
* Bank names
* Relationships
* DimYear
* DAX filter context
* `TREATAS`
* `SELECTEDVALUE`
* `VALUES`
* `FILTER`

The final model used common dimensions where possible and explicit filter transfer where required.

\---

# 30\. Bank Count Problem

Bank counts also produced inconsistencies.

Different counts appeared depending on whether the project counted:

* Rows
* Distinct bank names
* Bank IDs
* Dimension records
* Financial records

The project therefore distinguished between row counts and distinct bank identity.

This was important for the Global Overview.

\---

# 31\. Dynamic Ranking Measure

The Power BI ranking system uses a dynamic measure that switches between:

* Total Assets
* Net Income
* ROE
* ROA
* Deposits
* Loans
* Capital Adequacy
* NPL Ratio

The measure required careful handling because the metrics did not always originate from the same source or share identical filter paths.

A key lesson was:

**Correct DAX cannot compensate for incorrect source data or broken relationships.**

\---

# 32\. Power BI Model Development

After the PostgreSQL data and SQL validation were established, the data was brought into Power BI.

The Power BI model used common dimensions for:

* Bank
* Country
* Region
* Year

The model view was separately documented to show the analytical relationships used by Power BI.

\---

# 33\. Dashboard Development

The final dashboard was organized into six major areas:

1. Global Overview
2. Regional Analysis
3. Country Profile
4. Bank Profile
5. Bank Rankings
6. Risk and Stability

The dashboard uses:

* KPI cards
* Maps
* Ranking visuals
* Trend charts
* Slicers
* Dynamic metrics
* Banking risk indicators

The final visual design was intentionally kept clean and consistent.

Once the dashboard was considered complete, additional visual polishing was stopped so the project could move into documentation and publication.

\---

# 34\. Global Overview

The Global Overview provides a high-level view of:

* Banking scale
* Financial totals
* Bank coverage
* Country coverage
* Key banking indicators
* Geographic context

It acts as the entry point into the platform.

\---

# 35\. Regional Analysis

Regional Analysis compares banking systems across geographic regions.

The page depends on country-to-region mapping.

This required the Regions dataset and relationship structure so users could filter and compare regional banking performance.

\---

# 36\. Country Profile

Country Profile moves from global and regional analysis into a specific banking system.

It combines:

* Country context
* Economic information
* Banking sector scale
* Bank-level information

The purpose is to understand the banking system within a country.

\---

# 37\. Bank Profile

Bank Profile focuses on individual institutions.

It combines:

* Bank size
* Profitability
* Growth
* Risk
* Capital strength
* Efficiency

This allows users to move from sector-level information into individual bank performance.

\---

# 38\. Bank Rankings

The Bank Rankings page compares institutions across the major metrics:

* Total Assets
* Net Income
* ROE
* ROA
* Deposits
* Loans
* Capital Adequacy
* NPL Ratio

The dynamic ranking selector allows the same ranking area to answer different questions.

\---

# 39\. Risk and Stability

Risk and Stability focuses on:

* NPL ratio
* Capital adequacy
* Loan-to-deposit ratio
* Cost-to-income ratio

The Top Risk Banks analysis uses NPL and related risk indicators while displaying capital context.

The purpose is to avoid evaluating banks only by size or profitability.

\---

# 40\. Power BI Unsaved-Changes Issue

During development, Power BI was closed without saving the latest changes.

This caused the project to return to the previously saved working version.

The saved version was used as the baseline for restoring the dashboard.

This reinforced the importance of:

* Saving major changes
* Validating measures before closing
* Maintaining a known-good version

The final dashboard was rebuilt from the saved working state and then validated against PostgreSQL.

\---

# 41\. Source-Level Correction Principle

A major methodological rule developed during the project was:

> Correct the problem at the lowest appropriate layer.

For example:

```text
Incorrect Source Value
        ↓
Correct PostgreSQL Data
        ↓
Refresh Power BI
        ↓
Validate DAX
```

rather than:

```text
Incorrect Source Value
        ↓
Create a DAX Exception
```

This principle was applied whenever a problem originated in the financial source.

\---

# 42\. PostgreSQL Views

PostgreSQL views were used as reusable analytical layers.

An important view was:

`public.gbip\_bank\_analysis`

Views were useful for:

* Reusable joins
* Consistent analytical logic
* Reducing repeated SQL
* Preparing data for Power BI
* Separating analytical logic from physical storage

The SQL documentation also includes view inspection and validation.

\---

# 43\. PostgreSQL View Update Error

The project encountered an issue when attempting to update an analytical PostgreSQL view directly.

PostgreSQL rejected the operation because the object was a view rather than a physical table.

The project investigated the view definition and dependencies and identified the underlying financial table.

The underlying physical table was then updated.

This became an important practical database lesson about the difference between:

```text
Physical Table
```

and:

```text
View
```

\---

# 44\. PostgreSQL Schema and ERD

The final database schema was documented using the PostgreSQL ERD tool.

The ERD represents the actual database structure and relationships.

It is used in the project documentation to show the database layer independently from the Power BI analytical model.

The Power BI relationship/model diagram is kept separately because it represents the reporting model rather than the physical PostgreSQL schema.

\---

# 45\. SQL Documentation

The final SQL file was organized into major analytical sections covering:

1. Bank Rankings
2. Bank Profitability
3. Country Financial Performance
4. Global Banking Trends
5. Bank Growth
6. Bank Risk and Efficiency
7. Data Quality Checks
8. PostgreSQL Views
9. PostgreSQL Schema and Database Validation
10. PostgreSQL Analysis Workflow

The SQL file therefore serves as both an analytical query collection and a validation record for the project.

\---

# 46\. Final Data Quality Validation

Before finalizing the project, PostgreSQL was used to validate:

* Total records
* Bank counts
* Country counts
* Year coverage
* Duplicate records
* Missing values
* Financial anomalies
* Ratio calculations
* Dimension consistency
* View consistency
* Fact-to-dimension coverage
* Extreme year-over-year movements

The final SQL documentation contains more than fifty detailed data-quality checks plus summary checks.

\---

# 47\. Data Quality Philosophy

The project treats an anomaly as a signal for investigation rather than automatic proof that a value is wrong.

For example:

* High ROE
* High ROA
* High capital adequacy
* High NPL
* Loans greater than assets
* Deposits greater than assets
* Large year-over-year changes

can trigger investigation.

The project therefore uses SQL to identify suspicious records and then evaluates whether the issue is:

* A genuine unusual value
* A source-data problem
* A synthetic-data problem
* A calculation problem
* A relationship problem
* A filter-context problem

\---

# 48\. Final Data Architecture

The completed architecture is:

```text
Original Public Data
        ↓
Raw Data
        ↓
Python / Other Data Collection
        ↓
Data Processing
        ↓
Hybrid Processed Dataset
        ↓
PostgreSQL
        ↓
Data Quality Validation
        ↓
SQL Analysis
        ↓
PostgreSQL Views
        ↓
Power BI Data Model
        ↓
DAX Measures
        ↓
Interactive Dashboard
```

Each layer has a distinct role.

Python handles extraction where feasible and data preparation.

PostgreSQL handles storage, relational structure and source-level analysis.

SQL handles analysis and validation.

Views provide reusable analytical layers.

Power BI provides interactive reporting.

DAX handles dashboard-specific calculations and dynamic metrics.

\---

# 49\. Documentation Architecture

The final project documentation is separated into different purposes.

## Data Dictionary

Explains important analytical fields, dimensions, metrics and data structures.

## SQL Analysis

Documents the analytical questions and PostgreSQL validation queries.

## PostgreSQL ERD

Documents physical database structure and relationships.

## Power BI Model Diagram

Documents the analytical relationships used by Power BI.

## Methodology

Documents how GBIP was built, including data collection, hybrid data construction, PostgreSQL development, SQL analysis, Power BI development and the major problems encountered.

## README

Provides the concise public-facing project overview.

This separation keeps the README readable while preserving the technical history in the methodology.

\---

# 50\. Limitations

The most important limitation is the hybrid nature of the financial dataset.

Therefore:

* Original values should be treated as source-derived values.
* Synthetic values should be treated as generated project values.
* `Pending Public Data` represents an original data availability gap.
* Rankings involving synthetic values are illustrative.
* Cross-country monetary comparisons depend on USD normalization.
* Synthetic ratios should not be interpreted as official reported bank metrics.
* Python extraction was not possible for every country.
* Public financial information was not consistently available across every bank, metric and year.

GBIP should therefore be understood primarily as a demonstration of data engineering, database development, SQL analysis, financial analytics and business intelligence.

\---

# 51\. What GBIP Demonstrates

## Data Engineering

* Multi-source data preparation
* Public data extraction
* Python-based extraction where feasible
* Hybrid dataset construction
* Data normalization
* Reference data integration

## Python

* Financial data extraction where feasible
* Data processing
* Data preparation
* Synthetic completion where required
* Dataset transformation

## PostgreSQL

* Relational database design
* Data storage
* SQL analysis
* Views
* Dependencies
* Source-level correction
* Data validation

## SQL

* Aggregation
* Ranking
* Window functions
* Growth analysis
* Ratio validation
* Data-quality checks
* Dimension validation
* View validation

## Power BI

* Data modeling
* Relationships
* DAX
* Dynamic measures
* Interactive filtering
* KPI design
* Dashboard development

## Financial Analytics

* Assets
* Deposits
* Loans
* Net income
* ROA
* ROE
* NPL
* Capital adequacy
* Cost-to-income
* Loan-to-deposit

\---

# 52\. Final Project Outcome

GBIP is a complete banking analytics platform rather than a single visualization.

It preserves original collected financial data, records public-data gaps, uses synthetic values only where required, validates the resulting dataset through PostgreSQL and SQL, and presents the final analysis through Power BI.

The final workflow is:

```text
Data Collection
    ↓
Data Preparation
    ↓
Hybrid Dataset Construction
    ↓
Database Design
    ↓
Data Quality
    ↓
SQL Analysis
    ↓
Data Modeling
    ↓
DAX
    ↓
Business Intelligence
    ↓
Dashboard
```

The final repository should clearly distinguish:

* Original source data
* Processed hybrid data
* SQL analysis
* Database documentation
* Power BI model
* Final dashboard
* Methodology and project documentation

