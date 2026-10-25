#!/bin/bash 

set -o errexit 

set -o nounset 

set -o pipefail 

python << END 
import sys
import time
import psycopg2
suggest_unrecoverable_after = 30
start = time.time()
while True:
    try:
        psycopg2.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}"
        ) 
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("Waiting for database to become available...\n")
        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("This is taking longer than expected. The following exception is indicative of an unrecoverable error: '{}'\n".format(error))
        time.sleep(3) 
END

echo >&2 'Postgres is available'

exec "$@"
