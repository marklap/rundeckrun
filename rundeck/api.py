"""
:summary: Direct interaction with Rundeck server API

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
"""
__docformat__ = "restructuredtext en"

from functools import partial
from xml.sax.saxutils import quoteattr
try:
    from urllib import quote as urlquote
except ImportError:
    # python 3
    from urllib.parse import quote as urlquote

from .connection import RundeckConnectionTolerant, RundeckConnection
from .util import cull_kwargs, dict2argstring, StringType
from .exceptions import (
    InvalidResponseFormat,
    InvalidJobDefinitionFormat,
    InvalidDupeOption,
    InvalidUuidOption,
    HTTPError
    )
from .defaults import (
    GET,
    POST,
    DELETE,
    DupeOption,
    UuidOption,
    JobDefFormat,
    ExecutionOutputFormat,
    RUNDECK_API_VERSION,
    )

def api_version_check(api_version, required_version):
    """Raises a NotImplementedError if the api_version of the connection isn't sufficient
    """
    if api_version < required_version:
        raise NotImplementedError('Call requires API version {0} or higher'.format(required_version))


class RundeckNode(object):
    """Represents a Rundeck node; mainly for serializing to XML

    :IVariables:
        name : str
            name of the node
        hostname : str
            hostname of the node
        username : str
            username used for the remote connection
        description : str
            node description
        osArch : str
            the node's operating system architecture
        osFamily : str
            the node's operating system system family
        osName : str
            the node's operating system name
        tags : list(str, ...)
            a list of filtering tags
        editUrl : str
            URL to an external resource model editor service
        remoteUrl : str
            URL to an external resource model service
        attributes : dict
            a dictionary of name/value pairs to be used as node attributes
    """

    def __init__(self, name, hostname, username, **kwargs):
        """Initialize a RundeckNode instance

        :Parameters:
            name : str
                name of the node
            hostname : str
                hostname of the node
            username : str
                username used for the remote connection

        :Keywords:
            description : str
                node description
            osArch : str
                the node's operating system architecture
            osFamily : str
                the node's operating system system family
            osName : str
                the node's operating system name
            tags : list(str, ...)
                a list of filtering tags
            editUrl : str
                URL to an external resource model editor service
            remoteUrl : str
                URL to an external resource model service
            attributes : dict
                a dictionary of name/value pairs to be used as node attributes
        """
        self.name = name
        self.hostname = hostname
        self.username = username

        self.description = kwargs.get('description', None)
        self.osArch = kwargs.get('osArch', None)
        self.osFamily = kwargs.get('osFamily', None)
        self.osName = kwargs.get('osName', None)
        self.tags = kwargs.get('tags', None)
        self.editUrl = kwargs.get('editUrl', None)
        self.remoteUrl = kwargs.get('remoteUrl', None)
        self.attributes = kwargs.get('attributes', None)


    def serialize(self):
        """serializes the instance to XML

        :rtype: str
        :return: an XML string
        """
        node_attr_keys = (
            'name',
            'hostname',
            'username',
            'description',
            'osArch',
            'osFamily',
            'osName',
            'editUrl',
            'remoteUrl',
        )

        data = {k: getattr(self, k)
                    for k in node_attr_keys if getattr(self, k, None) is not None}

        if self.tags is not None and hasattr(self.tags, '__iter__'):
            data['tags'] = ','.join(self.tags)
        elif isinstance(self.tags, StringType):
            data['tags'] = self.tags

        node_xml_attrs = ' '.join(['{0}={1}'.format(k, quoteattr(v)) for k, v in data.items()])

        node_attributes = ''
        if self.attributes is not None and isinstance(self.attributes, dict):
            node_attributes = ''.join(['<attribute name="{0}" value="{1}" />'.format(k, v)
                                for k, v in self.attributes.items()])

        return '<node {0}>{1}</node>'.format(node_xml_attrs, node_attributes)

    @property
    def xml(self):
        return self.serialize()



