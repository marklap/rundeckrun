"""
:summary: Test rundeck.api.RundeckApi

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015

:requires: requests
"""
__docformat__ = "restructuredtext en"

import uuid
import time
import requests
from datetime import datetime
from pprint import pprint, pformat

from nose.tools import raises

from tests import (
    rundeck_client,
    rundeck_api,
    test_job_id,
    test_job_name,
    test_job_proj,
    test_job_def_tmpl,
    transforms,
    RundeckNode,
    )

del_test_job_id = str(uuid.uuid4())
bulk1_del_test_job_id = str(uuid.uuid4())
bulk2_del_test_job_id = str(uuid.uuid4())
imp_test_job_id = str(uuid.uuid4())


def setup():
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(
            del_test_job_id, test_job_name + 'ApiDelete', test_job_proj))
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(
            bulk1_del_test_job_id, test_job_name + 'ApiBulkDelete1', test_job_proj))
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(
            bulk2_del_test_job_id, test_job_name + 'ApiBulkDelete2', test_job_proj))
    time.sleep(3)


def teardown():
    pass


@raises(NotImplementedError)
def test_node_xml():
    # xml(self)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_exec():
    time.sleep(1)
    # _exec(self, method, url, params=None, data=None, parse_response=True, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_system_info():
    time.sleep(1)
    assert rundeck_api.system_info().success, 'system_info call was unsuccessful'


def test_jobs():
    time.sleep(1)
    assert rundeck_api.jobs(test_job_proj).success, 'jobs call was unsuccessful'


def test_project_jobs():
    time.sleep(1)
    assert rundeck_api.project_jobs(test_job_proj).success, 'project_jobs call was unsuccessful'


def test_job_run():
    time.sleep(3)
    assert rundeck_api.job_run(test_job_id).success, 'job_run call was unsuccessful'
    time.sleep(1)
    assert rundeck_api.job_run(test_job_id, argString={'from': 'test_job_run'}).success, \
        'job_run with argument dict call was unsuccessful'
    time.sleep(1)
    assert rundeck_api.job_run(test_job_id, argString='-from test_job_run').success, \
        'job_run with argument string call was unsuccessful'


def test_jobs_export():
    time.sleep(1)
    assert rundeck_api.jobs_export(test_job_proj).status_code == requests.codes.ok, \
        'jobs_export call was unsuccessful'


@raises(NotImplementedError)
def test_jobs_import():
    time.sleep(1)
    # jobs_import(self, definition, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_job():
    time.sleep(1)
    assert rundeck_api.job(test_job_id).status_code == requests.codes.ok, \
        'job call was unsuccessful'


def test_delete_job():
    time.sleep(1)
    response = rundeck_api.delete_job(del_test_job_id)
    assert response.status_code in (requests.codes.no_content, requests.codes.ok), \
        'delete_job call was unsuccessful'


def test_jobs_delete():
    time.sleep(1)
    assert rundeck_api.jobs_delete([bulk1_del_test_job_id, bulk2_del_test_job_id]).success, \
        'jobs_delete call was unsuccessful'


def test_job_executions():
    time.sleep(1)
    assert rundeck_api.job_executions(test_job_id).success, 'job_executions call was unsuccessful'


def test_executions_running():
    time.sleep(1)
    assert rundeck_api.executions_running(test_job_proj).success, \
        'executions_running call was unsuccessful'


def test_execution():
    time.sleep(1)
    execution = transforms['execution'](rundeck_api.job_run(test_job_id))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution(execution_id).success, 'execution call was unsuccessful'


def test_executions():
    time.sleep(1)
    assert rundeck_api.executions(test_job_proj).success, 'executions call was unsuccessful'


def test_execution_output():
    time.sleep(1)
    execution = transforms['execution'](rundeck_api.job_run(test_job_id))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution_output(execution_id).status_code == requests.codes.ok, \
        'execution_output call was unsuccessful'


def test_execution_abort():
    time.sleep(1)
    execution = transforms['execution'](rundeck_api.job_run(test_job_id, argString={'sleep': 30}))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution_abort(execution_id).success, 'execution_abort call was unsuccessful'
    time.sleep(1)
    execution = transforms['execution'](rundeck_api.execution(execution_id))
    assert execution['status'] == 'aborted', 'execution_abort status is not \'aborted\''


@raises(NotImplementedError)
def test_run_command():
    time.sleep(1)
    # run_command(self, project, command, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_script():
    time.sleep(1)
    # run_script(self, project, scriptFile, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_url():
    time.sleep(1)
    # run_url(self, project, scriptURL, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_projects():
    time.sleep(1)
    assert rundeck_api.projects().success, 'projects call was unsuccessful'


def test_project():
    time.sleep(1)
    assert rundeck_api.project(test_job_proj).success, 'project call was unsuccessful'


@raises(NotImplementedError)
def test_project_resources():
    time.sleep(1)
    # project_resources(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_project_resources_update():
    time.sleep(1)
    host1 = RundeckNode(
        'host1', 'hostname1', 'user1', description='I <3 XML', tags=['hot'],
        attributes={'foo': 'bar'}
        )
    assert rundeck_api.project_resources_update(test_job_proj, [host1]).success, \
        'test_project_resources_update call was unsuccessful'


@raises(NotImplementedError)
def test_project_resources_refresh():
    time.sleep(1)
    # project_resources_refresh(self, project, providerURL=None, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_history():
    time.sleep(1)
    # history(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')
