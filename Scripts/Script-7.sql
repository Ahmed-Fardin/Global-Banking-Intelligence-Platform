CREATE TABLE banks (
    bank_id BIGSERIAL PRIMARY KEY,

    iso3_code CHAR(3) NOT NULL,

    bank_name VARCHAR(150) NOT NULL,

    bank_type VARCHAR(20) NOT NULL,

    bank_rank INTEGER NOT NULL,

    headquarters_city VARCHAR(100),

    official_website VARCHAR(255),

    swift_code VARCHAR(20),

    founded_year INTEGER,


    is_active BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT fk_banks_country
        FOREIGN KEY (iso3_code)
        REFERENCES countries(iso3_code)
);