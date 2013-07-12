__docformat__ = "restructuredtext en"
"""
:summary: Python client for interacting with Rundeck API

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
from datetime import datetime
from connection import RundeckConnection
from defaults import RUNDECK_API_VERSION, GET, POST

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'

class Rundeck(object):

    def __init__(self, server, protocol='http', port=80, api_token=None, **kwargs):
        """ Initialize a Rundeck API Client

        :Parameters:
            server : str
                hostname of the Rundeck server
            protocol : str
                either http or https (default: 'http')
            port : int
                Rundeck server port (default: 80)
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
        return self.connection.execute_cmd(method, url, params, data)

    def system_info(self):
        """ Wraps `Rundeck API /system/info <http://rundeck.org/docs/api/index.html#system-info>`_

        :rtype: RundeckResponse
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

        :rtype: RundeckResponse
        """
        resp = self.execute_cmd(GET, 'projects')
        return [{p.tag: p.text for p in p_el} for p_el in resp.body.iterfind('project')]

    def list_jobs(self, project, **kwargs):
        """ Wraps `Rundeck API /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
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

        :rtype: RundeckResponse
        """
        resp = self.execute_cmd(GET, 'project/{0}/jobs'.format(project), params=kwargs)
        jobs = []
        for job_el in resp.body.iterfind('job'):
            job = {j.tag: j.text for j in job_el}
            job['id'] = job_el.attrib['id']
            jobs.append(job)
        return jobs

    def run_job_name(self, project, name, **kwargs):
        """ Performs lookup of a job name in a project to retrieve it's ID and
        run the job via Rundeck.run_job

        :Parameters:
            project : str
                name of the project the job lives in
            name : str
                name of the job

        :rtype: RundeckResponse
        """
        found_jobs = self.list_jobs(project, jobExactFilter=name)
        run_job = self.run_job(found_jobs[0]['id'], **kwargs)
        return run_job

    def run_job(self, id, **kwargs):
        """ Wraps `Rundeck API /job/[ID]/run <http://rundeck.org/docs/api/index.html#running-a-job>`_

        :Parameters:
            id : str
                UUID of a job to run

        :Keywords:
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

        :rtype: RundeckResponse
        """
        argString = kwargs.get('argString', None)
        if isinstance(argString, dict):
            kwargs['argString'] = ' '.join(['-' + k + ' ' + v for k, v in argString.items()])

        resp = self.execute_cmd(GET, 'job/{0}/run'.format(id), params=kwargs)
        execution = {}
        for execution_el in resp.body.iterfind('execution'):
            execution.update(execution_el.attrib)
            date_started = execution_el.find('date-started')
            if date_started is not None:
                execution['date-started'] = datetime.strptime(date_started.text, _DATETIME_ISOFORMAT)
                execution_el.remove(date_started)
            execution.update({e.tag: e.text for e in execution_el})

        return execution
