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


def teardown():
    pass


@raises(NotImplementedError)
def test_node_xml():
    # xml(self)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_exec():
    # _exec(self, method, url, params=None, data=None, parse_response=True, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_system_info():
    assert rundeck_api.system_info().success, 'system_info call was unsuccessful'


def test_jobs():
    assert rundeck_api.jobs(test_job_proj).success, 'jobs call was unsuccessful'


def test_project_jobs():
    assert rundeck_api.project_jobs(test_job_proj).success, 'project_jobs call was unsuccessful'


def test_job_run():
    assert rundeck_api.job_run(test_job_id).success, 'job_run call was unsuccessful'
    time.sleep(1)
    assert rundeck_api.job_run(test_job_id, argString={'from': 'test_job_run'}).success, \
        'job_run with argument dict call was unsuccessful'
    time.sleep(1)
    assert rundeck_api.job_run(test_job_id, argString='-from test_job_run').success, \
        'job_run with argument string call was unsuccessful'


def test_jobs_export():
    assert rundeck_api.jobs_export(test_job_proj).status_code == requests.codes.ok, \
        'jobs_export call was unsuccessful'


@raises(NotImplementedError)
def test_jobs_import():
    # jobs_import(self, definition, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_job():
    assert rundeck_api.job(test_job_id).status_code == requests.codes.ok, \
        'job call was unsuccessful'


def test_delete_job():
    assert rundeck_api.delete_job(del_test_job_id).success, 'delete_job call was unsuccessful'


def test_jobs_delete():
    assert rundeck_api.jobs_delete([bulk1_del_test_job_id, bulk2_del_test_job_id]).success, \
        'jobs_delete call was unsuccessful'


def test_job_executions():
    assert rundeck_api.job_executions(test_job_id).success, 'job_executions call was unsuccessful'


def test_executions_running():
    assert rundeck_api.executions_running(test_job_proj).success, \
        'executions_running call was unsuccessful'


def test_execution():
    execution = transforms['execution'](rundeck_api.job_run(test_job_id))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution(execution_id).success, 'execution call was unsuccessful'


def test_executions():
    assert rundeck_api.executions(test_job_proj).success, 'executions call was unsuccessful'


def test_execution_output():
    execution = transforms['execution'](rundeck_api.job_run(test_job_id))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution_output(execution_id).status_code == requests.codes.ok, \
        'execution_output call was unsuccessful'


def test_execution_abort():
    execution = transforms['execution'](rundeck_api.job_run(test_job_id, argString={'sleep': 30}))
    time.sleep(1)
    execution_id = execution['id']
    assert rundeck_api.execution_abort(execution_id).success, 'execution_abort call was unsuccessful'
    time.sleep(1)
    execution = transforms['execution'](rundeck_api.execution(execution_id))
    assert execution['status'] == 'aborted', 'execution_abort status is not \'aborted\''


@raises(NotImplementedError)
def test_run_command():
    # run_command(self, project, command, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_script():
    # run_script(self, project, scriptFile, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_url():
    # run_url(self, project, scriptURL, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_projects():
    assert rundeck_api.projects().success, 'projects call was unsuccessful'


def test_project():
    assert rundeck_api.project(test_job_proj).success, 'project call was unsuccessful'


@raises(NotImplementedError)
def test_project_resources():
    # project_resources(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


def test_project_resources_update():
    host1 = RundeckNode(
        'host1', 'hostname1', 'user1', description='I <3 XML', tags=['hot'],
        attributes={'foo': 'bar'}
        )
    assert rundeck_api.project_resources_update(test_job_proj, [host1]).success, \
        'test_project_resources_update call was unsuccessful'


@raises(NotImplementedError)
def test_project_resources_refresh():
    # project_resources_refresh(self, project, providerURL=None, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_history():
    # history(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')
