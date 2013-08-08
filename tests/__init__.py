import os
import logging
import unittest
import rundeck.client import Rundeck

_RUNDECKAPITOKENENVVAR = 'RUNDECKAPITOKEN'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class RundeckTestCast(unittest.TestCast):
    """Base TestCase to test Rundeck server
    """

    @classmethod
    def setupClass(cls):
        api_token = os.environ.get(_RUNDECKAPITOKENENVVAR, None)

        if api_token is None:
            raise Exception(
                'Must specify a Rundeck API token with ' + \
                'the {0} environment variable'.format(_RUNDECKAPITOKENENVVAR))
        self.rundeck = Rundeck(api_token=api_token)

