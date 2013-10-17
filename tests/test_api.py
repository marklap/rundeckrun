import uuid
import time
from datetime import datetime
from pprint import pprint

from tests import (
    rundeck_client,
    rundeck_api,
    test_job_id,
    test_job_name,
    test_job_proj,
    test_job_def_tmpl,
    RundeckNode,
    )

del_test_job_id = str(uuid.uuid4())
bulk1_del_test_job_id = str(uuid.uuid4())
bulk2_del_test_job_id = str(uuid.uuid4())
imp_test_job_id = str(uuid.uuid4())


def setup():
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(del_test_job_id, 'TestJobApiDelete', test_job_proj))
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(bulk1_del_test_job_id, 'TestBulkJobApiDelete1', test_job_proj))
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(bulk2_del_test_job_id, 'TestBulkJobApiDelete1', test_job_proj))


def teardown():
    rundeck_api.delete_job(imp_test_job_id)


def test_system_info():
    assert rundeck_api.system_info().success, 'system_info call was unsuccessful'


def test_projects():
    assert rundeck_api.projects().success, 'projects call was unsuccessful'


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
    assert rundeck_api.jobs_export(test_job_proj).status_code == 200, 'jobs_export call was unsuccessful'


def test_jobs_delete():
    assert rundeck_api.jobs_delete([bulk1_del_test_job_id, bulk2_del_test_job_id]).success, \
        'jobs_delete call was unsuccessful'


def test_job_executions():
    assert rundeck_api.job_executions(test_job_id).success, 'job_executions call was unsuccessful'


def test_executions_running():
    assert rundeck_api.executions_running(test_job_proj).success, 'executions_running call was unsuccessful'


def test_job():
    assert rundeck_api.job(test_job_id).status_code == 200, 'job call was unsuccessful'


def test_delete_job():
    assert rundeck_api.delete_job(del_test_job_id).success, 'delete_job call was unsuccessful'


def test_execution():
    execution = rundeck_api.job_run(test_job_id)
    time.sleep(1)
    execution_id = execution.as_dict['result']['executions']['execution']['@id']
    assert rundeck_api.execution(execution_id).success, 'execution call was unsuccessful'


def test_execution_output():
    execution = rundeck_api.job_run(test_job_id)
    time.sleep(1)
    execution_id = execution.as_dict['result']['executions']['execution']['@id']
    assert rundeck_api.execution_output(execution_id).status_code == 200, 'execution_output call was unsuccessful'


def test_execution_abort():
    execution = rundeck_api.job_run(test_job_id, argString={'sleep': 30})
    time.sleep(1)
    execution_id = execution.as_dict['result']['executions']['execution']['@id']
    assert rundeck_api.execution_abort(execution_id).success, 'execution_abort call was unsuccessful'
    time.sleep(1)
    execution = rundeck_api.execution(execution_id)
    assert execution.as_dict['result']['executions']['execution']['@status'] == 'aborted', \
        'execution_abort status is not \'aborted\''


def test_run_command():
    assert False, 'test not yet implemented'


def test_run_script():
    assert False, 'test not yet implemented'


def test_run_url():
    assert False, 'test not yet implemented'


def test_project_resources():
    assert False, 'test not yet implemented'


def test_project_resources_update():
    host1 = RundeckNode('host1', 'hostname1', 'user1', description='I <3 XML', tags=['hot'], attributes={'foo': 'bar'})
    host2 = RundeckNode('host2', 'hostname2', 'user2', tags=['cold'], attributes={'foz': 'baz'})
    host3 = RundeckNode('host3', 'hostname3', 'user3')

    assert rundeck_api.project_resources_update(test_job_proj, [host1, host2, host3]).success, \
        'test_project_resources_update call was unsuccessful'

def test_executions():
    assert rundeck_api.executions(test_job_proj).success, 'executions call was unsuccessful'


def test_project():
    assert rundeck_api.project(test_job_proj).success, 'project call was unsuccessful'
