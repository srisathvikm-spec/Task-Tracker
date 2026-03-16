#!/bin/bash
# Create the test database used by pytest
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE task_tracker_test;
EOSQL
