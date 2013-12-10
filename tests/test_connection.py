import time

from tests import rundeck_api

def test_response():
    response = rundeck_api.system_info()

    assert isinstance(response.body, basestring), 'response.body is not a string'
    assert isinstance(response.success, bool), 'response.success is not a bool'
    assert isinstance(response.message, basestring), 'response.message is not a string'
