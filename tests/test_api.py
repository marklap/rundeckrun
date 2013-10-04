import uuid
from datetime import datetime

from tests import (
    rundeck_client,
    rundeck_api,
    test_job_id,
    test_job_name,
    test_job_proj,
    test_job_def_tmpl,
    )


# from nose.tools import raises, with_setup

del_test_job_id = uuid.uuid4()
imp_test_job_id = uuid.uuid4()

def setup():
    rundeck_api.jobs_import(
        test_job_def_tmpl.format(del_test_job_id, 'TestJobApiDelete', test_job_proj))

def teardown():
    rundeck_api.delete_job(imp_test_job_id)


def test_system_info():
    assert rundeck_api.system_info().success, 'system_info call was unsuccessful'


def test_projects():
    assert rundeck_api.projects().success, 'projects call was unsuccessful'


def test_project():
    assert rundeck_api.project(test_job_proj).success, 'project call was unsuccessful'


def test_project_jobs():
    assert rundeck_api.project_jobs(test_job_proj).success, 'project_jobs call was unsuccessful'


def test_job_run():
    assert rundeck_api.job_run(test_job_id).success, 'job_run call was unsuccessful'


def test_execution():
    assert rundeck_api.execution().success, 'execution call was unsuccessful'


def test_executions():
    assert rundeck_api.executions().success, 'executions call was unsuccessful'


def test_job():
    assert rundeck_api.job(test_job_id).success, 'job call was unsuccessful'


def test_delete_job():
    assert rundeck_api.delete_job(del_test_job_id).success, 'delete_job call was unsuccessful'


def test_jobs_import():
    job_def = test_job_def_tmpl.format(imp_test_job_id, 'TestJobApiImp', test_job_proj)
    assert rundeck_api.jobs_import(job_def).success, 'jobs_import call was unsuccessful'
