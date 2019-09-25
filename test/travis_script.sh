#!/bin/sh -ex

DBNAME=portal

## SETUP SETTINGS
echo '>>> Preparing for testing: Fix settings.json file'
cp settings_sample.json settings.json

sed -i.tmp 's/"postgresHost" : "postgres host"/"postgresHost" : "127.0.0.1"/' settings.json
sed -i.tmp 's/"postgresPort" : 5432/"postgresPort" : 5433/' settings.json
sed -i.tmp "s/\"postgresName\" : \"portal\"/\"postgresName\" : \"$DBNAME\"/" settings.json

echo 'SETTINGS'
cat settings.json
echo '/SETTINGS'

echo '>>> Test 1: Load the portal schema'
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/data_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/user_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f test/data/test_data.sql "$DBNAME"


echo '>>> Test 2: Check that the backend starts'

(cd backend && ../test/01_daemon_starts.sh)


echo '>>> Test 4: The backend'
COVERAGE_FILE=.coverage_server coverage run backend/route.py --port=5000 --develop 1>http_log.txt 2>&1 &
BACKEND_PID=$!

sleep 2 # Lets wait a little bit so the server has started

exit_handler () {
    rv=$?
    # Ignore errors in the exit handler
    set +e
    # We want to make sure the background process has stopped, otherwise the
    # travis test will stall for a long time.
    kill -9 "$BACKEND_PID"

    echo 'THE HTTP LOG WAS:'
    cat http_log.txt

    exit "$rv"
}

trap exit_handler EXIT

echo '>>> Test 4A: Pytest'
# test browser
COVERAGE_FILE=.coverage_pytest PYTHONPATH=$PYTHONPATH:backend/ py.test backend/ --cov=backend/
RETURN_VALUE=$((RETURN_VALUE + $?))

# Quit the app
curl localhost:5000/developer/quit
sleep 2 # Lets wait a little bit so the server has stopped

echo '>>> Code evaluation'
pylint backend
RETURN_VALUE=$((RETURN_VALUE + $?))
pylint scripts
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Finalising: Combine coverage'

coverage combine .coverage_pytest .coverage_server

if [ -f .coverage ]; then
    coveralls
    coverage report
fi

exit "$RETURN_VALUE"
