CREATE TABLE IF NOT EXISTS objednavky (
    id            SERIAL PRIMARY KEY,
    zakaznik      VARCHAR(255) NOT NULL,
    produkt       VARCHAR(255) NOT NULL,
    cena_za_kus   NUMERIC(10, 2) NOT NULL,
    pocet_kusov   INTEGER NOT NULL,
    vytvorene     TIMESTAMP DEFAULT NOW()
);
