# ============================================================
# GLOBAL BANKING INTELLIGENCE
# 34 — CREATE USD-NORMALIZED BANK FINANCIALS
# CSV ONLY
# ============================================================

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import requests


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "Data/Raw/Banks/Mains/bank_financials_synthetic.csv"
)

OUTPUT_FILE = Path(
    "Data/Raw/Banks/Mains/bank_financials_usd.csv"
)

FX_REFERENCE_FILE = Path(
    "Data/Raw/Banks/Mains/fx_rates_complete.csv"
)

START_YEAR = 2020
END_YEAR = 2025

WORLD_BANK_START = 1960
WORLD_BANK_END = 2025

WORLD_BANK_OFFICIAL = "PA.NUS.FCRF"
WORLD_BANK_ALTERNATIVE = "PA.NUS.ATLS"

FRANKFURTER_BASE = "USD"

REQUEST_TIMEOUT = 120


# ============================================================
# EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "iso3_code",
    "bank_name",
    "fiscal_year",
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income",
    "roe_percent",
    "roa_percent",
    "capital_adequacy_percent",
    "cost_income_ratio",
    "loan_to_deposit_ratio",
    "npl_ratio",
    "employees",
    "branches",
    "reporting_currency",
    "source",
]


MONETARY_COLUMNS = [
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income",
]


# ============================================================
# DISPLAY
# ============================================================

def section(title):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# WORLD BANK DOWNLOAD
# ============================================================

