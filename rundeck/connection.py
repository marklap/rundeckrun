__docformat__ = "restructuredtext en"
"""
:summary: Connection object for Rundeck client

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013

:requires: requests
"""
import requests

# see if we can speed things up a bit with cElementTree (not required)
try:
    import cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

from defaults import RUNDECK_API_VERSION

class RundeckResponse(object):
    """ Base class for Rundeck responses """
    pass


class RundeckXmlResponse(RundeckResponse):

    def __init__(self, xml):
        """ Parses an XML string into a convenient Python object

        :Parameters:
            xml : str
                an XML string returned by the Rundeck server
        """
        self.xml = xml
        self.etree = ElementTree.fromstring(xml)
        self.api_version = self.etree.attrib.get('apiversion', None)
        self.message = None

        if 'success' in self.etree.attrib:
            self.success = True
            message_el = self.etree.find('success')
        else:
            self.success = False
            message_el = self.etree.find('error')

        if message_el is not None:
            self.message = message_el.find('message').text
            self.etree.remove(message_el)

    @property
    def body(self):
        """ Returns the most appropriate portion of the parsed XML response
        """
        if hasattr(self, '_body'):
            return self._body

        body_els = list(self.etree)
        body_el_count = len(body_els)
        if body_el_count == 0:
            self._body = None
        elif body_el_count == 1:
            self._body = body_els[0]
        else:
            self._body = body_els

        return self._body


class RundeckYamlResponse(RundeckResponse):

    def __init__(self, xml):
        raise NotImplementedError('YAML support not complete')

    @property
    def body(self):
        raise NotImplementedError('YAML support not complete')


class RundeckJsonResponse(RundeckResponse):

    def __init__(self, xml):
        raise NotImplementedError('JSON support not complete')

    @property
    def body(self):
        raise NotImplementedError('JSON support not complete')


class RundeckConnection(object):

    def __init__(self, server='localhost', protocol='http', port=4440, api_token=None, **kwargs):
        """ Initialize a Rundeck API client connection

        :Parameters:
            server : str
                hostname of the Rundeck server (default: localhost)
            protocol : str
                either http or https (default: 'http')
            port : int
                Rundeck server port (default: 4440)
            api_token : str
                *\*\*Preferred method of authentication* - valid Rundeck user API token
                (default: None)

        :Keywords:
            usr : str
                Rundeck user name (used in place of api_token)
            pwd : str
                Rundeck user password (used in combo with usr)
            api_version : int
                Rundeck API version
        """
        self.protocol = protocol
        self.usr = usr = kwargs.get('usr', None)
        self.pwd = pwd = kwargs.get('pwd', None)
        self.server = server
        self.api_token = api_token
        self.api_version = kwargs.get('api_version', RUNDECK_API_VERSION)

        if (protocol == 'http' and port != 80) or (protocol == 'https' and port != 443):
            self.server = '{0}:{1}'.format(server, port)

        if api_token is None and usr is None and pwd is None:
            raise InvalidAuthentication('Must supply either api_token or usr and pwd')

        self.http = requests.Session()
        if api_token is not None:
            self.http.headers['X-Rundeck-Auth-Token'] = api_token
        elif usr is not None and pwd is not None:
            # TODO: support username/password authentication
            raise NotImplementedError('Username/password authentication is not yet supported')

        self.base_url = '{0}://{1}/api/{2}/'.format(
            self.protocol, self.server, self.api_version)

    def make_url(self, api_url):
        """ Creates a valid Rundeck URL based on the API and the base url of
        the RundeckConnection

        :Parameters:
            api_url : str
                the Rundeck API URL

        :rtype: str
        :return: full Rundeck API URL
        """
        return self.base_url + api_url.lstrip('/')

    def execute_cmd(self, method, url, params=None, data=None):
        """ Sends the HTTP request to Rundeck

        :Parameters:
            method : str
                the HTTP request method
            url : str
                API URL
            params : dict({str: str, ...})
                a dict of query string params (default: None)
            data : str
                the XML or YAML payload necessary for some commands
                (default: None)

        :rtype: RundeckXmlResponse | RundeckYamlResponse
        """
        url = self.make_url(url)

        response = self.http.request(method, url, params=params, data=data)
        if response.status_code == requests.codes.ok:
            return RundeckXmlResponse(response.text)
        else:
            return response
