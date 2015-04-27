"""
:summary: Test rundeck.client.Rundeck

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015

:requires: nose
"""
__docformat__ = "restructuredtext en"

from nose.tools import raises


@raises(NotImplementedError)
def test_is_job_id():
    # is_job_id(job_id)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_system_info():
    # system_info(self, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_get_job_id():
    # get_job_id(self, project, name=None, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_get_job_ids():
    # get_job_ids(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_list_jobs():
    # list_jobs(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_job():
    # run_job(self, project, job_name, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_jobs_export():
    # jobs_export(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_import_job():
    # import_job(self, definition, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_import_job_file():
    # import_job_file(self, file_path, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_export_job():
    # export_job(self, job_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_delete_job():
    # delete_job(self, job_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_delete_jobs():
    # delete_jobs(self, idlist, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_list_job_executions():
    # list_job_executions(self, job_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_list_running_executions():
    # list_running_executions(self, project='*', **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_execution_status():
    # execution_status(self, execution_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_query_executions():
    # query_executions(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_get_execution_output():
    # get_execution_output(self, execution_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_abort_execution():
    # abort_execution(self, execution_id, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_adhoc_command():
    # run_adhoc_command(self, project, command, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_adhoc_script():
    # run_adhoc_script(self, project, scriptFile, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_run_adhoc_url():
    # run_adhoc_url(self, project, scriptUrl, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_list_projects():
    # list_projects(self, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_get_project():
    # get_project(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_list_project_resources():
    # list_project_resources(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_update_project_resources():
    # update_project_resources(self, project, nodes, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_refresh_project_resources():
    # refresh_project_resources(self, project, providerURL=None, **kwargs)
    raise NotImplementedError('Test not yet implemented')


@raises(NotImplementedError)
def test_get_project_history():
    # get_project_history(self, project, **kwargs)
    raise NotImplementedError('Test not yet implemented')

