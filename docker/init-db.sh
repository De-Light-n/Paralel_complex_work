#!/bin/bash
# PostgreSQL initialization script
# Creates separate databases for each microservice
# This demonstrates database-per-service pattern (Lab #4 requirement)

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create database for Asset Service
    CREATE DATABASE asset_db;
    GRANT ALL PRIVILEGES ON DATABASE asset_db TO postgres;
    
    -- Create database for Transaction Service
    CREATE DATABASE transaction_db;
    GRANT ALL PRIVILEGES ON DATABASE transaction_db TO postgres;
    
    -- Create database for Portfolio Service
    CREATE DATABASE portfolio_db;
    GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO postgres;
    
    -- Note: Analytics Service does not need a database (stateless)
    
    -- Display created databases
    \l
EOSQL

echo "All databases created successfully!"
