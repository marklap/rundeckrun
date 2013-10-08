"""
:summary: Direct interaction with Rundeck server API

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
__docformat__ = "restructuredtext en"

from functools import partial
from string import maketrans, ascii_letters, digits
from urllib import urlencode

from connection import RundeckConnection
from exceptions import (
    InvalidResponseFormat,
    InvalidJobDefinitionFormat,
    InvalidDupeOption,
    InvalidUuidOption
    )
from defaults import (
    GET,
    POST,
    DELETE,
    DupeOption,
    UuidOption,
    JobDefFormat,
    ExecutionOutputFormat,
    )

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'
_JOB_ID_CHARS = ascii_letters + digits
_JOB_ID_TRANS_TAB = maketrans(_JOB_ID_CHARS, '#' * len(_JOB_ID_CHARS))
_JOB_ID_TEMPLATE = '########-####-####-####-############'


def api_version_check(api_version, required_version):
    """Raises a NotImplementedError if the api_version of the connection isn't sufficient
    """
    if api_version < required_version:
        raise NotImplementedError('Call requires API version {0} or higher'.format(required_version))


def cull_kwargs(api_keys, kwargs):
    """strips out the api_params from kwargs based on the list of api_keys
    !! modifies kwargs inline

    :Parameters:
        api_keys : list | set | tuple
            an iterable representing the keys of the key value pairs to pull out of kwargs
        kwargs : dict
            a dictionary of kwargs

    :return: a dictionary the API params
    :rtype: dict
    """
    return {k: kwargs.pop(k) for k in api_keys if k in kwargs}


class RundeckApi(object):
    """As close to the Rundeck API as possible

    :IVariables:
        connection : RundeckConnection
            a RundeckConnection instance
    """

    def __init__(self, server='localhost', protocol='http', port=4440, api_token=None, **kwargs):
        """ Initialize a Rundeck API instance

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
        """
        self.connection = RundeckConnection(
            server, protocol=protocol, port=port, api_token=api_token, **kwargs)
        self.requires_version = partial(api_version_check, self.connection.api_version)


    def execute_cmd(self, method, url, params=None, data=None, parse_response=True, **kwargs):
        """ Executes a request to Rundeck via the RundeckConnection

        :Parameters:
            method : str
                either rundeck.defaults.GET or rundeck.defaults.POST
            url : str
                Rundeck API endpoint URL
            params : dict
                dict of query string params
            data : dict
                dict of POST data

        :Keywords:
            \*\* : \*
                all remaining keyword arguments will be passed on to RundeckConnection.execute_cmd

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.connection.execute_cmd(method, url, params, data, parse_response, **kwargs)


    def system_info(self, **kwargs):
        """ Wraps `Rundeck API GET /system/info <http://rundeck.org/docs/api/index.html#system-info>`_

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, 'system/info', **kwargs)


    def jobs(self, project, **kwargs):
        """ Wraps `Rundeck API GET /jobs <http://rundeck.org/docs/api/index.html#listing-jobs>`_

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

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        # the keyword args jobExactFilter and groupPathExact require API version 2 so we will too
        # (but seriously... are you still using Rundeck API v1?!?!)
        self.requires_version(2)

        params = cull_kwargs(
            ('idlist', 'groupPath', 'jobFilter', 'jobExactFilter', 'groupPathExact'), kwargs)
        params['project'] = project

        return self.execute_cmd(GET, 'jobs', params=params, **kwargs)


    def project_jobs(self, project, **kwargs):
        """ Wraps `Rundeck API GET /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_

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

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(2)

        params = cull_kwargs(
            ('idlist', 'groupPath', 'jobFilter', 'jobExactFilter', 'groupPathExact'), kwargs)
        params['project'] = project

        return self.execute_cmd(GET, 'project/{0}/jobs'.format(project), params=params, **kwargs)


    def job_run(self, job_id, **kwargs):
        """Wraps `Rundeck API GET /job/[ID]/run <http://rundeck.org/docs/api/index.html#running-a-job>`_

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

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        params = cull_kwargs(('argString', 'loglevel', 'asUser', 'exclude-precedence', \
            'hostname', 'tags', 'os-name', 'os-family', 'os-arch', 'os-version', 'name', \
            'exlude-hostname', 'exlude-tags', 'exlude-os-name', 'exlude-os-family', \
            'exlude-os-arch', 'exlude-os-version', 'exlude-name'), kwargs)

        argString = params.get('argString', None)
        if isinstance(argString, dict):
            params['argString'] = ' '.join(['-' + k + ' ' + v for k, v in argString.items()])

        return self.execute_cmd(GET, 'job/{0}/run'.format(job_id), params=params, **kwargs)


    def jobs_export(self, project, **kwargs):
        """ Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

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

        :return: A Requests response
        :rtype: requests.models.Response
        """
        params = cull_kwargs(('fmt', 'idlist', 'groupPath', 'jobFilter'), kwargs)
        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self.execute_cmd(GET, 'projects', params=params, parse_response=False, **kwargs)


    def jobs_import(self, definition, **kwargs):
        """ Wraps `Rundeck API POST /jobs/import <http://rundeck.org/docs/api/index.html#importing-jobs>`_

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

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        data = cull_kwargs(('fmt', 'dupeOption', 'project', 'uuidOption'), kwargs)
        data['xmlBatch'] = definition
        if 'fmt' in data:
            data['format'] = data.pop('fmt')

        return self.execute_cmd(POST, '/jobs/import', data=data, **kwargs)


    def job(self, job_id, **kwargs):
        """ Wraps `Rundeck API GET /job/[ID] <http://rundeck.org/docs/api/index.html#getting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            fmt : str
                the format of the response one of JobDefFormat.values (default: 'xml')

        :return: A Requests response
        :rtype: requests.models.Response
        """
        params = cull_kwargs(('fmt',), kwargs)

        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self.execute_cmd(GET, '/job/{0}'.format(job_id), params=params, parse_response=False, **kwargs)


    def delete_job(self, job_id, **kwargs):
        """ Wraps `Rundeck API DELETE /job/[ID] <http://rundeck.org/docs/api/index.html#deleting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(DELETE, '/job/{0}'.format(job_id), **kwargs)


    def jobs_delete(self, idlist, **kwargs):
        """ Wraps `Rundeck API POST /jobs/delete <http://rundeck.org/docs/api/index.html#importing-jobs>`_

        :Parameters:
            idlist : str | list(str, ...)
                a list of job ids or a string of comma seperated job ids to delete

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        if not isinstance(idlist, basestring) and hasattr(idlist, '__iter__'):
            idlist = ','.join(idlist)

        params = {'idlist': idlist}

        return self.execute_cmd(POST, '/jobs/delete', params=params, **kwargs)


    def job_executions(self, job_id, **kwargs):
        """ Wraps `Rundeck API GET /job/[ID]/executions <http://rundeck.org/docs/api/index.html#getting-executions-for-a-job>`_

        :Parameters:
            job_id : str
                a Job ID

        :Keywords:
            status : str
                one of Status.values
            max : int
                maximum number of results to include in response (default: 20)
            offset : int
                offset for result set (default: 0)

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        params = cull_kwargs(('status', 'max', 'offset'), kwargs)
        return self.execute_cmd(POST, '/job/{0}/executions'.format(job_id), params=params, **kwargs)


    def executions_running(self, project, **kwargs):
        """ Wraps `Rundeck API GET /executions/running <http://rundeck.org/docs/api/index.html#listing-running-executions>`_

        :Parameters:
            project : str
                the name of a project

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        params = {'project': project}
        return self.execute_cmd(GET, '/executions/running', params=params, **kwargs)


    def execution(self, execution_id, **kwargs):
        """Wraps `Rundeck API GET /execution/[ID] <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, '/execution/{0}'.format(execution_id), **kwargs)


    def executions(self, project, **kwargs):
        """Wraps `Rundeck API GET /executions <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            api_params : DO NOT SUPPLY
                **see cull_kwargs decorator**
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


        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(5)

        params = cull_kwargs(('statusFilter', 'abortedbyFilter', 'userFilter', 'recentFilter', \
            'begin', 'end', 'adhoc', 'jobIdListFilter', 'excludeJobIdListFilter', \
            'jobListFilter', 'excludeJobListFilter', 'groupPath', 'groupPathExact', \
            'excludeGroupPath', 'excludeGroupPathExact', 'jobExactFilter', \
            'exludeJobExactFilter', 'max', 'offset'), kwargs)
        params['project'] = project

        return self.execute_cmd(GET, '/executions', params=params, **kwargs)


    def execution_output(self, execution_id, **kwargs):
        """Wraps `Rundeck API GET /execution/[ID]/output <http://rundeck.org/docs/api/index.html#execution-output>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :Keywords:
            fmt : str
                the format of the response one of ExecutionOutputFormat.values (default: 'text')
            offset : int
                byte offset to read from in the file, 0 indicates the beginning
            lastlines : int
                number of lines to retrieve from the end of the available output, overrides offset
            lastmod : int
                a unix millisecond timestamp; return output data received after this timestamp
            maxlines : int
                maximum number of lines to retrieve forward from the specified offset

        :return: A Requests response
        :rtype: requests.models.Response
        """
        params = cull_kwargs(('fmt', 'offset', 'lastlines', 'lastmod', 'maxlines'), kwargs)
        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self.execute_cmd(GET, '/execution/{0}/output'.format(execution_id), params=params, parse_response=False, **kwargs)


    def execution_abort(self, execution_id, **kwargs):
        """Wraps `Rundeck API GET /execution/[ID]/output <http://rundeck.org/docs/api/index.html#execution-output>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :Keywords:
            asUser : str
                specifies a username identifying the user who aborted the execution

        :return: A Requests response
        :rtype: requests.models.Response
        """
        params = cull_kwargs(('asUser',), kwargs)
        return self.execute_cmd(GET, '/execution/{0}/output'.format(execution_id), params=params, **kwargs)


    def projects(self, **kwargs):
        """ Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(POST, '/projects', **kwargs)


    def project(self, name, **kwargs):
        """ Wraps `Rundeck API /project/[NAME] <http://rundeck.org/docs/api/index.html#getting-project-info>`_

        :Parameters:
            name : str
                name of Project

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, 'project/{0}'.format(name), **kwargs)


    def project_resources(self, *args, **kwargs):
        """ Wraps `Rundeck API GET /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_
        """
        self.requires_version(2)
        raise NotImplementedError('Method not implemented')


    def project_resources_update(self, *args, **kwargs):
        """ Wraps `Rundeck API POST /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_
        """
        self.requires_version(2)
        raise NotImplementedError('Method not implemented')


    def project_resources_refresh(self, *args, **kwargs):
        """ Wraps `Rundeck API GET /project/[NAME]/resources/refresh <http://rundeck.org/docs/api/index.html#refreshing-resources-for-a-project>`_
        """
        self.requires_version(2)
        raise NotImplementedError('Method not implemented')


    def run_url(self, *args, **kwargs):
        """ Wraps `Rundeck API POST /run/url <http://rundeck.org/docs/api/index.html#running-adhoc-script-urls>`_
        """
        self.requires_version(4)
        raise NotImplementedError('Method not implemented')
