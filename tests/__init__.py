import os
import logging

from rundeck.client import Rundeck

_RUNDECK_API_TOKEN_VAR = 'RUNDECK_API_TOKEN'
_RUNDECK_SERVER_VAR = 'RUNDECK_SERVER'
_RUNDECK_PORT_VAR = 'RUNDECK_PORT'
_RUNDECK_PROTOCOL_VAR = 'RUNDECK_PROTOCOL'
_RUNDECK_USR_VAR = 'RUNDECK_USR'
_RUNDECK_PWD_VAR = 'RUNDECK_PWD'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

api_token = os.environ.get(_RUNDECK_API_TOKEN_VAR, None)
server = os.environ.get(_RUNDECK_SERVER_VAR, 'localhost')
port = os.environ.get(_RUNDECK_PORT_VAR, 4440)
protocol = os.environ.get(_RUNDECK_PROTOCOL_VAR, 'http')
usr = os.environ.get(_RUNDECK_USR_VAR, None)
pwd = os.environ.get(_RUNDECK_PWD_VAR, None)

assert api_token is not None, 'Must specify a Rundeck API token with ' + \
    'the {0} environment variable'.format(_RUNDECK_API_TOKEN_VAR)
rundeck_api = Rundeck(server=server, protocol=protocol, port=port, api_token=api_token)

# Rundeck.connection still doesn't support password auth
assert usr is not None and pwd is not None, 'Must specify a valid Rundeck username and ' + \
    'password with {0} and {1} environment variables'.format(_RUNDECK_USR_VAR, _RUNDECK_PWD_VAR)
try:
    rundeck_pwd = Rundeck(server=server, protocol=protocol, port=port, usr=usr, pwd=pwd)
except NotImplementedError:
    rundeck_pwd = None
