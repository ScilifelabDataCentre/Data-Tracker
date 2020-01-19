#!/bin/sh -ex

DBNAME=tracker

## SETUP SETTINGS
echo '>>> Preparing for testing: Add config.yaml'
cp test/appconfig_travis.yaml config.yaml

echo 'CONFIG'
cat config.yaml
echo '/CONFIG'

echo ">>> Test 1: Check that the backend doesn't crash immediately"

(cd backend && ../test/01_daemon_starts.sh)

echo '>>> Preparing: Loading database with generated data'

PYTHONPATH=backend python test/gen_test_db.py

echo '>>> Preparing: Start the backend'
COVERAGE_FILE=.coverage_backend coverage run backend/app.py 1>http_log.txt 2>&1 &
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

echo '>>> Test 2: Pytest'
# test browser
COVERAGE_FILE=.coverage_pytest PYTHONPATH=$PYTHONPATH:backend/ py.test backend/ --cov=backend/
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Test 3: Code evaluation'
pylint backend/*py
RETURN_VALUE=$((RETURN_VALUE + $?))
pydocstyle backend/*py
RETURN_VALUE=$((RETURN_VALUE + $?))
#flake8 backend/*py
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Finalising: Stop the backend'

curl http://127.0.0.1:5000/api/developer/quit
sleep 5 # Lets wait a little bit so the server has stopped

echo '>>> Finalising: Combine coverage'

coverage combine .coverage_pytest .coverage_backend

if [ -f .coverage ]; then
    coveralls
    coverage report
fi

exit "$RETURN_VALUE"
