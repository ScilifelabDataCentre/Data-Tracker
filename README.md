# Data Tracker
[![Travis Status][travis-badge]][travis-link]
[![Coverage Status][codecov-badge]][codecov-link]

A system for tracking datasets.

[Setting up a development system](https://scilifelabdatacentre.github.io/SciLifeLab-Data-Tracker/development.quick_environment.html)

[Documentation](https://scilifelabdatacentre.github.io/SciLifeLab-Data-Tracker/)


## Containers
[Frontend](https://hub.docker.com/repository/docker/scilifelabdatacentre/data-tracker-frontend)
[Backend](https://hub.docker.com/repository/docker/scilifelabdatacentre/data-tracker-backend)

The backend requires a `config.yaml` file to be mounted to `/config.yaml`.

The frontend assumes that the backend is available at `/api`.



[travis-badge]: https://api.travis-ci.com/ScilifelabDataCentre/Data-Tracker.svg?branch=develop
[travis-link]: https://travis-ci.com/ScilifelabDataCentre/Data-Tracker

[codecov-badge]: https://codecov.io/gh/ScilifelabDataCentre/Data-Tracker/branch/develop/graph/badge.svg
[codecov-link]: https://codecov.io/gh/ScilifelabDataCentre/Data-Tracker
