"""
:summary: Transformations for RundeckResponses to simple dicts for consumption

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013

:requires: requests
"""
__docformat__ = "restructuredtext en"

from functools import wraps
import inspect

try:
    from cElementTree import ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class RundeckResponse(object):

    def __init__(self, response, as_dict_method=None):
        """ Parses an XML string into a convenient Python object

        :Parameters:
            response : str
                a response from the Rundeck server
        """
        self._response = response
        self._dict = None
        self._success = None
        self._message = None

    def _get_dict(self):
        if self._dict is None:
            pass  # self._dict = xmltodict.parse(self._response)
        return self._dict

    @property
    def response(self):
        return self._response

    @property
    def as_dict(self):
        if self._as_dict_method is None:
            return self._dict
        else:
            return self._as_dict_method(self)

    @property
    def api_version(self):
        return self.as_dict['result']['@apiversion']

    @property
    def success(self):
        if self._success is not None:
            return self._success

        self._success = '@success' in self.as_dict['result']
        return self._success

    @property
    def message(self):
        if self._message is not None:
            return self._message

        if self.success:
            self._message = self.as_dict['result']['success']['message']
        else:
            self._message = self.as_dict['result']['error']['message']

        return self._message


class RundeckResponseError(RundeckResponse):
    pass




def is_transform(func):
    func.__is_transform__ = True
    return func

def _result(resp):
    """Pulls the result information out - useful for just about all responses
    """


system_info = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
        <success>
                <message>System Stats for RunDeck 1.6.1 on node 0136M956912L</message>
        </success>
        <system>
                <timestamp epoch="1382731189837" unit="ms">
                        <datetime>2013-10-25T19:59:49Z</datetime>
                </timestamp>
                <rundeck>
                        <version>1.6.1</version>
                        <build>1.6.1-1</build>
                        <node>0136M956912L</node>
                        <base>C:/workspace/servers/rundeck-1.6.1</base>
                        <apiversion>9</apiversion>
                </rundeck>
                <os>
                        <arch>amd64</arch>
                        <name>Windows 7</name>
                        <version>6.1</version>
                </os>
                <jvm>
                        <name>Java HotSpot(TM) 64-Bit Server VM</name>
                        <vendor>Oracle Corporation</vendor>
                        <version>23.25-b01</version>
                </jvm>
                <stats>
                        <uptime duration="283596" unit="ms">
                                <since epoch="1382730906241" unit="ms">
                                        <datetime>2013-10-25T19:55:06Z</datetime>
                                </since>
                        </uptime>
                        <cpu>
                                <loadAverage unit="percent">-1.0</loadAverage>
                                <processors>4</processors>
                        </cpu>
                        <memory unit="byte">
                                <max>1877213184</max>
                                <free>366096184</free>
                                <total>651886592</total>
                        </memory>
                        <scheduler>
                                <running>0</running>
                        </scheduler>
                        <threads>
                                <active>27</active>
                        </threads>
                </stats>
        </system>
</result>"""

projects = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
        <projects count="1">
                <project>
                        <name>TestProject</name>
                        <description/>
                </project>
        </projects>
</result>"""

project = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
        <projects count="1">
                <project>
                        <name>TestProject</name>
                        <description/>
                </project>
        </projects>
</result>"""

@is_transform
def system_info(resp):
    return {'resp': resp}


@is_transform
def execution(resp):
    """Transforms an Execution's RundeckResponse object into a dict

    :Parameters:
        resp : RundeckResponse
            a RundeckResponse representing a Rundeck Execution

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



_transforms = {obj_key: obj_val for obj_key, obj_val in locals().items() if hasattr(obj_val, '__is_transform__')}

def transform(resp_type):

    def inner(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                xform = _transforms[resp_type]
            except KeyError:
                raise Exception('Transform does not exist for type: {0}'.format(resp_type))
            else:
                return xform(func(*args, **kwargs))

        return wrapper

    return inner

