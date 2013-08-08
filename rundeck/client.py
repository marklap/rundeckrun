__docformat__ = "restructuredtext en"
"""
:summary: Python client for interacting with Rundeck API

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
import time
from string import maketrans, ascii_letters, digits
from datetime import datetime
from connection import RundeckConnection
from exceptions import (
    JobNotFound,
    MissingProjectArgument,
    InvalidJobArgument,
    InvalidResponseFormat,
    )
from defaults import GET, POST, Status

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'
_JOB_ID_CHARS = ascii_letters + digits
_JOB_ID_TRANS_TAB = maketrans(_JOB_ID_CHARS, '#' * len(_JOB_ID_CHARS))
_JOB_ID_TEMPLATE = '########-####-####-####-############'
_RUNDECK_RESP_FORMATS = ('xml')  # TODO: yaml and json
_EXECUTION_COMPLETED = (Status.FAILED, Status.SUCCEEDED, Status.ABORTED)
_EXECUTION_PENDING = (Status.RUNNING,)

class Rundeck(object):

    def __init__(self, server='localhost', protocol='http', port=4440, api_token=None, **kwargs):
        """ Initialize a Rundeck API Client

        :Parameters:
            server : str
                hostname of the Rundeck server (default: localhost)
            protocol : str
                either http or https (default: 'http')
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
        """
        self.connection = RundeckConnection(server, protocol=protocol, port=port, api_token=api_token, **kwargs)


    def execute_cmd(self, method, url, params=None, data=None):
        """ Executes a job via the RundeckConnection

        :Parameters:
            method : str
                either rundeck.defaults.GET or rundeck.defaults.POST
            url : str
                Rundeck API endpoint URL
            params : dict
                dict of query string params
            data : dict
                dict of POST data

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.connection.execute_cmd(method, url, params, data)


    def is_job_id(self, id):
        """ Checks if a Job ID "looks" valid - does not check if it exists as a
            job in Rundeck

        :Parameters:
            id : str
                a Rundeck Job ID

        :rtype: bool
        """
        if id and isinstance(id, basestring):
            return id.translate(_JOB_ID_TRANS_TAB) == _JOB_ID_TEMPLATE

        return False


    def get_job_id(self, project, name):
        """ Fetch the ID for a job

        :Parameters:
            project : str
                name of the Rundeck Project
            name : str
                name of the Rundeck Job

        :return: a Rundeck Job ID
        :rtype: str
        """
        found_jobs = self.list_jobs(project, jobExactFilter=name)
        if len(found_jobs) == 1:
            return found_jobs[0]['id']
        else:
            raise JobNotFound('Job {0!r} not found in Project {1!r}'.format(name, project))


    def system_info(self):
        """ Wraps `Rundeck API /system/info <http://rundeck.org/docs/api/index.html#system-info>`_

        :return: a dict object representing the Rundeck system information
        :rtype: dict
        """
        resp = self.execute_cmd(GET, 'system/info')
        ts = resp.body.find('timestamp').find('datetime').text
        ts_date = datetime.strptime(ts, _DATETIME_ISOFORMAT)

        system_info = {
            'timestamp': {'datetime': ts_date},
            'rundeck': {c.tag: c.text for c in resp.body.find('rundeck')},
            'os': {c.tag: c.text for c in resp.body.find('os')},
            'jvm': {c.tag: c.text for c in resp.body.find('jvm')},
        }

        # TODO: include stats returned in the response
        return system_info


    def list_projects(self):
        """ Wraps `Rundeck API /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

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
        """ Wraps `Rundeck API /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_

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
        """Wraps `Rundeck API /job/[ID]/run <http://rundeck.org/docs/api/index.html#running-a-job>`_

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
            loglevel : str
                one of 'DEBUG','VERBOSE','INFO','WARN','ERROR'
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


    def transform_execution(self, resp):
        """Transforms an Execution's RundeckXmlResponse object into a dict

        :Parameters:
            resp : RundeckXmlResponse
                A RundeckXmlResponse representing a Rundeck Execution

        :return: a dict object representing a Rundeck Execution
        :rtype: dict
        """
        execution = {}
        for execution_el in resp.body.iterfind('execution'):
            execution.update(execution_el.attrib)

            date_started = execution_el.find('date-started')
            if date_started is not None:
                execution['date-started'] = datetime.strptime(date_started.text, _DATETIME_ISOFORMAT)
                execution_el.remove(date_started)

            date_ended = execution_el.find('date-ended')
            if date_ended is not None:
                execution['date-ended'] = datetime.strptime(date_ended.text, _DATETIME_ISOFORMAT)
                execution_el.remove(date_ended)

            job_el = execution_el.find('job')
            if job_el is not None:
                execution['job'] = dict(job_el.attrib)
                execution['job'].update({c.tag: c.text for c in job_el})
                execution_el.remove(job_el)

            execution.update({e.tag: e.text for e in execution_el})

        return execution


    def get_execution_info(self, id):
        """Wraps `Rundeck API /execution/[ID] <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

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
            fmt : str
                one of ('xml','yaml') - if undefined, the Rundeck response will
                be converted to a Python dict (TODO) otherwise the raw response
                from Rundeck will be returned

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
