"""
:summary: Testing setup

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
"""
__docformat__ = "restructuredtext en"

import os
import logging
import uuid

from rundeck.client import Rundeck
from rundeck.api import RundeckApi, RundeckNode
from rundeck.transforms import _transforms as transforms

_RUNDECK_API_TOKEN_VAR = 'RUNDECK_API_TOKEN'
_RUNDECK_SERVER_VAR = 'RUNDECK_SERVER'
_RUNDECK_PORT_VAR = 'RUNDECK_PORT'
_RUNDECK_PROTOCOL_VAR = 'RUNDECK_PROTOCOL'
_RUNDECK_USR_VAR = 'RUNDECK_USR'
_RUNDECK_PWD_VAR = 'RUNDECK_PWD'
_RUNDECK_API_VERSION_VAR = 'RUNDECK_API_VERSION'

logger = logging.getLogger(__name__)
# logger = logging.getLogger('')  # for debugging
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

cwd = os.path.dirname(os.path.realpath(__file__))
job_def_file = 'TestJobDef.xml'
job_def_path = os.path.join(cwd, job_def_file)

api_token = os.environ.get(_RUNDECK_API_TOKEN_VAR, None)
server = os.environ.get(_RUNDECK_SERVER_VAR, 'localhost')
port = os.environ.get(_RUNDECK_PORT_VAR, 4440)
protocol = os.environ.get(_RUNDECK_PROTOCOL_VAR, 'http')
usr = os.environ.get(_RUNDECK_USR_VAR, None)
pwd = os.environ.get(_RUNDECK_PWD_VAR, None)
api_version = os.environ.get(_RUNDECK_API_VERSION_VAR, 11)

test_job_id = uuid.uuid4()
test_job_name = 'TestJobTest'
test_job_proj = 'TestProjectTest'
test_job_def_tmpl = """<joblist>
  <job>
    <id>{0}</id>
    <loglevel>INFO</loglevel>
    <sequence keepgoing='false' strategy='node-first'>
      <command>
        <node-step-plugin type='localexec'>
          <configuration>
            <entry key='command' value='echo "Hello World! (from:${{option.from}})"' />
          </configuration>
        </node-step-plugin>
      </command>
      <command>
        <node-step-plugin type='localexec'>
          <configuration>
            <entry key='command' value='sleep ${{option.sleep}}' />
          </configuration>
        </node-step-plugin>
      </command>
    </sequence>
    <description></description>
    <name>{1}</name>
    <context>
      <project>{2}</project>
      <options>
        <option name='from' value='Tester' />
        <option name='sleep' value='0' />
      </options>
    </context>
    <uuid>{0}</uuid>
  </job>
</joblist>"""
test_job_def = test_job_def_tmpl.format(test_job_id, test_job_name, test_job_proj)

assert any([api_token, all([usr, pwd])]), 'Must specify a Rundeck API token or username/' + \
        'password pair with the {0} environment variable or use'.format(_RUNDECK_API_TOKEN_VAR) + \
        ' both the {0}, and {1}  environment variables'.format(_RUNDECK_USR_VAR, _RUNDECK_PWD_VAR)

options = {
    'server': server,
    'protocol': protocol,
    'port': port,
    'verify_cert': False,
    'api_version': api_version,
}

if api_token is not None:
    options['api_token'] = api_token
else:
    if usr is not None and pwd is not None:
        options['usr'] = usr
        options['pwd'] = pwd
    else:
        assert False, 'Must specifiy username AND password with the {0} and {1} ' + \
            'environment variables'.format(_RUNDECK_USR_VAR, _RUNDECK_PWD_VAR)

rundeck_client = Rundeck(**options)
rundeck_api = RundeckApi(**options)


def setup():
    rundeck_api.jobs_import(test_job_def, uuidOption='preserve')


def teardown():
    jobs = transforms['jobs'](rundeck_api.jobs(test_job_proj))
    rundeck_api.jobs_delete([job['id'] for job in jobs])
