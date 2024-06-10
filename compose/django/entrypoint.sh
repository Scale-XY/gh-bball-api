#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -o errexit
# Exit if any of the intermediate steps in a pipeline fails.
set -o pipefail
# Exit if trying to use an uninitialized variable.
set -o nounset

# Function to check if PostgreSQL is ready
postgres_ready() {
    python << END
import sys
import psycopg2
import os

# Check if all required environment variables are set
required_env_vars = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT"]
for var in required_env_vars:
    if var not in os.environ:
        sys.exit(f"Environment variable {var} is not set: {os.environ}")

try:
    psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL to become available
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

# Execute the passed command
exec "$@"
