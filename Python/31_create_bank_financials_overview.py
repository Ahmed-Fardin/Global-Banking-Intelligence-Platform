import psycopg2


# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 31 — CREATE FINANCIAL ANALYTICAL VIEWS
# ============================================================

DB_NAME = "gbip"
DB_USER = "postgres"
DB_PASSWORD = "1204"
DB_HOST = "localhost"
DB_PORT = 5432


print("=" * 70)
print("GLOBAL BANKING INTELLIGENCE")
print("31 — CREATE FINANCIAL ANALYTICAL VIEWS")
print("=" * 70)


# ============================================================
# CONNECT
# ============================================================

print()
print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = connection.cursor()

print("Connected to database:", DB_NAME)


# ============================================================
# VERIFY REQUIRED TABLES
# ============================================================

print()
print("=" * 70)
print("REQUIRED TABLE CHECK")
print("=" * 70)

required_tables = [
    "countries",
    "banks",
    "bank_financials",
]

for table in required_tables:

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (table,)
    )

    exists = cursor.fetchone()[0]

    print(
        f"{table}:",
        "FOUND" if exists else "MISSING"
    )

    if not exists:

        connection.rollback()
        cursor.close()
        connection.close()

        raise ValueError(
            f"Required table does not exist: {table}"
        )


# ============================================================
# VERIFY DATA
# ============================================================

print()
print("=" * 70)
print("SOURCE DATA CHECK")
print("=" * 70)

cursor.execute(
    "SELECT COUNT(*) FROM countries"
)

country_count = cursor.fetchone()[0]


cursor.execute(
    "SELECT COUNT(*) FROM banks"
)

bank_count = cursor.fetchone()[0]


cursor.execute(
    "SELECT COUNT(*) FROM bank_financials"
)

financial_count = cursor.fetchone()[0]


print(
    "Countries:",
    country_count
)

print(
    "Banks:",
    bank_count
)

print(
    "Financial records:",
    financial_count
)


if financial_count == 0:

    connection.rollback()
    cursor.close()
    connection.close()

    raise ValueError(
        "bank_financials contains no records."
    )


# ============================================================
# VIEW 1
# BANK FINANCIAL PERFORMANCE
# ============================================================

print()
print("=" * 70)
print("CREATING VIEW 1")
print("=" * 70)

print(
    "vw_bank_financial_performance"
)


cursor.execute(
    """
    CREATE OR REPLACE VIEW
        vw_bank_financial_performance
    AS

    SELECT

        f.financial_id,

        f.iso3_code,

        c.country_name,

        f.bank_name,

        b.bank_type,

        b.bank_rank,

        b.headquarters_city,

        b.official_website,

        b.founded_year,

        b.is_active,

        f.fiscal_year,

        f.total_assets,

        f.total_deposits,

        f.total_loans,

        f.shareholders_equity,

        f.operating_income,

        f.net_income,

        f.roe_percent,

        f.roa_percent,

        f.capital_adequacy_percent,

        f.cost_income_ratio,

        f.loan_to_deposit_ratio,

        f.npl_ratio,

        f.employees,

        f.branches,

        f.reporting_currency,

        f.source

    FROM bank_financials f

    LEFT JOIN banks b
        ON f.iso3_code = b.iso3_code
       AND f.bank_name = b.bank_name

    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code
    """
)


print("Created successfully.")


# ============================================================
# VIEW 2
# COUNTRY FINANCIAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("CREATING VIEW 2")
print("=" * 70)

print(
    "vw_country_financial_summary"
)


cursor.execute(
    """
    CREATE OR REPLACE VIEW
        vw_country_financial_summary
    AS

    SELECT

        f.iso3_code,

        c.country_name,

        f.fiscal_year,

        COUNT(*) AS bank_count,

        SUM(f.total_assets)
            AS total_assets,

        SUM(f.total_deposits)
            AS total_deposits,

        SUM(f.total_loans)
            AS total_loans,

        SUM(f.shareholders_equity)
            AS shareholders_equity,

        SUM(f.operating_income)
            AS operating_income,

        SUM(f.net_income)
            AS net_income,

        AVG(f.roe_percent)
            AS average_roe_percent,

        AVG(f.roa_percent)
            AS average_roa_percent,

        AVG(f.capital_adequacy_percent)
            AS average_capital_adequacy_percent,

        AVG(f.cost_income_ratio)
            AS average_cost_income_ratio,

        AVG(f.loan_to_deposit_ratio)
            AS average_loan_to_deposit_ratio,

        AVG(f.npl_ratio)
            AS average_npl_ratio,

        SUM(f.employees)
            AS total_employees,

        SUM(f.branches)
            AS total_branches

    FROM bank_financials f

    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code

    GROUP BY

        f.iso3_code,
        c.country_name,
        f.fiscal_year
    """
)


print("Created successfully.")


# ============================================================
# VIEW 3
# YEARLY GLOBAL BANKING SUMMARY
# ============================================================

print()
print("=" * 70)
print("CREATING VIEW 3")
print("=" * 70)

print(
    "vw_global_banking_yearly_summary"
)