class RundeckApiTolerant(object):
    """As close to the Rundeck API as possible. The "Tolerant" class does not throw exceptions
    when HTTP status codes are returned. Probably don't want/need to use this.

    :IVariables:
        connection : :class:`~rundeck.connection.RundeckConnection`
            a :class:`~rundeck.connection.RundeckConnection` instance
    """

    def __init__(self, server='localhost', protocol='http', port=4440, api_token=None, **kwargs):
        """Initialize a Rundeck API instance

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
            base_path : str
                Custom base URL path for Rundeck server URLs [default: None]
            usr : str
                Rundeck user name (used in place of api_token)
            pwd : str
                Rundeck user password (used in combo with usr)
            api_version : int
                Rundeck API version
            connection : :class:`~rundeck.connection.RundeckConnection`
                an instance of a :class:`~rundeck.connection.RundeckConnection` or instance of a
                subclass of :class:`~rundeck.connection.RundeckConnection`
        """
        connection = kwargs.pop('connection', None)

        if connection is None:
            self.connection = RundeckConnection(
                server=server, protocol=protocol, port=port, api_token=api_token, **kwargs)
        elif isinstance(connection, RundeckConnectionTolerant):
            self.connection = connection
        else:
            raise Exception('Supplied connection argument is not a valid RundeckConnection: {0}'.format(connection))

        self.requires_version = partial(api_version_check, self.connection.api_version)


    def _exec(self, method, url, params=None, data=None, parse_response=True, **kwargs):
        """ Executes a request to Rundeck via the RundeckConnection

        :Parameters:
            method : str
                either :class:`~rundeck.defaults.GET` or :class:`~rundeck.defaults.POST`
            url : str
                Rundeck API endpoint URL
            params : dict
                dict of query string params
            data : dict
                dict of POST data

        :Keywords:
            \*\* : \*
                all remaining keyword arguments will be passed on to RundeckConnection._exec

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        return self.connection.call(
            method, url, params=params, data=data, parse_response=parse_response, **kwargs)


    def system_info(self, **kwargs):
        """Wraps `Rundeck API GET /system/info <http://rundeck.org/docs/api/index.html#system-info>`_

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        return self._exec(GET, 'system/info', **kwargs)


    def jobs(self, project, **kwargs):
        """Wraps `Rundeck API GET /jobs <http://rundeck.org/docs/api/index.html#listing-jobs>`_

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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = cull_kwargs(
            ('idlist', 'groupPath', 'jobFilter', 'jobExactFilter', 'groupPathExact'), kwargs)

        if 'jobExactFilter' in params or 'groupPathExact' in params:
            self.requires_version(2)

        params['project'] = project

        return self._exec(GET, 'jobs', params=params, **kwargs)


    def project_jobs(self, project, **kwargs):
        """ Simulates `Rundeck API GET /project/[NAME]/jobs <http://rundeck.org/docs/api/index.html#listing-jobs-for-a-project>`_
            **Note**: Can't find any difference between this and /jobs, so this method is just a
                synonym for the `jobs` method

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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        return self.jobs(project, **kwargs)


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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = cull_kwargs(('argString', 'loglevel', 'asUser', 'exclude-precedence', \
            'hostname', 'tags', 'os-name', 'os-family', 'os-arch', 'os-version', 'name', \
            'exlude-hostname', 'exlude-tags', 'exlude-os-name', 'exlude-os-family', \
            'exlude-os-arch', 'exlude-os-version', 'exlude-name'), kwargs)

        argString = params.get('argString', None)
        if argString is not None:
            params['argString'] = dict2argstring(argString)

        return self._exec(GET, 'job/{0}/run'.format(job_id), params=params, **kwargs)


    def jobs_export(self, project, **kwargs):
        """Wraps `Rundeck API GET /jobs/export <http://rundeck.org/docs/api/index.html#exporting-jobs>`_

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
        params['project'] = project

        return self._exec(GET, 'jobs/export', params=params, parse_response=False, **kwargs)


    def jobs_import(self, definition, **kwargs):
        """Wraps `Rundeck API POST /jobs/import <http://rundeck.org/docs/api/index.html#importing-jobs>`_

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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        data = cull_kwargs(('fmt', 'dupeOption', 'project', 'uuidOption'), kwargs)
        data['xmlBatch'] = definition
        if 'fmt' in data:
            data['format'] = data.pop('fmt')

        return self._exec(POST, 'jobs/import', data=data, **kwargs)


    def job(self, job_id, **kwargs):
        """Wraps `Rundeck API GET /job/[ID] <http://rundeck.org/docs/api/index.html#getting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :Keywords:
            fmt : str
                the format of the response one of :class:`~rundeck.defaults.JobDefFormat` ``values``
                (default: 'xml')

        :return: A Requests response
        :rtype: requests.models.Response
        """
        params = cull_kwargs(('fmt',), kwargs)

        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self._exec(GET, 'job/{0}'.format(job_id), params=params, parse_response=False, **kwargs)


    def delete_job(self, job_id, **kwargs):
        """Wraps `Rundeck API DELETE /job/[ID] <http://rundeck.org/docs/api/index.html#deleting-a-job-definition>`_

        :Parameters:
            job_id : str
                Rundeck Job ID

        :return: A Requests response
        :rtype: requests.models.Response
        """
        return self._exec(DELETE, 'job/{0}'.format(job_id), parse_response=False, **kwargs)


    def jobs_delete(self, idlist, **kwargs):
        """Wraps `Rundeck API POST /jobs/delete <http://rundeck.org/docs/api/index.html#importing-jobs>`_

        :Parameters:
            ids : str | list(str, ...)
                a list of job ids or a string of comma seperated job ids to delete

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        if not isinstance(idlist, StringType) and hasattr(idlist, '__iter__'):
            idlist = ','.join(idlist)

        data = {
            'idlist': idlist,
            }

        try:
            return self._exec(POST, 'jobs/delete', data=data, **kwargs)
        except Exception as exc:
            # TODO: what on earth did I do there?!?! need to fix this
            raise


    def job_executions(self, job_id, **kwargs):
        """Wraps `Rundeck API GET /job/[ID]/executions <http://rundeck.org/docs/api/index.html#getting-executions-for-a-job>`_

        :Parameters:
            job_id : str
                a Job ID

        :Keywords:
            status : str
                one of :class:`~rundeck.defaults.Status` ``values``
            max : int
                maximum number of results to include in response (default: 20)
            offset : int
                offset for result set (default: 0)

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = cull_kwargs(('status', 'max', 'offset'), kwargs)
        return self._exec(GET, 'job/{0}/executions'.format(job_id), params=params, **kwargs)


    def executions_running(self, project, **kwargs):
        """Wraps `Rundeck API GET /executions/running <http://rundeck.org/docs/api/index.html#listing-running-executions>`_

        :Parameters:
            project : str
                the name of a project

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = {'project': project}
        return self._exec(GET, 'executions/running', params=params, **kwargs)


    def execution(self, execution_id, **kwargs):
        """Wraps `Rundeck API GET /execution/[ID] <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        return self._exec(GET, 'execution/{0}'.format(execution_id), **kwargs)


    def executions(self, project, **kwargs):
        """Wraps `Rundeck API GET /executions <http://rundeck.org/docs/api/index.html#getting-execution-info>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            statusFilter : str
                one of :class:`~rundeck.defaults.Status` ``values``
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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(5)

        params = cull_kwargs(('statusFilter', 'abortedbyFilter', 'userFilter', 'recentFilter', \
            'begin', 'end', 'adhoc', 'jobIdListFilter', 'excludeJobIdListFilter', \
            'jobListFilter', 'excludeJobListFilter', 'groupPath', 'groupPathExact', \
            'excludeGroupPath', 'excludeGroupPathExact', 'jobExactFilter', \
            'exludeJobExactFilter', 'max', 'offset'), kwargs)
        params['project'] = project

        return self._exec(GET, 'executions', params=params, **kwargs)


    def execution_output(self, execution_id, **kwargs):
        """Wraps `Rundeck API GET /execution/[ID]/output <http://rundeck.org/docs/api/index.html#execution-output>`_

        :Parameters:
            execution_id : str
                Rundeck Job Execution ID

        :Keywords:
            fmt : str
                the format of the response one of :class:`~rundeck.defaults.ExecutionOutputFormat`
                ``values`` (default: 'text')
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

        parse_response = kwargs.pop('parse_response', False)

        return self._exec(GET, 'execution/{0}/output'.format(execution_id), params=params, parse_response=parse_response, **kwargs)


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
        return self._exec(GET, 'execution/{0}/abort'.format(execution_id), params=params, **kwargs)


    def run_command(self, project, command, **kwargs):
        """Wraps `Rundeck API GET /run/command <http://rundeck.org/docs/api/index.html#running-adhoc-commands>`_

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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = cull_kwargs(('nodeThreadcount', 'nodeKeepgoing', 'asUser', 'hostname', 'tags', \
            'os-name', 'os-family', 'os-arch', 'os-version', 'name', 'exlude-hostname', \
            'exlude-tags', 'exlude-os-name', 'exlude-os-family', 'exlude-os-arch', \
            'exlude-os-version', 'exlude-name'), kwargs)

        params['project'] = project
        params['exec'] = command

        return self._exec(GET, 'run/command', params=params, **kwargs)


    def run_script(self, project, scriptFile, **kwargs):
        """Wraps `Rundeck API POST /run/script <http://rundeck.org/docs/api/index.html#running-adhoc-scripts>`_

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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        params = cull_kwargs(('argString', 'nodeThreadcount', 'nodeKeepgoing', 'asUser', \
            'scriptInterpreter', 'interpreterArgsQuoted', 'hostname', 'tags', 'os-name', \
            'os-family', 'os-arch', 'os-version', 'name', 'exlude-hostname', 'exlude-tags', \
            'exlude-os-name', 'exlude-os-family', 'exlude-os-arch', 'exlude-os-version', \
            'exlude-name'), kwargs)

        params['project'] = project
        files = {'scriptFile': scriptFile}

        if 'scriptInterpreter' in params or 'interpreterArgsQuoted' in params:
            self.requires_version(8)

        argString = params.get('argString', None)
        if argString is not None:
            params['argString'] = dict2argstring(argString)


        return self._exec(POST, 'run/script', params=params, files=files, **kwargs)


    def run_url(self, project, scriptURL, **kwargs):
        """Wraps `Rundeck API POST /run/url <http://rundeck.org/docs/api/index.html#running-adhoc-script-urls>`_
        Requires API version >4

        :Parameters:
            project : str
                name of the project
            scriptURL : str
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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(4)

        data = cull_kwargs(('argString', 'nodeThreadcount', 'nodeKeepgoing', 'asUser', \
            'scriptInterpreter', 'interpreterArgsQuoted', 'hostname', 'tags', 'os-name', \
            'os-family', 'os-arch', 'os-version', 'name', 'exlude-hostname', 'exlude-tags', \
            'exlude-os-name', 'exlude-os-family', 'exlude-os-arch', 'exlude-os-version', \
            'exlude-name'), kwargs)

        data['project'] = project
        data['scriptURL'] = scriptURL

        if 'scriptInterpreter' in data or 'interpreterArgsQuoted' in data:
            self.requires_version(8)

        argString = data.get('argString', None)
        if argString is not None:
            data['argString'] = dict2argstring(argString)

        return self._exec(POST, 'run/url', data=data, **kwargs)


    def _post_projects(self, project, **kwargs):
        """Wraps `Rundeck API POST /projects <http://rundeck.org/docs/api/index.html#project-creation>`_
        Requires API version >11

        :Parameters:
            project : str
                name of the project

        :Keywords:
            config : dict
                a dictionary of key/value pairs for the project config

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(11)

        config = kwargs.pop('config', None)

        prop_tmpl = '<property key="{0}" value="{1}" />'
        config_tmpl =  '  <config>\n' + \
                       '    {0}\n' + \
                       '  </config>\n'
        project_tmpl = '<project>\n' + \
                       '  <name>{0}</name>\n' + \
                       '{1}</project>'

        if config is not None:
            props_xml = '    \n'.join([prop_tmpl.format(k, v) for k, v in config.items()])
            config_xml = config_tmpl.format(props_xml)
        else:
            config_xml = ''

        xml = project_tmpl.format(project, config_xml)
        print(xml)

        headers = {'Content-Type': 'application/xml'}

        return self._exec(POST, 'projects', data=xml, headers=headers, **kwargs)


    def _get_projects(self, **kwargs):
        """Wraps `Rundeck API GET /projects <http://rundeck.org/docs/api/index.html#listing-projects>`_

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        return self._exec(GET, 'projects', **kwargs)


    def projects(self, method=GET, **kwargs):
        """An interface to the Rundeck `projects` API endpoint support

        :Parameters:
            method : str
                GET will retrieve a project, POST will create a project

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        if method == GET:
            return self._get_projects(**kwargs)
        elif method == POST:
            return self._post_projects(**kwargs)


    def project(self, project, **kwargs):
        """Wraps `Rundeck API /project/[NAME] <http://rundeck.org/docs/api/index.html#getting-project-info>`_

        :Parameters:
            project : str
                name of Project

        :Keywords:
            create : bool
                Create the project if it is not found (requires API version >11)
                [default: True for API version >11 else False]

        :return: A :class:`~.rundeck.connection.RundeckResponse``
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        # check if project creation is desired and apply defaults
        create = kwargs.pop('create', None)
        if create is None:
            if self.connection.api_version >= 11:
                create = True
            else:
                create = False
        elif create == True:
            self.requires_version(11)

        rd_url = 'project/{0}'.format(urlquote(project))

        # seed project var (seems cleaner than alternatives)
        project = None
        try:
            project = self._exec(GET, rd_url, **kwargs)
        except HTTPError as exc:
            if create:
                project = self._exec(POST, rd_url, **kwargs)
            else:
                raise

        return project


    def project_resources(self, project, **kwargs):
        """Wraps `Rundeck API GET /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project

        :Keywords:
            fmt : str
                the format of the response one of :class:`~rundeck.defaults.ExecutionOutputFormat`
                ``values`` (default: 'text')
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

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(2)

        params = cull_kwargs(('fmt', 'scriptInterpreter', 'interpreterArgsQuoted', 'hostname', \
            'tags', 'os-name', 'os-family', 'os-arch', 'os-version', 'name', 'exlude-hostname', \
            'exlude-tags', 'exlude-os-name', 'exlude-os-family', 'exlude-os-arch', \
            'exlude-os-version', 'exlude-name'), kwargs)

        if 'fmt' in params:
            params['format'] = params.pop('fmt')

        return self._exec(GET, 'project/{0}/resources'.format(urlquote(project)), params=params, **kwargs)


    def project_resources_update(self, project, nodes, **kwargs):
        """Wraps `Rundeck API POST /project/[NAME]/resources <http://rundeck.org/docs/api/index.html#updating-and-listing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project
            nodes : list(RundeckNode, ...)
                a list of RundeckNode objects

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        headers = {'Content-Type': 'text/xml'}

        data = '<nodes>{0}</nodes>'.format('\n'.join([node.xml for node in nodes]))

        return self._exec(POST, 'project/{0}/resources'.format(urlquote(project)), data=data, headers=headers, **kwargs)


    def project_resources_refresh(self, project, providerURL=None, **kwargs):
        """Wraps `Rundeck API POST /project/[NAME]/resources/refresh <http://rundeck.org/docs/api/index.html#refreshing-resources-for-a-project>`_

        :Parameters:
            project : str
                name of the project
            providerURL : str
                Specify the Resource Model Provider URL to refresh the resources from; otherwise
                the configured provider URL in the `project.properties` file will be used

        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(2)

        data = {}
        if providerURL is not None:
            data['providerURL'] = providerURL

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
                one of :class:`~rundeck.defaults.Status` ``values``
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


        :return: A :class:`~.rundeck.connection.RundeckResponse`
        :rtype: :class:`~.rundeck.connection.RundeckResponse`
        """
        self.requires_version(4)
        params = cull_kwargs(('jobIdFilter', 'reportIdFilter', 'userFilter', 'statFilter', \
            'jobListFilter', 'excludeJobListFilter', 'recentFilter', 'begin', 'end', 'max', \
            'offset'), kwargs)
        params['project'] = project
        return self._exec(GET, 'history', params=params, **kwargs)


class RundeckApi(RundeckApiTolerant):
    """ Same as RundeckApiTolerant and complains on every Rundeck Server error or 4xx/5xx HTTP
    status code.
    """
    def _exec(self, method, url, params=None, data=None, parse_response=True, **kwargs):
        quiet = kwargs.get('quiet', False)

        result = super(RundeckApi, self)._exec(
            method, url, params=params, data=data, parse_response=parse_response, **kwargs)

        if not quiet and parse_response:
            result.raise_for_error()

        return result
