"""
:summary: Python client for interacting with Rundeck API

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
__docformat__ = "restructuredtext en"

import time
import errno
from string import maketrans, ascii_letters, digits
from datetime import datetime

from api import RundeckApi, RundeckApiNoisy
from connection import RundeckConnection
from transforms import transform
from util import child2dict, attr2dict, cull_kwargs
from exceptions import (
    RundeckServerError,
    JobNotFound,
    MissingProjectArgument,
    InvalidJobArgument,
    InvalidResponseFormat,
    InvalidJobDefinitionFormat,
    )
from defaults import (
    GET,
    POST,
    DELETE,
    Status,
    DupeOption,
    UuidOption,
    JobDefFormat,
    JOB_RUN_TIMEOUT,
    JOB_RUN_INTERVAL,
    )

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'
_JOB_ID_CHARS = ascii_letters + digits
_JOB_ID_TRANS_TAB = maketrans(_JOB_ID_CHARS, '#' * len(_JOB_ID_CHARS))
_JOB_ID_TEMPLATE = '########-####-####-####-############'
_RUNDECK_RESP_FORMATS = ('xml')  # TODO: yaml and json
_EXECUTION_COMPLETED = (Status.FAILED, Status.SUCCEEDED, Status.ABORTED)
_EXECUTION_PENDING = (Status.RUNNING,)


def is_job_id(job_id):
    """Checks if a Job ID "looks" like a UUID. It does not check if it exists as a job in Rundeck.
        And of course, a Rundeck Job ID does not have to be a "UUID". Any unique string will do
        so be prepared for false negatives if you customize your job ids.

    :Parameters:
        job_id : str
            a Rundeck Job ID

    :rtype: bool
    """
    if job_id and isinstance(job_id, basestring):
        return job_id.translate(_JOB_ID_TRANS_TAB) == _JOB_ID_TEMPLATE

    return False



class Rundeck(object):

    def __init__(self, server='localhost', protocol='http', port=4440, api_token=None, **kwargs):
        """Initialize a Rundeck API Client

        :Parameters:
            server : str
                hostname of the Rundeck server (default: localhost)
            protocol : str ('http'|'https')
                (default: 'http')
            port : int
                Rundeck server port (default: 4440)
            api_token : str
                valid Rundeck user API token

        :Keywords:
            usr : str
                Rundeck user name (used in place of api_token)
            pwd : str
                Rundeck user password (used in combo with usr)
            api_version : int
                Rundeck API version
            api : RundeckApi
                an instance of a RundeckApi or subclass of RundeckApi
            connection : RundeckConnection
                an instance of a RundeckConnection or instance of a subclass of RundeckConnection
        """
        api = kwargs.pop('api', None)
        if api is None:
            self.api = RundeckApiNoisy(
                server, protocol=protocol, port=port, api_token=api_token, **kwargs)
        elif isinstance(api, RundeckApi):
            self.api = api
        else:
            raise Exception('Supplied api argument is not a valide RundeckApi: {0}'.format(api))

    @transform('system_info')
    def system_info(self, **kwargs):
        """Get Rundeck Server System Info

        :return: a dict object representing the Rundeck system information
        :rtype: dict
        """
        return self.api.system_info(**kwargs)

    def get_job_id(self, project, name=None, **kwargs):
        """Fetch a Job ID that matches the filter criterea specified
            **WARNING**: if there is more than one job that matches the specified criteria, this
                will return the first job that Rundeck server includes in the list of matches

        :Parameters:
            project : str
                the name of a project

        :Keywords:
            idlist : str | list(str, ...)
                specify a comma-separated string or a list of Job IDs to include
            groupPath : str
                specify a group or partial group path to include all jobs within that group path
                or "*" for all groups or "-" to match top level jobs only (default: "*")
            jobFilter : str
                specify a job name filter; will match any job name that contains this string
            jobExactFilter : str
                specify an exact job name to match
            groupPathExact : str
                specify an exact group path to match or "-" to match the top level jobs only

        :return: a Rundeck Job ID
        :rtype: str
        """
        if name is not None:
            kwargs['jobExactFilter'] = name

        try:
            job_list = self.get_job_ids(project, limit=1, **kwargs)
        except JobNotFound:
            raise JobNotFound('Job {0!r} not found in Project {1!r}'.format(name, project))
        else:
            return job_list[0]

    def get_job_ids(self, project, **kwargs):
        """Fetch a list of Job IDs that match the filter criterea specified

        :Parameters:
            project : str
                the name of a project

        :Keywords:
            limit : int
                limit the result set to 1 or more jobs
            idlist : str | list(str, ...)
                specify a comma-separated string or a list of Job IDs to include
            groupPath : str
                specify a group or partial group path to include all jobs within that group path
                or "*" for all groups or "-" to match top level jobs only (default: "*")
            jobFilter : str
                specify a job name filter; will match any job name that contains this string
            jobExactFilter : str
                specify an exact job name to match
            groupPathExact : str
                specify an exact group path to match or "-" to match the top level jobs only

        :return: a list of Job IDs
        :rtype: list
        """
        limit = kwargs.pop('limit', None)
        resp = self.jobs(project, **kwargs)
        jobs = resp.as_dict

        job_ids = []
        if len(jobs) > 0:
            job_ids = [job['id'] for job in jobs]
        else:
            raise JobNotFound('No jobs in Project {0!r} matching criteria'.format(project))

        return job_ids[:limit]  # if limit is None, this will return the whole shebang

    @transform('jobs')
    def jobs(self, project, **kwargs):
        """Fetch a listing of jobs for a project

        :Parameters:
            project : str
                the name of a project

        :Keywords:
            limit : int
                limit the result set to 1 or more jobs
            idlist : str | list(str, ...)
                specify a comma-separated string or a list of Job IDs to include
            groupPath : str
                specify a group or partial group path to include all jobs within that group path
                or "*" for all groups or "-" to match top level jobs only (default: "*")
            jobFilter : str
                specify a job name filter; will match any job name that contains this string
            jobExactFilter : str
                specify an exact job name to match
            groupPathExact : str
                specify an exact group path to match or "-" to match the top level jobs only

        :return: a list of Jobs
        :rtype: list(dict, ...)
        """
        jobs = self.api.jobs(project, **kwargs)
        jobs.raise_for_error()
        return jobs

    def job_run_and_block(self, job_id, **kwargs):
        """Wraps job_run method and implements a blocking mechanism to wait for the job to
            complete (within reason, i.e. timeout and interval)

            See Rundeck.job_run docstring for additional keyword args

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            timeout : int | float
                how many seconds to wait for a completed status (default: 60)
            interval : int | float
                how many seconds to sleep between polling cycles (default: 3)

        :return: Details about the Job Execution
        :rtype: dict
        """
        timeout = kwargs.pop('timeout', JOB_RUN_TIMEOUT)
        interval = kwargs.pop('interval', JOB_RUN_INTERVAL)

        execution = self.job_run(job_id, **kwargs)

        exec_id = execution.as_dict['id']
        start = time.time()
        duration = 0

        while (duration < timeout):

            execution = self.execution(exec_id)

            try:
                exec_status = execution.as_dict['status']
            except AttributeError:
                # for some reason, we don't always immediately get an execution back from Rundeck
                #    loop once before we let the execption bubble up
                if duration == 0:
                    continue

            if exec_status in _EXECUTION_COMPLETED:
                break

            time.sleep(interval)
            duration = time.time() - start

        return execution

    @transform('execution')
    def job_run(self, job_id, **kwargs):
        """Kick off a Rundeck Job

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            argString : str | dict
                argument string to pass to job - if str, will be passed as-is
                else if dict will be converted to compatible string
            loglevel : str('DEBUG', 'VERBOSE', 'INFO', 'WARN', 'ERROR')
                logging level (default: 'INFO')
            asUser : str
                user to run the job as
            exclude-precedence : bool
                set the exclusion precedence (default True)
            hostname : str
                hostname inclusion filter
            tags : str
                tags inclusion filter
            os-name : str
                os-name inclusion filter
            os-family : str
                os-family inclusion filter
            os-arch : str
                os-arch inclusion filter
            os-version : str
                os-version inclusion filter
            name : str
                name inclusion filter
            exlude-hostname : str
                hostname exclusion filter
            exlude-tags : str
                tags exclusion filter
            exlude-os-name : str
                os-name exclusion filter
            exlude-os-family : str
                os-family exclusion filter
            exlude-os-arch : str
                os-arch exclusion filter
            exlude-os-version : str
                os-version exclusion filter
            exlude-name : str
                name exclusion filter

        :return: Details about the Job Execution
        :rtype: dict
        """
        return self.api.job_run(job_id, **kwargs)

    def jobs_export(self, project, **kwargs):
        """Export a the job definitions for a project in XML or YAML format

        :Parameters:
            name : str
                name of the project

        :Keywords:
            fmt : str ('xml'|'yaml')
                format of the definition string (default: 'xml')
            idlist : list(str, ...)
                a list of job ids to return
            groupPath : str
                a group path, partial group path or the special top level only
                char '-'
            jobFilter: str
                find job names that include this string

        :return: a job definition
        :rtype: str
        """
        return self.api.jobs_export(project, **kwargs)


    @transform('job_import_status')
    def jobs_import(self, definition, **kwargs):
        """Import a job definition in XML or YAML format

        :Parameters:
            definition : str
                a string representing a job definition

        :Keywords:
            fmt : str ('xml'|'yaml')
                format of the definition string (default: 'xml')
            dupeOption : str ('skip'|'create'|'update')
                a value to indicate the behavior when importing jobs which already exist
                (default: 'create')
            project : str
                specify the project that all job definitions should be imported to otherwise all
                job definitions must define a project
            uuidOption : str ('preserve'|'remove')
                preserve or remove UUIDs in imported jobs - preserve may fail if a UUID already
                exists

        :return: the results of the job import
        :rtype: dict
        """
        return self.api.jobs_import(definition, **kwargs)

    def job(self, job_id, **kwargs):
        """Export a job definition in XML or YAML format

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            fmt : str
                the format of the response one of JobDefFormat.values (default: 'xml')

        :return: a Job definition
        :rtype: str
        """
        return self.api.job(job_id, **kwargs)

    def delete_job(self, job_id, **kwargs):
        """Delete a job

        :Parameters:
            job_id : str
                Rundeck Job ID

        :return: success
        :rtype: bool
        """
        return self.api.delete_job(job_id, **kwargs).success

    def jobs_delete(self, idlist, **kwargs):
        """Bulk Job delete

        :Parameters:
            idlist : str | list(str, ...)
                a list of job ids or a string of comma seperated job ids to delete

        :return: results of the bulk delete with details
        :rtype: dict

        Example Response::

            {
            'requestCount': 3,
            'allsuccessful': False,
            'succeeded': {
                'id': '1234-123-123-12345',
                'message': 'success',
                },
            'failed': {
                'id': '9876-986-987-98765',
                'message': 'Job ID 9876-986-987-98765 does not exist',
                },
            }

        """
        # while we're waiting for https://github.com/dtolabs/rundeck/issues/588 to get resolved,
        #   we'll just use iterate over the list of ids and call delete_job - potentially REALLY
        #   painfully slow for large lists
        if isinstance(idlist, basestring):
            idlist = idlist.split(',')

        results = []
        for id in idlist:
            result = None
            try:
                result = self.delete_job(id)
            except RundeckServerError as exc:
                result = exc.rundecK_response
            results.append(result)

        return results


    @transform('executions')
    def job_executions(self, job_id, **kwargs):
        """Get a list of executions of a Job

        :Parameters:
            job : str
                A Job ID

        :Keywords:
            status : str
                one of Status.values
            max : int
                maximum number of results to include in response (default: 20)
            offset : int
                offset for result set (default: 0)

        :return: a list of Job Executions
        :rtype: list(dict, ...)
        """
        return self.api.job_executions(job_id, **kwargs)

    @transform('executions')
    def executions_running(self, project='*', **kwargs):
        """Retrieve running executions

        :Parameters:
            project : str
                the name of a project (use "*" for all projects - API v9+ required)

        :return: a list of Job Executions
        :rtype: list(dict, ...)
        """
        return self.api.executions_running(project, **kwargs)

    @transform('execution')
    def execution(self, execution_id, **kwargs):
        """Get the status of an execution

        :Parameters:
            execution_id : int
                Rundeck Job Execution ID

        :return: an Execution
        :rtype: dict
        """
        return self.api.execution(execution_id, **kwargs)

    @transform('executions')
    def executions(self, project, **kwargs):
        """Execution query

        :Parameters:
            project : str
                name of the project

        :Keywords:
            statusFilter : str
                one of Status.values
            abortedbyFilter : str
                user name that aborted the execution
            userFilter : str
                user name that initiated the execution
            recentFilter | str
                Use a simple text format to filter executions that completed within a period of
                time; the format is "XY" where 'X' is an integer and 'Y' is one of:

                    * `h`:hour
                    * `d`:day
                    * `w`:week
                    * `m`:month
                    * `y`:year

                So a value of "2w" would return executions that completed within the last two weeks

            begin : int | str
                either a unix millisecond timestamp or a W3C dateTime "yyyy-MM-ddTHH:mm:ssZ"
            end : int | str
                either a unix millisecond timestamp or a W3C dateTime "yyyy-MM-ddTHH:mm:ssZ"
            adhoc : bool
                includes adhoc executions
            jobIdListFilter : str | list
                one or more job ids to include
            excludeJobIdListFilter : str | list
                one or more job ids to exclude
            jobListFilter : str | list
                one or more full job group/name to include
            excludeJobListFilter : str | list
                one or more full job group/name to include
            groupPath : str
                a group or partial group path to include, special "-" setting matches top level
                jobs only
            groupPathExact : str
                an exact group path to include, special "-" setting matches top level jobs only
            excludeGroupPath : str
                a group or partial group path to exclude, special "-" setting matches top level
                jobs only
            excludeGroupPathExact : str
                an exact group path to exclude, special "-" setting matches top level jobs only
            jobExactFilter : str
                an exact job name
            exludeJobExactFilter : str
                an exact job name to exclude
            max : int
                maximum number of results to include in response (default: 20)
            offset : int
                offset for result set (default: 0)

        :return: a list of Job Executions
        :rtype: list(dict, ...)
        """
        return self.api.executions(project, **kwargs)

    @transform('execution_output')
    def _execution_output_json(self, execution_id, **kwargs):
        return self.api.execution_output(execution_id, **kwargs)

    def execution_output(self, execution_id, **kwargs):
        """Get the output for an execution in various formats

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :Keywords:
            fmt : str
                the format of the response one of ExecutionOutputFormat.values (default: 'json')
            raw : bool
                return the results of the Execution output request unmodified (default: False)
            offset : int
                byte offset to read from in the file, 0 indicates the beginning
            lastlines : int
                number of lines to retrieve from the end of the available output, overrides offset
            lastmod : int
                a unix millisecond timestamp; return output data received after this timestamp
            maxlines : int
                maximum number of lines to retrieve forward from the specified offset

        :return: Execution output
        :rtype: str | dict | RundeckResponse
        """
        raw = kwargs.pop('raw', None)
        fmt = kwargs.pop('fmt', None)
        if fmt is None and raw is None:
            fmt = 'json'
            raw = False

        if fmt is None:
            # default raw is in xml format
            fmt = 'xml'

        if raw or fmt == 'text':
            return self.api.execution_output(execution_id, fmt=fmt, **kwargs).text
        elif fmt == 'json':
            results = self._execution_output_json(execution_id, fmt=fmt, **kwargs)
            return results._as_dict_method(results)
        elif fmt == 'xml':
            return self.api.execution_output(execution_id, fmt=fmt, parse_response=True, **kwargs)





    @transform('projects')
    def projects(self, **kwargs):
        """Get a list of projects

        :return: a list of Rundeck projects
        :rtype: list(dict, ...)
        """
        return self.api.projects(**kwargs)

    @transform('project')
    def project(self, project, **kwargs):
        """Fetch a listing of jobs for a project

        :Parameters:
            project : str
                the name of a project

        :return: detailed information about a project
        :rtype: dict
        """
        return self.api.project(project, **kwargs)


    @transform('execution_abort')
    def execution_abort(self, execution_id, **kwargs):
        """Abort a running Job Execution

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :Keywords:
            asUser : str
                specifies a username identifying the user who aborted the execution

        :return: abort status information
        :rtype: dict
        """
        return self.api.execution_abort(execution_id, **kwargs)


    @transform('run_execution')
    def run_command(self, project, command, **kwargs):
        """Run a command

        :Parameters:
            project : str
                name of the project
            command : str
                the shell command string to run


        :Keywords:
            nodeThreadcount : int
                the number of threads to use
            nodeKeepgoing : bool
                if True, continue executing on other nodes even if some fail
            asUser : str
                specifies a username identifying the user who ran the command; requires runAs
                permission
            hostname : str
                hostname inclusion filter
            tags : str
                tags inclusion filter
            os-name : str
                os-name inclusion filter
            os-family : str
                os-family inclusion filter
            os-arch : str
                os-arch inclusion filter
            os-version : str
                os-version inclusion filter
            name : str
                name inclusion filter
            exlude-hostname : str
                hostname exclusion filter
            exlude-tags : str
                tags exclusion filter
            exlude-os-name : str
                os-name exclusion filter
            exlude-os-family : str
                os-family exclusion filter
            exlude-os-arch : str
                os-arch exclusion filter
            exlude-os-version : str
                os-version exclusion filter
            exlude-name : str
                name exclusion filter

        :return: Execution ID
        :rtype: int
        """
        return self.api.run_command(project, command, **kwargs)


    @transform('run_execution')
    def run_script(self, project, scriptFile, **kwargs):
        """Run a script downloaded from a URL

        :Parameters:
            project : str
                name of the project
            scriptFile : str
                a string containing the script file content


        :Keywords:
            argString : str | dict
                argument string to pass to job - if str, will be passed as-is
                else if dict will be converted to compatible string
            nodeThreadcount : int
                the number of threads to use
            nodeKeepgoing : bool
                if True, continue executing on other nodes even if some fail
            asUser : str
                specifies a username identifying the user who ran the command; requires runAs
                permission
            scriptInterpreter : str
                a command to use to run the script (requires API version 8 or higher)
            interpreterArgsQuoted : bool
                if True the script file and arguments will be quoted as the last argument to the
                scriptInterpreter (requires API version 8 or higher)
            hostname : str
                hostname inclusion filter
            tags : str
                tags inclusion filter
            os-name : str
                os-name inclusion filter
            os-family : str
                os-family inclusion filter
            os-arch : str
                os-arch inclusion filter
            os-version : str
                os-version inclusion filter
            name : str
                name inclusion filter
            exlude-hostname : str
                hostname exclusion filter
            exlude-tags : str
                tags exclusion filter
            exlude-os-name : str
                os-name exclusion filter
            exlude-os-family : str
                os-family exclusion filter
            exlude-os-arch : str
                os-arch exclusion filter
            exlude-os-version : str
                os-version exclusion filter
            exlude-name : str
                name exclusion filter

        :return: Execution ID
        :rtype: int
        """
        return self.api.run_script(project, scriptFile, **kwargs)


    @transform('run_execution')
    def run_url(self, project, scriptUrl, **kwargs):
        """Run a script downloaded from a URL

        :Parameters:
            project : str
                name of the project
            scriptUrl : str
                a URL referencing a script to download and run


        :Keywords:
            argString : str | dict
                argument string to pass to job - if str, will be passed as-is
                else if dict will be converted to compatible string
            nodeThreadcount : int
                the number of threads to use
            nodeKeepgoing : bool
                if True, continue executing on other nodes even if some fail
            asUser : str
                specifies a username identifying the user who ran the command; requires runAs
                permission
            scriptInterpreter : str
                a command to use to run the script (requires API version 8 or higher)
            interpreterArgsQuoted : bool
                if True the script file and arguments will be quoted as the last argument to the
                scriptInterpreter (requires API version 8 or higher)
            hostname : str
                hostname inclusion filter
            tags : str
                tags inclusion filter
            os-name : str
                os-name inclusion filter
            os-family : str
                os-family inclusion filter
            os-arch : str
                os-arch inclusion filter
            os-version : str
                os-version inclusion filter
            name : str
                name inclusion filter
            exlude-hostname : str
                hostname exclusion filter
            exlude-tags : str
                tags exclusion filter
            exlude-os-name : str
                os-name exclusion filter
            exlude-os-family : str
                os-family exclusion filter
            exlude-os-arch : str
                os-arch exclusion filter
            exlude-os-version : str
                os-version exclusion filter
            exlude-name : str
                name exclusion filter

        :return: Execution ID
        :rtype: int
        """
        return self.api.run_url(project, scriptUrl, **kwargs)


'''

    def projects(self, **kwargs):
        """Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self._exec(POST, 'projects', **kwargs)


    def project(self, project, **kwargs):
        """Wraps `Rundeck API /project/[NAME] <http://rundeck.org/docs/api/index.html#getting-project-info>`_

        :Parameters:
            project : str
                name of Project

        :return: A RundeckResponse`
        :rtype: RundeckResponse
        """
        return self._exec(GET, 'project/{0}'.format(urllib.quote(project)), **kwargs)


    def project_resources(self, project, **kwargs):
        """Wraps `Rundeck API GET /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            fmt : str
                the format of the response one of ExecutionOutputFormat.values (default: 'text')
            hostname : str
                hostname inclusion filter
            tags : str
                tags inclusion filter
            os-name : str
                os-name inclusion filter
            os-family : str
                os-family inclusion filter
            os-arch : str
                os-arch inclusion filter
            os-version : str
                os-version inclusion filter
            name : str
                name inclusion filter
            exlude-hostname : str
                hostname exclusion filter
            exlude-tags : str
                tags exclusion filter
            exlude-os-name : str
                os-name exclusion filter
            exlude-os-family : str
                os-family exclusion filter
            exlude-os-arch : str
                os-arch exclusion filter
            exlude-os-version : str
                os-version exclusion filter
            exlude-name : str
                name exclusion filter

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(2)

        params = cull_kwargs(('fmt', 'scriptInterpreter', 'interpreterArgsQuoted', 'hostname', \
            'tags', 'os-name', 'os-family', 'os-arch', 'os-version', 'name', 'exlude-hostname', \
            'exlude-tags', 'exlude-os-name', 'exlude-os-family', 'exlude-os-arch', \
            'exlude-os-version', 'exlude-name'), kwargs)

        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self._exec(GET, 'project/{0}/resources'.format(urllib.quote(project)), **kwargs)


    def project_resources_update(self, project, nodes, **kwargs):
        """Wraps `Rundeck API POST /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project
            nodes : list(RundeckNode, ...)
                a list of RundeckNode objects

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        headers = {'Content-Type': 'text/xml'}

        data = '<nodes>{0}</nodes>'.format('\n'.join([node.xml for node in nodes]))

        return self._exec(POST, 'project/{0}/resources'.format(urllib.quote(project)), data=data, headers=headers, **kwargs)


    def project_resources_refresh(self, project, providerUrl=None, **kwargs):
        """Wraps `Rundeck API POST /project/[NAME]/resources/refresh <http://rundeck.org/docs/api/index.html#refreshing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project
            providerUrl : str
                Specify the Resource Model Provider URL to refresh the resources from; otherwise
                the configured provider URL in the `project.properties` file will be used

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(2)

        data = {}
        if providerUrl is not None:
            data['providerUrl'] = providerUrl

        return self._exec(POST, 'project/{0}/resources/refresh'.format(project), data=data, **kwargs)




    def history(self, project, **kwargs):
        """Wraps `Rundeck API GET /history <http://rundeck.org/docs/api/index.html#listing-history>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            jobIdFilter : str
                include event for a job ID
            reportIdFilter : str
                include events for an event name
            userFilter : str
                include events created by user
            statFilter : str
                one of Status.values
            jobListFilter : str | list
                one or more full job group/name to include
            excludeJobListFilter : str | list
                one or more full job group/name to include
            recentFilter | str
                Use a simple text format to filter executions that completed within a period of
                time; the format is "XY" where 'X' is an integer and 'Y' is one of:

                    * `h`:hour
                    * `d`:day
                    * `w`:week
                    * `m`:month
                    * `y`:year

                So a value of "2w" would return executions that completed within the last two weeks

            begin : int | str
                either a unix millisecond timestamp or a W3C dateTime "yyyy-MM-ddTHH:mm:ssZ"
            end : int | str
                either a unix millisecond timestamp or a W3C dateTime "yyyy-MM-ddTHH:mm:ssZ"
            max : int
                maximum number of results to include in response (default: 20)
            offset : int
                offset for result set (default: 0)


        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(4)
        params = cull_kwargs(('jobIdFilter', 'reportIdFilter', 'userFilter', 'statFilter', \
            'jobListFilter', 'excludeJobListFilter', 'recentFilter', 'begin', 'end', 'max', \
            'offset'), kwargs)
        params['project'] = project
        return self._exec(GET, 'history', **kwargs)



    def job_definition(self, name, project=None, fmt=None):
        """Wraps `Rundeck API /job/[ID] <http://rundeck.org/docs/api/index.html#getting-a-job-definition>`_

        :Parameters:
            name : str
                Rundeck Job name (or ID) - if ID is provided project is not
                necessary
            project : str
                Rundeck Project name - if a Job ID is provided this is not
                necessary (default: None)
            fmt : str('python', 'xml' or 'yaml')
                if undefined, the Rundeck response will be converted to a Python dict
                (default: 'python')

        :return: a dict object representing a Rundeck Job or a the raw response
            from Rundeck in the requested format
        :rtype: dict | str
        """
        if self.is_job_id(name):
            id = name
        else:
            if not isinstance(project, basestring):
                raise MissingProjectArgument('job_definittion method requires project argument when name argument is not a Job ID')
            else:
                id = self.get_job_id(project, name)


        params = {}
        if fmt is None:
            # we're not ready to convert a job def xml format into a dict yet
            raise NotImplementedError('Conversion of a Job Defintion is not yet supported')
        else:
            if fmt in _RUNDECK_RESP_FORMATS:
                params['format'] = fmt
            else:
                raise InvalidResponseFormat(fmt)

        resp = self.execute_cmd(GET, '/job/{0}'.format(id), params=params)

        # TODO: support converting an xml Job Defintion (http://rundeck.org/docs/manpages/man5/job-v20.html) into a dict
        return resp.xml


    def delete_job(self, id):
        """Wraps `Rundeck API /job/[ID] <http://rundeck.org/docs/api/index.html#deleting-a-job-definition>`_
        """
        self.execute_cmd(DELETE, '/job/{0}'.format(id))


    def import_job(self, definition, *args, **kwargs):
        """Determines the type of argument passed in (file path or string) and calls the
            appropriate method passing along all extra arguments and keyword arguments

        :Parameters:
            definition : str
                the path to a job definition file or a string representing a job definition
                (automatically treated as job definition string if a newline character is found)

        :Keywords:
            definition_type : str ('file', 'string', 'auto')
                force the definition argument to be treated as a file or a string or
                attempt to determine automatically (default: 'auto')

        :return: a dict object representing a set of Rundeck status messages
        :rtype: dict
        """

        if definition_type == 'string' or '\n' in definition.strip():
            return self.import_job_definition_string(*args, **kwargs)
        elif definition_type in ('file', 'auto'):
            return self.import_job_definition_file(definition, *args, **kwargs)
        else:
            raise Exception('Could not determine the type of definition')


    def import_job_definition_string(self, definition, **kwargs):
        """Wraps `Rundeck API /jobs/import <http://rundeck.org/docs/api/index.html#importing-jobs>`_

        :Parameters:
            file_path : str
                the path to a job definition file or a string representing a job definition
                (automatically treated as job definition string if a newline character is found)

        :Keywords:
            fmt : str ('xml'|'yaml')
                format of the definition string (default: 'xml')
            dupeOption : str ('skip'|'create'|'update')
                a value to indicate the behavior when importing jobs which already exist
                (default: 'create')
            project : str
                specify the project that all job definitions should be imported to otherwise all
                job definitions must define a project
            uuidOption : str ('preserve'|'remove')
                preserve or remove UUIDs in imported jobs - preserve may fail if a UUID already
                exists

        :return: a dict object representing a set of Rundeck status messages
        :rtype: dict
        """

        fmt = kwargs.get('fmt', JobDefFormat.XML)
        if fmt not in JobDefFormat.values:
            fmt = JobDefFormat.XML

        dupe_option = kwargs.get('dupeOption', DupeOption.CREATE)
        if dupe_option not in DupeOption.values:
            dupe_option = DupeOption.CREATE

        uuid_option = kwargs.get('uuidOption', UuidOption.PRESERVE)
        if uuid_option not in UuidOption.values:
            uuid_option = UuidOption.PRESERVE

        # TODO: if this is not None, for API versions <8, maybe we could inject/update the job def
        #       as a convenience to the end user
        project = kwargs.get('project', None)

        api_kwargs = {
            'xmlBatch': definition,
            'format': fmt,
            'dupeOption': dupe_option,
            'uuidOption': uuid_option,
        }
        if project is not None:
            api_kwargs['project'] = project

        resp = self.execute_cmd(POST, '/jobs/import', data=api_kwargs)



    def import_job_definition_file(self, file_path, *args, **kwargs):
        """Convenience method for reading in the contents of a job definition file for import

        :Parameters:
            file_path : str
                the path to a readable job definition file

        :Keywords:
            file_format : str ('xml'|'yaml')
                if not specified it will be derived from the file extension (default: 'xml')

        :raise IOError: raised if job definition file can not be found or is not readable

        :return: a dict object representing a set of Rundeck status messages
        :rtype: dict
        """

        fmt = kwargs.pop('file_format', None)
        if fmt is None:
            fmt = JobDefFormat.XML
            fmt_specified = False
        else:
            fmt_specified = True

        definition = open(file_path, 'r').read()

        if not fmt_specified:
            fmt = os.path.splitext(file_name.strip())[1][1:].lower()

        if fmt not in JobDefFormat.values:
            raise InvalidJobDefinitionFormat('Invalid Job definition format: {0}'.format(fmt))

        return self.import_job_definition_string(definition, fmt=fmt, **kwargs)


'''
