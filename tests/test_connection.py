import time

from tests import rundeck_api

def test_response():
    response = rundeck_api.system_info()

    assert isinstance(response._response, basestring), 'response._response is not a string'
    assert isinstance(response.as_dict, dict), 'response.as_dict is not a dict'
    assert isinstance(response.success, bool), 'response.success is not a bool'
    assert isinstance(response.message, basestring), 'response.message is not a string'