cursor.execute(
    """
    CREATE OR REPLACE VIEW
        vw_global_banking_yearly_summary
    AS

    SELECT

        fiscal_year,

        COUNT(*) AS financial_records,

        COUNT(
            DISTINCT iso3_code
        ) AS countries,

        COUNT(
            DISTINCT
            iso3_code || '|' || bank_name
        ) AS banks,

        SUM(total_assets)
            AS total_assets,

        SUM(total_deposits)
            AS total_deposits,

        SUM(total_loans)
            AS total_loans,

        SUM(shareholders_equity)
            AS shareholders_equity,

        SUM(operating_income)
            AS operating_income,

        SUM(net_income)
            AS net_income,

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
            AS average_npl_ratio,

        SUM(employees)
            AS total_employees,

        SUM(branches)
            AS total_branches

    FROM bank_financials

    GROUP BY fiscal_year
    """
)


print("Created successfully.")


# ============================================================
# VIEW 4
# LATEST BANK FINANCIALS
# ============================================================

print()
print("=" * 70)
print("CREATING VIEW 4")
print("=" * 70)

print(
    "vw_latest_bank_financials"
)


cursor.execute(
    """
    CREATE OR REPLACE VIEW
        vw_latest_bank_financials
    AS

    SELECT

        f.financial_id,

        f.iso3_code,

        c.country_name,

        f.bank_name,

        f.fiscal_year,

        f.total_assets,

        f.total_deposits,

        f.total_loans,

        f.shareholders_equity,

        f.operating_income,

        f.net_income,

        f.roe_percent,

        f.roa_percent,

        f.capital_adequacy_percent,

        f.cost_income_ratio,

        f.loan_to_deposit_ratio,

        f.npl_ratio,

        f.employees,

        f.branches,

        f.reporting_currency

    FROM bank_financials f

    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code

    INNER JOIN (

        SELECT

            iso3_code,

            bank_name,

            MAX(fiscal_year)
                AS latest_year

        FROM bank_financials

        GROUP BY

            iso3_code,
            bank_name

    ) latest

        ON f.iso3_code =
            latest.iso3_code

       AND f.bank_name =
            latest.bank_name

       AND f.fiscal_year =
            latest.latest_year
    """
)


print("Created successfully.")


# ============================================================
# VIEW 5
# BANK YEAR-OVER-YEAR PERFORMANCE
# ============================================================

print()
print("=" * 70)
print("CREATING VIEW 5")
print("=" * 70)

print(
    "vw_bank_yearly_performance"
)


cursor.execute(
    """
    CREATE OR REPLACE VIEW
        vw_bank_yearly_performance
    AS

    SELECT

        f.financial_id,

        f.iso3_code,

        c.country_name,

        f.bank_name,

        f.fiscal_year,

        f.total_assets,

        f.total_deposits,

        f.total_loans,

        f.net_income,

        f.roe_percent,

        f.roa_percent,

        f.npl_ratio,

        LAG(f.total_assets)
            OVER (
                PARTITION BY
                    f.iso3_code,
                    f.bank_name

                ORDER BY
                    f.fiscal_year
            )
            AS previous_year_assets,

        LAG(f.total_deposits)
            OVER (
                PARTITION BY
                    f.iso3_code,
                    f.bank_name

                ORDER BY
                    f.fiscal_year
            )
            AS previous_year_deposits,

        LAG(f.total_loans)
            OVER (
                PARTITION BY
                    f.iso3_code,
                    f.bank_name

                ORDER BY
                    f.fiscal_year
            )
            AS previous_year_loans,

        LAG(f.net_income)
            OVER (
                PARTITION BY
                    f.iso3_code,
                    f.bank_name

                ORDER BY
                    f.fiscal_year
            )
            AS previous_year_net_income

    FROM bank_financials f

    LEFT JOIN countries c
        ON f.iso3_code = c.iso3_code
    """
)


print("Created successfully.")


# ============================================================
# COMMIT
# ============================================================

print()
print("=" * 70)
print("COMMITTING VIEWS")
print("=" * 70)


connection.commit()


# ============================================================
# VERIFY VIEWS
# ============================================================

print()
print("=" * 70)
print("VIEW VERIFICATION")
print("=" * 70)


expected_views = [
    "vw_bank_financial_performance",
    "vw_country_financial_summary",
    "vw_global_banking_yearly_summary",
    "vw_latest_bank_financials",
    "vw_bank_yearly_performance",
]


for view_name in expected_views:

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.views
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (view_name,)
    )

    exists = cursor.fetchone()[0]

    print(
        f"{view_name}:",
        "FOUND" if exists else "MISSING"
    )

    if not exists:

        connection.rollback()
        cursor.close()
        connection.close()

        raise ValueError(
            f"View creation failed: {view_name}"
        )


# ============================================================
# TEST VIEW ROW COUNTS
# ============================================================

print()
print("=" * 70)
print("VIEW ROW COUNT TEST")
print("=" * 70)


for view_name in expected_views:

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {view_name}
        """
    )

    count = cursor.fetchone()[0]

    print(
        f"{view_name}: {count:,} rows"
    )


# ============================================================
# CLOSE
# ============================================================

cursor.close()
connection.close()


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("ANALYTICAL VIEWS CREATED SUCCESSFULLY")
print("=" * 70)

print()
print("Views created:")

for view_name in expected_views:
    print(
        f"  ✓ {view_name}"
    )

print()
print("Database:", DB_NAME)

print()
print("DONE")
print("=" * 70)