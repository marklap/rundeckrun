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


    def execute_cmd(self, method, url, params=None, data=None):
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

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.connection.execute_cmd(method, url, params, data)


    def system_info(self):
        """ Wraps `Rundeck API GET /system/info <http://rundeck.org/docs/api/index.html#system-info>`_

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, 'system/info')


    def projects(self):
        """ Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, 'projects')


    def project(self, name):
        """ Wraps `Rundeck API /project/[NAME] <http://rundeck.org/docs/api/index.html#getting-project-info>`_

        :Parameters:
            name : str
                name of Project

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, 'project/{0}'.format(name))


    def project_jobs(self, name, **kwargs):
        """ Wraps `Rundeck API GET /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_

        :Parameters:
            name : str
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
        return self.execute_cmd(GET, 'project/{0}/jobs'.format(name), params=kwargs)


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
        argString = kwargs.get('argString', None)
        if isinstance(argString, dict):
            kwargs['argString'] = ' '.join(['-' + k + ' ' + v for k, v in argString.items()])

        return self.execute_cmd(GET, 'job/{0}/run'.format(job_id), params=kwargs)


    def execution(self, execution_id):
        """Wraps `Rundeck API GET /execution/[ID] <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(GET, '/execution/{0}'.format(execution_id))


    def executions(self, project, **kwargs):
        """Wraps `Rundeck API GET /executions <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

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


        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        self.requires_version(5)
        params = {'project': project}
        return self.execute_cmd(GET, '/execution/{0}'.format(execution_id), params=params)


    def job(self, job_id, **kwargs):
        """ Wraps `Rundeck API GET /job/[ID] <http://rundeck.org/docs/api/index.html#getting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            fmt : str
                the format of the response one of JobDefFormat.values (default: 'xml')

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        fmt = kwargs.get('fmt', JobDefFormat.XML)
        if fmt not in JobDefFormat.values:
            raise InvalidJobDefinitionFormat(fmt)

        params = {'format': fmt}

        return self.execute_cmd(GET, '/job/{0}'.format(job_id), params=params)


    def delete_job(self, job_id):
        """ Wraps `Rundeck API DELETE /job/[ID] <http://rundeck.org/docs/api/index.html#deleting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :return: A RundeckResponse
        :rtype: RundeckResponse
        """
        return self.execute_cmd(DELETE, '/job/{0}'.format(job_id))


    def jobs_import(self, definition, fmt='xml', **kwargs):
        """ Wraps `Rundeck API POST /jobs/import <http://rundeck.org/docs/api/index.html#importing-jobs>`_

        :Parameters:
            definition : str
                a string representing a job definition
            fmt : str ('xml'|'yaml')
                format of the definition string (default: 'xml')

        :Keywords:
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

        fmt = kwargs.get('fmt', JobDefFormat.XML)
        if fmt not in JobDefFormat.values:
            raise InvalidJobDefinitionFormat(fmt)

        dupe_option = kwargs.get('dupeOption', DupeOption.CREATE)
        if dupe_option not in DupeOption.values:
            raise InvalidDupeOption(dupe_option)

        uuid_option = kwargs.get('uuidOption', UuidOption.PRESERVE)
        if uuid_option not in UuidOption.values:
            raise InvalidUuidOption(uuid_option)

        project = kwargs.get('project', None)

        api_kwargs = {
            'xmlBatch': definition,
            'format': fmt,
            'dupeOption': dupe_option,
            'uuidOption': uuid_option,
        }
        if project is not None:
            api_kwargs['project'] = project

        return self.execute_cmd(POST, '/jobs/import', data=api_kwargs)
