"""
:summary: Transformations for RundeckResponses to simple dicts for consumption

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013

:requires: requests
"""
__docformat__ = "restructuredtext en"

from pprint import pprint

from datetime import datetime
from functools import wraps
import inspect

try:
    from cElementTree import ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

from util import child2dict, attr2dict

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'


def is_transform(func):
    func.__is_transform__ = True
    return func


_system_info = """\
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

_projects = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
        <projects count="1">
                <project>
                        <name>TestProject</name>
                        <description/>
                </project>
        </projects>
</result>"""

_project = """\
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
    base = resp.etree.find('system')
    rundeck = base.find('rundeck')
    os = base.find('os')
    jvm = base.find('jvm')
    stats = base.find('stats')

    ts = base.find('timestamp').find('datetime').text
    ts_date = datetime.strptime(ts, _DATETIME_ISOFORMAT)

    data = {
        'timestamp': {'datetime': ts_date},
        'rundeck': child2dict(rundeck),
        'os': child2dict(os),
        'jvm': child2dict(jvm),
        'stats': {
            'uptime': attr2dict(stats.find('uptime')),
            'cpu': child2dict(stats.find('cpu')),
            'memory': child2dict(stats.find('memory')),
            'scheduler': child2dict(stats.find('scheduler')),
            'threads': child2dict(stats.find('threads')),
            }
        }

    return data


_execution = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
    <executions count="1">
        <execution href="http://optimus-prime:4440/execution/follow/282" id="282" project="TestProject" status="succeeded">
            <user>admin</user>
            <date-started unixtime="1383364692131">2013-11-02T03:58:12Z</date-started>
            <date-ended unixtime="1383364693001">2013-11-02T03:58:13Z</date-ended>
            <job averageDuration="870" id="f114ab12-9590-41e9-934a-78cdfaaaba77">
                <name>Huh</name>
                <group>prod</group>
                <project>TestProject</project>
                <description/>
            </job>
            <description>Plugin[localexec, nodeStep: true] [... 2 steps]</description>
            <argstring/>
        </execution>
    </executions>
</result>"""

@is_transform
def execution(resp):
    return executions(resp)[0]

@is_transform
def executions(resp):
    base = resp.etree.find('executions')
    exec_count = int(base.attrib['count'])

    def xform(el):

        data = child2dict(el)
        data.update(attr2dict(el))

        job_el = el.find('job')
        if job_el is not None:
            data['job'] = attr2dict(job_el)
            data['job'].update(child2dict(job_el))
            el.remove(job_el)

        if 'date-started' in data:
            data['date-started'] = datetime.strptime(data['date-started'], _DATETIME_ISOFORMAT)
        if 'date-ended' in data:
            data['date-ended'] = datetime.strptime(data['date-ended'], _DATETIME_ISOFORMAT)
        return data

    if exec_count > 0:
        return [xform(el) for el in base.iterfind('execution')]
    else:
        return []


@is_transform
def execution_old(resp):
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


_job = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
    <jobs count="3">
        <job id="8436f27f-7d16-48a1-9d4d-0a89145d1121">
            <name>HelloWorld</name>
            <group/>
            <project>TestProject</project>
            <description/>
        </job>
        <job id="16f4f377-0b3f-4eed-97e7-7946112e8dcc">
            <name>Huh</name>
            <group>test</group>
            <project>TestProject</project>
            <description/>
        </job>
        <job id="f114ab12-9590-41e9-934a-78cdfaaaba77">
            <name>Huh</name>
            <group>prod</group>
            <project>TestProject</project>
            <description/>
        </job>
    </jobs>
</result>"""

@is_transform
def jobs(resp):
    base = resp.etree.find('jobs')
    job_count = int(base.attrib['count'])

    jobs = []
    if job_count > 0:
        for job_el in base.iterfind('job'):
            job = attr2dict(job_el)
            job.update(child2dict(job_el))
            jobs.append(job)

    return jobs




_projects = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
    <projects count="2">
        <project>
            <name>JustAnotherProject</name>
            <description/>
        </project>
        <project>
            <name>TestProject</name>
            <description/>
        </project>
    </projects>
</result>"""

@is_transform
def projects(resp):
    base = resp.etree.find('projects')
    project_count = int(base.attrib['count'])

    projects = []
    if project_count > 0:
        for project_el in base.iterfind('project'):
            projects.append(child2dict(project_el))

    return projects


_transforms = {obj_key: obj_val for obj_key, obj_val in locals().items() if hasattr(obj_val, '__is_transform__')}

def transform(resp_type):

    def inner(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                xform = _transforms[resp_type]
            except KeyError:
                raise Exception('Transform does not exist for type: {0}'.format(resp_type))

            results = func(self, *args, **kwargs)
            results._as_dict_method = xform
            return results

        return wrapper

    return inner

