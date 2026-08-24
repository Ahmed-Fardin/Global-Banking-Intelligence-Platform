

SELECT
    conname,
    pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'currencies'::regclass;


SELECT
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'currencies';


ALTER TABLE currencies
ALTER COLUMN currency_name TYPE VARCHAR(100);

ALTER TABLE currencies
ALTER COLUMN currency_code TYPE VARCHAR(20);

ALTER TABLE currencies
ALTER COLUMN currency_symbol TYPE VARCHAR(20);