"""Tests for dataset requests."""

import json
import uuid
import requests

import helpers

# pylint: disable=redefined-outer-name

def test_country_list():
    """
    Request a list of countries

    Should also test e.g. pagination once implemented.
    """
    responses = helpers.make_request_all_roles('/api/countries')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['countries']) == 240