def download_world_bank(
    indicator,
    description,
):

    print()
    print(
        f"Downloading: {description}"
    )

    print(
        f"Indicator: {indicator}"
    )

    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        f"indicator/{indicator}"
    )

    params = {
        "format": "json",
        "per_page": 30000,
        "date": (
            f"{WORLD_BANK_START}:"
            f"{WORLD_BANK_END}"
        ),
    }

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError(
            "Unexpected World Bank response."
        )

    if len(payload) < 2:
        raise ValueError(
            f"No data returned for {indicator}."
        )

    rows = []

    for item in payload[1]:

        iso3 = item.get(
            "countryiso3code"
        )

        year = item.get(
            "date"
        )

        value = item.get(
            "value"
        )

        if not iso3:
            continue

        if value is None:
            continue

        try:
            year = int(year)
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            continue

        if not np.isfinite(value):
            continue

        if value <= 0:
            continue

        iso3 = (
            str(iso3)
            .strip()
            .upper()
        )

        if len(iso3) != 3:
            continue

        rows.append(
            {
                "iso3_code": iso3,
                "fiscal_year": year,
                "fx_rate": value,
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        raise ValueError(
            f"No usable data for {indicator}."
        )

    result = (
        result
        .sort_values(
            [
                "iso3_code",
                "fiscal_year",
            ]
        )
        .drop_duplicates(
            [
                "iso3_code",
                "fiscal_year",
            ],
            keep="last",
        )
        .reset_index(drop=True)
    )

    print(
        f"Records: {len(result):,}"
    )

    print(
        f"Countries: "
        f"{result['iso3_code'].nunique():,}"
    )

    return result


# ============================================================
# FRANKFURTER CURRENCY LIST
# ============================================================

def get_frankfurter_currencies():

    print()
    print(
        "Downloading Frankfurter currency list..."
    )

    url = (
        "https://api.frankfurter.dev/v2/"
        "currencies"
    )

    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    currencies = set()

    for item in data:

        code = item.get(
            "iso_code"
        )

        if code:

            currencies.add(
                str(code)
                .strip()
                .upper()
            )

    currencies.add("USD")

    print(
        f"Frankfurter currencies available: "
        f"{len(currencies):,}"
    )

    return currencies


# ============================================================
# FRANKFURTER HISTORICAL RATE
# ============================================================

def get_frankfurter_rate(
    currency,
    year,
):

    if currency == "USD":

        return {
            "rate": 1.0,
            "date": f"{year}-01-01",
            "source": "USD — direct",
        }

    # --------------------------------------------------------
    # Request a full-year range.
    # Frankfurter returns available historical
    # observations.
    # --------------------------------------------------------

    start_date = (
        f"{year}-01-01"
    )

    end_date = (
        f"{year}-12-31"
    )

    url = (
        "https://api.frankfurter.dev/v2/"
        "rates"
    )

    params = {
        "base": currency,
        "quotes": "USD",
        "from": start_date,
        "to": end_date,
    }

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        return None

    rates = []

    for item in data:

        rate = item.get(
            "rate"
        )

        date = item.get(
            "date"
        )

        if rate is None:
            continue

        try:
            rate = float(rate)
        except (
            TypeError,
            ValueError,
        ):
            continue

        if not np.isfinite(rate):
            continue

        if rate <= 0:
            continue

        rates.append(
            {
                "date": date,
                "rate": rate,
            }
        )

    if not rates:
        return None

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We need LCU per USD.
    #
    # Frankfurter gives:
    #
    #     1 LCU = X USD
    #
    # Therefore:
    #
    #     1 USD = 1 / X LCU
    #
    # We calculate the annual average of the
    # daily LCU/USD rates first, then invert it.
    # --------------------------------------------------------

    usd_per_local = np.mean(
        [
            item["rate"]
            for item in rates
        ]
    )

    if usd_per_local <= 0:
        return None

    lcu_per_usd = (
        1.0
        /
        usd_per_local
    )

    return {
        "rate": lcu_per_usd,
        "date": (
            f"{year}-annual-average"
        ),
        "source": (
            "Frankfurter — "
            "annual average"
        ),
    }


# ============================================================
# LOAD SOURCE
# ============================================================

section(
    "GLOBAL BANKING INTELLIGENCE"
)

print(
    "34 — CREATE USD-NORMALIZED "
    "BANK FINANCIALS"
)

print()
print(
    "Input:"
)

print(
    INPUT_FILE
)

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input file not found: "
        f"{INPUT_FILE}"
    )


financials = pd.read_csv(
    INPUT_FILE
)

original_rows = len(
    financials
)

print()
print(
    f"Rows: {len(financials):,}"
)

print(
    f"Columns: {len(financials.columns):,}"
)


# ============================================================
# COLUMN CHECK
# ============================================================

section(
    "COLUMN CHECK"
)

missing = [
    column
    for column in EXPECTED_COLUMNS
    if column not in financials.columns
]

extra = [
    column
    for column in financials.columns
    if column not in EXPECTED_COLUMNS
]

print(
    f"Expected columns: "
    f"{len(EXPECTED_COLUMNS)}"
)

print(
    f"Actual columns: "
    f"{len(financials.columns)}"
)

print(
    f"Missing columns: "
    f"{len(missing)}"
)

print(
    f"Extra columns: "
    f"{len(extra)}"
)

if missing:

    print()

    for column in missing:
        print(
            f"Missing: {column}"
        )

    raise ValueError(
        "Required columns are missing."
    )


# ============================================================
# NORMALIZE TEXT
# ============================================================

section(
    "TEXT NORMALIZATION"
)

financials["iso3_code"] = (
    financials["iso3_code"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)

financials["bank_name"] = (
    financials["bank_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

financials["reporting_currency"] = (
    financials["reporting_currency"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# BASIC VALIDATION
# ============================================================

section(
    "BASIC VALIDATION"
)

invalid_iso3 = (
    financials["iso3_code"].str.len()
    != 3
)

blank_bank = (
    financials["bank_name"].str.len()
    == 0
)

print(
    f"Invalid ISO3: "
    f"{int(invalid_iso3.sum())}"
)

print(
    f"Blank bank names: "
    f"{int(blank_bank.sum())}"
)

if invalid_iso3.any():
    raise ValueError(
        "Invalid ISO3 values detected."
    )

if blank_bank.any():
    raise ValueError(
        "Blank bank names detected."
    )


# ============================================================
# FISCAL YEAR
# ============================================================

section(
    "FISCAL YEAR CHECK"
)

financials["fiscal_year"] = (
    pd.to_numeric(
        financials["fiscal_year"],
        errors="coerce",
    )
)

invalid_year = (
    financials["fiscal_year"].isna()
    |
    ~financials["fiscal_year"].between(
        START_YEAR,
        END_YEAR,
    )
)

print(
    f"Invalid fiscal years: "
    f"{int(invalid_year.sum())}"
)

if invalid_year.any():
    raise ValueError(
        "Invalid fiscal years detected."
    )

financials["fiscal_year"] = (
    financials["fiscal_year"]
    .astype(int)
)


# ============================================================
# DUPLICATES
# ============================================================

section(
    "DUPLICATE CHECK"
)

duplicates = (
    financials
    .groupby(
        [
            "iso3_code",
            "bank_name",
            "fiscal_year",
        ],
        dropna=False,
    )
    .size()
)

duplicates = duplicates[
    duplicates > 1
]

print(
    f"Duplicate groups: "
    f"{len(duplicates):,}"
)

if not duplicates.empty:
    raise ValueError(
        "Duplicate bank/year records detected."
    )


# ============================================================
# MONETARY FIELDS
# ============================================================

section(
    "MONETARY FIELD NORMALIZATION"
)

for column in MONETARY_COLUMNS:

    financials[column] = pd.to_numeric(
        financials[column],
        errors="coerce",
    )

    print(
        f"{column}: normalized"
    )


# ============================================================
# WORLD BANK OFFICIAL
# ============================================================

section(
    "WORLD BANK OFFICIAL FX"
)

official_fx = download_world_bank(
    WORLD_BANK_OFFICIAL,
    "Official exchange rate",
)

official_lookup = {}

for row in official_fx.itertuples(
    index=False
):

    key = (
        row.iso3_code,
        int(row.fiscal_year),
    )

    official_lookup[key] = float(
        row.fx_rate
    )


# ============================================================
# WORLD BANK ALTERNATIVE
# ============================================================

section(
    "WORLD BANK ALTERNATIVE FX"
)

alternative_fx = download_world_bank(
    WORLD_BANK_ALTERNATIVE,
    "DEC alternative conversion factor",
)

alternative_lookup = {}

for row in alternative_fx.itertuples(
    index=False
):

    key = (
        row.iso3_code,
        int(row.fiscal_year),
    )

    alternative_lookup[key] = float(
        row.fx_rate
    )


# ============================================================
# FRANKFURTER CURRENCY LIST
# ============================================================

section(
    "FRANKFURTER FALLBACK"
)

frankfurter_currencies = (
    get_frankfurter_currencies()
)


# ============================================================
# BUILD FX LOOKUP
# ============================================================

section(
    "BUILDING FX LOOKUP"
)

fx_records = []

unresolved = []

frankfurter_cache = {}


for index, row in financials.iterrows():

    iso3 = str(
        row["iso3_code"]
    ).strip().upper()

    currency = str(
        row["reporting_currency"]
    ).strip().upper()

    year = int(
        row["fiscal_year"]
    )

    # --------------------------------------------------------
    # USD DIRECT
    # --------------------------------------------------------

    if currency == "USD":

        fx_records.append(
            {
                "row_index": index,
                "fx_rate": 1.0,
                "fx_source": "USD — direct",
                "fx_year": year,
            }
        )

        continue

    # --------------------------------------------------------
    # WORLD BANK OFFICIAL
    # --------------------------------------------------------

    key = (
        iso3,
        year,
    )

    if key in official_lookup:

        fx_records.append(
            {
                "row_index": index,
                "fx_rate": official_lookup[key],
                "fx_source": (
                    "World Bank — "
                    "official exchange rate"
                ),
                "fx_year": year,
            }
        )

        continue

    # --------------------------------------------------------
    # WORLD BANK ALTERNATIVE
    # --------------------------------------------------------

    if key in alternative_lookup:

        fx_records.append(
            {
                "row_index": index,
                "fx_rate": alternative_lookup[key],
                "fx_source": (
                    "World Bank — "
                    "alternative conversion factor"
                ),
                "fx_year": year,
            }
        )

        continue

    # --------------------------------------------------------
    # FRANKFURTER
    # --------------------------------------------------------

    if currency not in frankfurter_currencies:

        unresolved.append(
            {
                "row_index": index,
                "iso3_code": iso3,
                "currency": currency,
                "fiscal_year": year,
                "reason": (
                    "Currency not supported "
                    "by Frankfurter"
                ),
            }
        )

        continue

    cache_key = (
        currency,
        year,
    )

    if cache_key not in frankfurter_cache:

        print(
            f"Frankfurter: "
            f"{currency} / {year}"
        )

        try:

            frankfurter_cache[
                cache_key
            ] = get_frankfurter_rate(
                currency,
                year,
            )

        except requests.RequestException:

            frankfurter_cache[
                cache_key
            ] = None

    frank_rate = frankfurter_cache[
        cache_key
    ]

    if frank_rate is None:

        unresolved.append(
            {
                "row_index": index,
                "iso3_code": iso3,
                "currency": currency,
                "fiscal_year": year,
                "reason": (
                    "No Frankfurter "
                    "historical rate"
                ),
            }
        )

        continue

    fx_records.append(
        {
            "row_index": index,
            "fx_rate": float(
                frank_rate["rate"]
            ),
            "fx_source": frank_rate[
                "source"
            ],
            "fx_year": year,
        }
    )


# ============================================================
# APPLY FX
# ============================================================

section(
    "APPLYING FX RATES"
)

fx_df = pd.DataFrame(
    fx_records
)

print(
    f"FX records resolved: "
    f"{len(fx_df):,}"
)

print(
    f"FX records unresolved: "
    f"{len(unresolved):,}"
)


for item in fx_records:

    index = int(
        item["row_index"]
    )

    financials.at[
        index,
        "fx_rate_lcu_per_usd",
    ] = float(
        item["fx_rate"]
    )

    financials.at[
        index,
        "fx_source",
    ] = str(
        item["fx_source"]
    )

    financials.at[
        index,
        "fx_rate_year",
    ] = int(
        item["fx_year"]
    )


# ============================================================
# UNRESOLVED RECORD REPORT
# ============================================================

section(
    "FX COVERAGE RESULT"
)

print(
    f"Total records: "
    f"{len(financials):,}"
)

print(
    f"Resolved: "
    f"{len(fx_records):,}"
)

print(
    f"Unresolved: "
    f"{len(unresolved):,}"
)


if unresolved:

    unresolved_df = pd.DataFrame(
        unresolved
    )

    print()
    print(
        "UNRESOLVED FX RECORDS:"
    )

    print(
        unresolved_df[
            [
                "iso3_code",
                "currency",
                "fiscal_year",
                "reason",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "currency",
                "fiscal_year",
            ]
        )
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We deliberately STOP here.
    # No fabricated FX.
    # No nearest country.
    # No random rate.
    # --------------------------------------------------------

    raise ValueError(
        f"{len(unresolved):,} records "
        "still need FX rates. "
        "No USD dataset was created."
    )


# ============================================================
# FX VALIDATION
# ============================================================

section(
    "FX VALIDATION"
)

financials[
    "fx_rate_lcu_per_usd"
] = pd.to_numeric(
    financials[
        "fx_rate_lcu_per_usd"
    ],
    errors="coerce",
)

invalid_fx = (
    financials[
        "fx_rate_lcu_per_usd"
    ].isna()
    |
    (
        financials[
            "fx_rate_lcu_per_usd"
        ] <= 0
    )
    |
    ~np.isfinite(
        financials[
            "fx_rate_lcu_per_usd"
        ]
    )
)

print(
    f"Invalid FX records: "
    f"{int(invalid_fx.sum())}"
)

if invalid_fx.any():
    raise ValueError(
        "Invalid FX rates detected."
    )


# ============================================================
# USD CONVERSION
# ============================================================

section(
    "USD CONVERSION"
)

usd_columns = []

for column in MONETARY_COLUMNS:

    usd_column = (
        f"{column}_usd"
    )

    financials[
        usd_column
    ] = (
        financials[
            column
        ]
        /
        financials[
            "fx_rate_lcu_per_usd"
        ]
    )

    financials[
        usd_column
    ] = (
        financials[
            usd_column
        ].round(2)
    )

    usd_columns.append(
        usd_column
    )

    print(
        f"{column} -> "
        f"{usd_column}"
    )


# ============================================================
# USD VALIDATION
# ============================================================

section(
    "USD VALUE VALIDATION"
)

total_errors = 0

for column in usd_columns:

    invalid = (
        financials[column].notna()
        &
        ~np.isfinite(
            financials[column]
        )
    )

    count = int(
        invalid.sum()
    )

    print(
        f"{column}: "
        f"{count} invalid"
    )

    total_errors += count


if total_errors > 0:

    raise ValueError(
        "Invalid USD values detected."
    )


# ============================================================
# COLUMN ORDER
# ============================================================

base_columns = [
    "iso3_code",
    "bank_name",
    "fiscal_year",
    "total_assets",
    "total_deposits",
    "total_loans",
    "shareholders_equity",
    "operating_income",
    "net_income",
    "roe_percent",
    "roa_percent",
    "capital_adequacy_percent",
    "cost_income_ratio",
    "loan_to_deposit_ratio",
    "npl_ratio",
    "employees",
    "branches",
    "reporting_currency",
    "source",
]

metadata_columns = [
    "fx_rate_lcu_per_usd",
    "fx_rate_year",
    "fx_source",
]

financials = financials[
    base_columns
    + usd_columns
    + metadata_columns
]


# ============================================================
# FINAL ROW CHECK
# ============================================================

section(
    "FINAL VALIDATION"
)

print(
    f"Original rows: "
    f"{original_rows:,}"
)

print(
    f"Final rows: "
    f"{len(financials):,}"
)

if len(financials) != original_rows:

    raise ValueError(
        "Row count changed."
    )


# ============================================================
# FINAL DUPLICATE CHECK
# ============================================================

duplicates = (
    financials
    .groupby(
        [
            "iso3_code",
            "bank_name",
            "fiscal_year",
        ],
        dropna=False,
    )
    .size()
)

duplicates = duplicates[
    duplicates > 1
]

print(
    f"Duplicate groups: "
    f"{len(duplicates):,}"
)

if not duplicates.empty:

    raise ValueError(
        "Duplicate records detected."
    )


# ============================================================
# SAVE FX REFERENCE
# ============================================================

section(
    "SAVING FX REFERENCE"
)

FX_REFERENCE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fx_reference = financials[
    [
        "iso3_code",
        "fiscal_year",
        "reporting_currency",
        "fx_rate_lcu_per_usd",
        "fx_rate_year",
        "fx_source",
    ]
].drop_duplicates()

fx_reference.to_csv(
    FX_REFERENCE_FILE,
    index=False,
)

print(
    f"Saved: "
    f"{FX_REFERENCE_FILE}"
)


# ============================================================
# SAVE USD DATASET
# ============================================================

section(
    "SAVING USD DATASET"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

financials.to_csv(
    OUTPUT_FILE,
    index=False,
)

print(
    f"Saved: "
    f"{OUTPUT_FILE}"
)


# ============================================================
# RELOAD AND VERIFY
# ============================================================

section(
    "OUTPUT VERIFICATION"
)

check = pd.read_csv(
    OUTPUT_FILE
)

print(
    f"Saved rows: "
    f"{len(check):,}"
)

print(
    f"Saved columns: "
    f"{len(check.columns):,}"
)

if len(check) != original_rows:

    raise ValueError(
        "Saved row count does not match "
        "source row count."
    )

missing_usd = [
    column
    for column in usd_columns
    if column not in check.columns
]

print(
    f"Missing USD columns: "
    f"{len(missing_usd)}"
)

if missing_usd:

    raise ValueError(
        "USD columns missing: "
        + ", ".join(missing_usd)
    )


# ============================================================
# SUCCESS
# ============================================================

section(
    "USD NORMALIZATION COMPLETE"
)

print(
    f"Source records: "
    f"{original_rows:,}"
)

print(
    f"USD records: "
    f"{len(check):,}"
)

print(
    "FX priority:"
)

print(
    "1. World Bank official exact year"
)

print(
    "2. World Bank alternative exact year"
)

print(
    "3. Frankfurter currency/year"
)

print(
    "4. USD direct"
)

print()
print(
    "Original local-currency CSV unchanged."
)

print(
    "CSV ONLY."
)

print()
print(
    "USD dataset:"
)

print(
    OUTPUT_FILE
)

print()
print(
    "FX reference:"
)

print(
    FX_REFERENCE_FILE
)

print()
print(
    "# DONE"
)