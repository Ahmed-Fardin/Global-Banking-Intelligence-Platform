import pandas as pd

banks_data = [
    ("CUB", "Central Bank of Cuba", "CUP"),
    ("CUB", "Banco Nacional de Cuba", "CUP"),
    ("CUB", "Banco Popular de Ahorro", "CUP"),
    ("CUB", "Banco Metropolitano", "CUP"),
    ("CUB", "Banco de Crédito y Comercio", "CUP"),
    ("CUB", "Banco Internacional de Comercio", "CUP"),
    
    ("CZE", "Czech National Bank", "CZK"),
    ("CZE", "ČSOB", "CZK"),
    ("CZE", "Česká spořitelna", "CZK"),
    ("CZE", "Komerční banka", "CZK"),
    ("CZE", "UniCredit Bank Czech Republic", "CZK"),
    ("CZE", "Moneta Money Bank", "CZK"),
    
    ("COD", "Bank of Central African Congo", "CDF"),
    ("COD", "EquityBCDC", "USD"),
    ("COD", "Trust Merchant Bank", "USD"),
    ("COD", "BGFIBank RDC", "USD"),
    ("COD", "Ecobank DRC", "USD"),
    
    ("DNK", "Danmarks Nationalbank", "DKK"),
    ("DNK", "Jyske Bank", "DKK"),
    ("DNK", "Sydbank", "DKK"),
    ("DNK", "Spar Nord Bank", "DKK"),
    
    ("DJI", "Central Bank of Djibouti", "DJF"),
    ("DJI", "Banque pour le Commerce et l'Industrie Mer Rouge", "DJF"),
    ("DJI", "International Commercial Bank Djibouti", "DJF"),
    ("DJI", "Saba Islamic Bank", "DJF"),
    ("DJI", "East Africa Bank", "DJF"),
    ("DJI", "Exim Bank Djibouti", "DJF"),
    
    ("DMA", "National Bank of Dominica", "XCD"),
    ("DMA", "Republic Bank EC Dominica", "XCD"),
    ("DMA", "CIBC FirstCaribbean Dominica", "XCD"),
    ("DMA", "Royal Bank of Canada Dominica", "XCD"),
    ("DMA", "National Cooperative Credit Union", "XCD"),
    
    ("DOM", "Central Bank of the Dominican Republic", "DOP"),
    ("DOM", "Banco Popular Dominicano", "DOP"),
    ("DOM", "Banreservas", "DOP"),
    ("DOM", "BHD León", "DOP"),
    ("DOM", "Scotiabank República Dominicana", "DOP"),
    ("DOM", "Banco Santa Cruz", "DOP"),
    
    ("ECU", "Central Bank of Ecuador", "USD"),
    ("ECU", "Banco Pichincha", "USD"),
    ("ECU", "Banco Guayaquil", "USD"),
    ("ECU", "Banco del Pacífico", "USD"),
    ("ECU", "Produbanco", "USD"),
    ("ECU", "Banco Internacional Ecuador", "USD"),
    
    ("EGY", "Central Bank of Egypt", "EGP"),
    ("EGY", "National Bank of Egypt", "EGP"),
    ("EGY", "Banque Misr", "EGP"),
    ("EGY", "Commercial International Bank", "EGP"),
    ("EGY", "QNB Alahli", "EGP"),
    ("EGY", "Banque du Caire", "EGP"),
    
    ("SLV", "Central Reserve Bank of El Salvador", "USD"),
    ("SLV", "Banco Agrícola", "USD"),
    ("SLV", "Banco Cuscatlán", "USD"),
    ("SLV", "Davivienda El Salvador", "USD"),
    ("SLV", "Banco Promerica El Salvador", "USD"),
    ("SLV", "Banco Atlántida El Salvador", "USD"),
    
    ("GNQ", "BGFIBank Guinea Ecuatorial", "XAF"),
    ("GNQ", "CCEI Bank GE", "XAF"),
    ("GNQ", "BANGE", "XAF"),
    ("GNQ", "Ecobank Guinea Ecuatorial", "XAF"),
    ("GNQ", "Societe Generale Guinea Ecuatorial", "XAF"),
    
    ("ERI", "Bank of Eritrea", "ERN"),
    ("ERI", "Commercial Bank of Eritrea", "ERN"),
    ("ERI", "Housing and Commerce Bank of Eritrea", "ERN"),
    ("ERI", "Eritrean Investment and Development Bank", "ERN"),
    ("ERI", "Eritrean Development Bank", "ERN"),
    ("ERI", "Himbol Financial Services", "ERN"),
    
    ("EST", "Eesti Pank", "EUR"),
    ("EST", "LHV Pank", "EUR"),
    ("EST", "Swedbank Estonia", "EUR"),
    ("EST", "SEB Estonia", "EUR"),
    ("EST", "Coop Pank", "EUR"),
    
    ("SWZ", "Standard Bank Eswatini", "SZL"),
    ("SWZ", "FNB Eswatini", "SZL"),
    ("SWZ", "Nedbank Eswatini", "SZL"),
    ("SWZ", "Eswatini Bank", "SZL"),
    ("SWZ", "SwaziBank", "SZL"),
    
    ("ETH", "National Bank of Ethiopia", "ETB"),
    ("ETH", "Commercial Bank of Ethiopia", "ETB"),
    ("ETH", "Awash Bank", "ETB"),
    ("ETH", "Hibret Bank", "ETB"),
    ("ETH", "Cooperative Bank of Oromia", "ETB"),
    
    ("FJI", "ANZ Fiji", "FJD"),
    ("FJI", "Bank of Baroda Fiji", "FJD"),
    ("FJI", "HFC Bank Fiji", "FJD"),
    ("FJI", "BSP Fiji", "FJD"),
    
    ("FIN", "Bank of Finland", "EUR"),
    ("FIN", "Nordea Bank Finland", "EUR"),
    ("FIN", "OP Financial Group", "EUR"),
    ("FIN", "Danske Bank Finland", "EUR"),
    ("FIN", "Aktia Bank", "EUR"),
    ("FIN", "S-Bank", "EUR")
]

years = [2020, 2021, 2022, 2023, 2024, 2025]

columns = [
    "iso3_code", "bank_name", "fiscal_year", "total_assets", "total_deposits", 
    "total_loans", "shareholders_equity", "operating_income", "net_income", 
    "roe_percent", "roa_percent", "capital_adequacy_percent", "cost_income_ratio", 
    "loan_to_deposit_ratio", "npl_ratio", "employees", "branches", "reporting_currency", "source"
]

rows = []
for iso, bank, curr in banks_data:
    for year in years:
        rows.append({
            "iso3_code": iso,
            "bank_name": bank,
            "fiscal_year": year,
            "total_assets": None,
            "total_deposits": None,
            "total_loans": None,
            "shareholders_equity": None,
            "operating_income": None,
            "net_income": None,
            "roe_percent": None,
            "roa_percent": None,
            "capital_adequacy_percent": None,
            "cost_income_ratio": None,
            "loan_to_deposit_ratio": None,
            "npl_ratio": None,
            "employees": None,
            "branches": None,
            "reporting_currency": curr,
            "source": None
        })

df = pd.DataFrame(rows, columns=columns)
df.to_csv("bank_financials_2020_2025_template.csv", index=False)
print("CSV file generated successfully with 552 panel records.")