# Global Banking Intelligence Platform

GBIP is a global banking analytics project built to analyze bank performance, profitability, growth, risk and stability across multiple countries and regions from 2020 to 2025.

The project was built using Python, PostgreSQL, Excel, SQL and Power BI.

## What GBIP Covers

- Global banking overview
- Regional banking analysis
- Country-level analysis
- Individual bank analysis
- Bank rankings
- Risk and stability analysis
- Banking growth and trends

Key metrics include:

- Total Assets
- Total Deposits
- Total Loans
- Net Income
- ROE
- ROA
- NPL Ratio
- Capital Adequacy
- Loan-to-Deposit Ratio
- Cost-to-Income Ratio

## Tools Used

Python was used for data extraction, processing, cleaning and synthetic data generation.

Python libraries used during the project include:

- pandas
- NumPy
- requests
- BeautifulSoup
- Playwright
- lxml
- PyMuPDF
- pdfplumber
- fake-useragent
- Loguru

Automated bank financial extraction was possible for only a limited number of countries because public financial sources varied significantly in structure and availability.

PostgreSQL was used as the main database and analytical layer.

SQL was used for data analysis, rankings, growth calculations, financial validation and extensive data-quality checks.

Power BI was used to build the final interactive dashboard, with DAX used for measures and dynamic ranking logic.

## Dataset

GBIP uses a hybrid dataset containing original public data and synthetic values.

Original values were retained wherever they were publicly available.

Synthetic values were only introduced where the required bank-level public data was unavailable.

When an original value could not be obtained, it was marked as `Pending Public Data` in the raw dataset.

The original financial datasets are preserved separately in the raw data folder:

- `bank_financials`
- `bank_financials_usd`

These contain the original collected values without synthetic replacements.

This allows the original data to be kept separate from the processed analytical dataset.

Synthetic values are intended for analytical and portfolio purposes.

## Documentation

The `docs` folder contains the detailed project documentation.

- Data Dictionary — data structures, dimensions and financial metrics
- Methodology — complete development process, data collection, processing and validation
- Database Schema — PostgreSQL database structure and relationships
- Power BI Model — Power BI relationships and analytical model
- SQL Analysis — analytical queries and data-quality checks

For the complete methodology and development process, see the `docs` folder.
