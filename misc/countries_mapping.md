# Countries Dataset Mapping

## Source
REST Countries API v5

## Destination Table
countries

| API Field | Database Column | Action | Notes |
|-----------|-----------------|--------|-------|
| names.common | country_name | Keep | Direct mapping |
| codes.alpha_2 | iso2_code | Keep | Direct mapping |
| codes.alpha_3 | iso3_code | Keep | Direct mapping |
| continents[0] | continent | Keep | Direct mapping |
| region | region_id | Transform | Lookup in regions table |
| coordinates.lat | latitude | Keep | Direct mapping |
| coordinates.lng | longitude | Keep | Direct mapping |
| currencies[0].code | currency_id | Transform | Lookup in currencies table |
| flag.url_png | country_flag_url | Keep | Direct mapping |
| links.official | official_website | Keep | Direct mapping |

## Ignored Fields

- Capital
- Population
- Languages
- Timezones
- Calling Codes
- Borders
- Government Type
- Maps
- Postal Code
- Area
- Translations
- Demonyms
- Driving Side
- Gini Coefficient
- Memberships