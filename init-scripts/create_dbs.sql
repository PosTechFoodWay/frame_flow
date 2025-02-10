-- init-scripts/create_dbs.sql

-- Create auth_db if it doesn't already exist
SELECT 'CREATE DATABASE auth_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'auth_db')
\gexec

-- Create upload_db if it doesn't already exist
SELECT 'CREATE DATABASE upload_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'upload_db')
\gexec

-- Create process_db if it doesn't already exist
SELECT 'CREATE DATABASE process_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'process_db')
\gexec