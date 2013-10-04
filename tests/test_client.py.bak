from datetime import datetime

from tests import rundeck_api, rundeck_pwd, api_token, server, port, protocol, usr, pwd
from rundeck.client import Rundeck

from nose.tools import raises, with_setup


def test_api_token_auth():
    assert isinstance(rundeck_api.system_info(), dict), \
        'Failed to fetch System Info using API token auth'


# since password auth is not yet ready, pass these tests
@raises(NotImplementedError)
def test_pwd_auth():
    raise NotImplementedError('RundeckRun does not yet support password auth')


def test_system_info():
    system_info = rundeck_api.system_info()
    assert isinstance(system_info, dict), 'system_info did not return a dict'
    assert 'timestamp' in system_info, 'system_info does not have the \'timestamp\' key'
    assert 'datetime' in system_info['timestamp'], \
        'system_info timestamp doesn\'t have the \'datetime\' key'
    assert isinstance(system_info['timestamp']['datetime'], datetime)


def test_list_jobs():
    raise NotImplementedError('Test not implemented')


def test_list_projects():
    jobs = rundeck_api.list_projects()
    assert isinstance(jobs, list), 'list_projects did not return a list'


def test_get_project():
    raise NotImplementedError('Test not implemented')


def test_list_jobs():
    raise NotImplementedError('Test not implemented')


def test_run_job():
    raise NotImplementedError('Test not implemented')


def test_run_job_and_block():
    raise NotImplementedError('Test not implemented')


def test_transform_execution():
    raise NotImplementedError('Test not implemented')


def test_get_execution_info():
    raise NotImplementedError('Test not implemented')


def test_job_definition():
    raise NotImplementedError('Test not implemented')
