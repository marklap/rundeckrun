"""
:summary: Test rundeck.connection.RundeckConnection

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
"""
__docformat__ = "restructuredtext en"

import time

from tests import rundeck_api
from rundeck.util import StringType

def test_response():
    response = rundeck_api.system_info()

    assert isinstance(response.body, StringType), 'response.body is not a string'
    assert isinstance(response.success, bool), 'response.success is not a bool'
    assert isinstance(response.message, StringType), 'response.message is not a string'
