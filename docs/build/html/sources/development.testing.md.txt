# Testing

All tests require an active setup of the Data Tracker via docker-compose and test data in the database (See [System for development](development.quick_environment.md))

Most tests are not deterministic and do not restore the state of the db afterwards.

## Backend

The tests are found in `backend/tests`. Use the same `venv` used to add data to the database.

From the root of the repository:

```
PYTHONPATH=backend pytest backend
```

## Frontend

Frontend testing is implemented using the end-to-end testing solution Nightwatch.

Go to `test/nighwatch` and run `yarn install` to install the required packages.

Nightwatch can use multiple different browsers, but the tests have only been confirmed to work with Chrome.

To run the tests (in the `test/nighwatch` folder):

```
npx nightwatch collection.js --env chrome
```

## Continous integration

Automated backend testing is set up at Travis for any commits/pull requests. As Travis now have a credit system, it will need to be replaced with Github Actions at some point.

See `/.travis.yml` and `test/travis_script.sh` for information about what is run.

Frontend tests are currently *not* automated.