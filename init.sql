DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'swapi') THEN
        CREATE DATABASE swapi;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'swapi') THEN
        CREATE USER swapi WITH PASSWORD '12345';
    END IF;

    GRANT ALL PRIVILEGES ON DATABASE swapi TO swapi;

    ALTER USER swapi CREATEDB;

END $$;