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
    JobNotFound,
    MissingProjectArgument,
    InvalidJobArgument,
    InvalidResponseFormat,
    InvalidJobDefinitionFormat,
    )
from defaults import GET, POST, DELETE, Status, DupeOption, UuidOption, JobDefFormat

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'
_JOB_ID_CHARS = ascii_letters + digits
_JOB_ID_TRANS_TAB = maketrans(_JOB_ID_CHARS, '#' * len(_JOB_ID_CHARS))
_JOB_ID_TEMPLATE = '########-####-####-####-############'
_RUNDECK_RESP_FORMATS = ('xml')  # TODO: yaml and json
_EXECUTION_COMPLETED = (Status.FAILED, Status.SUCCEEDED, Status.ABORTED)
_EXECUTION_PENDING = (Status.RUNNING,)


def is_job_id(job_id):
    """ Checks if a Job ID "looks" like a UUID. It does not check if it exists as a job in Rundeck.
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
        """ Initialize a Rundeck API Client

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


    def get_job_id(self, project, name=None, **kwargs):
        """ Fetch a Job ID that matches the filter criterea specified
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
        """ Fetch a list of Job IDs that match the filter criterea specified

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
        """ Fetch a listing of jobs for a project

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


    @transform('execution')
    def execution(self, execution_id, **kwargs):
        """ Get that status of an execution

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :return: an Execution
        :rtype: dict
        """
        execution = self.api.execution(execution_id, **kwargs)

    @transform('executions')
    def job_executions(self, job_id, **kwargs):
        """ Get a list of executions of a Job

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

        :return: an Execution
        :rtype: dict
        """
        return self.api.job_executions(job_id, **kwargs)

    @transform('system_info')
    def system_info(self, **kwargs):
        """ Get Rundeck Server System Info

        :return: a dict object representing the Rundeck system information
        :rtype: dict
        """
        return self.api.system_info(**kwargs)

    @transform('projects')
    def projects(self, **kwargs):
        """ Get a list of projects

        :return: a list of Rundeck Project names
        :rtype: list(str, ...)
        """
        return self.api.projects(**kwargs)


'''
    def list_projects(self):
        """ Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

        :return: a list of Rundeck Project names
        :rtype: list(str, ...)
        """
        resp = self.execute_cmd(GET, 'projects')
        return [{p.tag: p.text for p in p_el} for p_el in resp.body.iterfind('project')]


    def get_project(self, project):
        """ Wraps `Rundeck API /project/[NAME] <http://rundeck.org/docs/api/index.html#getting-project-info>`_

        :Parameters:
            project : str
                name of Project

        :return: dict object representing a Project definition
        :rtype: dict
        """
        raise NotImplementedError('get_project method not completed')


    def list_jobs(self, project, **kwargs):
        """ Wraps `Rundeck API GET /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            job_list : list(str, ...)
                a list of job names to included - Rundeck does not support this
                natively - filter applied on results of fetching all Jobs for
                a Project
            idlist : list(str, ...)
                a list of job ids to return
            groupPath : str
                a group path, partial group path or the special top level only
                char '-'
            jobFilter: str
                find job names that include this string
            jobExactFilter : str
                a specific job name to return
            groupPathExact : str
                a exact group path to match or the special top level only char
                '-'

        :return: a list of dict objects representing a Rundeck Jobs
        :rtype: list(dict, ...)
        """
        job_list = kwargs.get('job_list', None)
        if isinstance(job_list, basestring):
            job_list = [job_list]

        resp = self.execute_cmd(GET, 'project/{0}/jobs'.format(project), params=kwargs)
        jobs = []
        for job_el in resp.body.iterfind('job'):
            if job_list is not None:
                if job_el.find('name').text not in job_list:
                    continue
            job = {j.tag: j.text for j in job_el}
            job['id'] = job_el.attrib['id']
            jobs.append(job)
        return jobs


    def run_job(self, name, project=None, **kwargs):
        """Wraps `Rundeck API GET /job/[ID]/run <http://rundeck.org/docs/api/index.html#running-a-job>`_

        :Parameters:
            name : str
                Rundeck Job name (or ID) - if ID is provided project is not
                necessary
            project : str
                Rundeck Project name - if a Job ID is provided this is not
                necessary (default: None)

        :Keywords:
            block : bool
                if True, waits for a completed execution (default: False)
            timeout : int | float
                with block, how many seconds to wait for a completed status (default: 60)
            interval : int | float
                with block, how many seconds to sleep between polling cycles (default: 3)
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

        :return: a dict object representing a Rundeck Execution
        :rtype: dict
        """
        block = kwargs.pop('block', False)

        if not self.is_job_id(name):
            if isinstance(project, basestring):
                id = self.get_job_id(project, name)
            else:
                raise MissingProjectArgument('run_job method requires project argument when name argument is not a Job ID')
        else:
            id = name

        argString = kwargs.get('argString', None)
        if isinstance(argString, dict):
            kwargs['argString'] = ' '.join(['-' + k + ' ' + v for k, v in argString.items()])

        resp = self.execute_cmd(GET, 'job/{0}/run'.format(id), params=kwargs)
        execution = self.transform_execution(resp)

        if not block:
            return execution

        timeout = kwargs.pop('timeout', 60)
        interval = kwargs.pop('interval', 3)
        duration = 0

        exec_id = execution['id']
        start = time.time()

        while (duration < timeout):

            execution = self.get_execution_info(exec_id)

            if execution['status'] in _EXECUTION_COMPLETED:
                break

            time.sleep(interval)
            duration = time.time() - start

        return execution


    def run_job_and_block(self, name, project=None, **kwargs):
        """Executes Rundeck.run_job with the 'block' argument set to True
        """
        return self.run_job(name, project, block=True, **kwargs)


    def get_execution_info(self, id):
        """Wraps `Rundeck API GET /execution/[ID] <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            id : str
                Rundeck Job name (or ID) - if ID is provided project is not
                necessary

        :return: a dict object representing a Rundeck Job execution
        :rtype: dict
        """
        resp = self.execute_cmd(GET, '/execution/{0}'.format(id))
        return self.transform_execution(resp)


    def job_definition(self, name, project=None, fmt=None):
        """ Wraps `Rundeck API /job/[ID] <http://rundeck.org/docs/api/index.html#getting-a-job-definition>`_

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
        """ Wraps `Rundeck API /job/[ID] <http://rundeck.org/docs/api/index.html#deleting-a-job-definition>`_
        """
        self.execute_cmd(DELETE, '/job/{0}'.format(id))


    def import_job(self, definition, *args, **kwargs):
        """ Determines the type of argument passed in (file path or string) and calls the
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
        """ Wraps `Rundeck API /jobs/import <http://rundeck.org/docs/api/index.html#importing-jobs>`_

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
        """ Convenience method for reading in the contents of a job definition file for import

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
