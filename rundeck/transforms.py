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

import json
from datetime import datetime
from functools import wraps
import inspect

try:
    from cElementTree import ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

from util import child2dict, attr2dict, node2dict

_DATETIME_ISOFORMAT = '%Y-%m-%dT%H:%M:%SZ'


def is_transform(func):
    func.__is_transform__ = True
    return func


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
            data['job'] = node2dict(job_el)
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
def jobs(resp):
    base = resp.etree.find('jobs')
    job_count = int(base.attrib['count'])

    jobs = []
    if job_count > 0:
        for job_el in base.iterfind('job'):
            jobs.append(node2dict(job_el))

    return jobs


@is_transform
def project(resp):
    return projects(resp)[0]


@is_transform
def projects(resp):
    base = resp.etree.find('projects')
    project_count = int(base.attrib['count'])

    projects = []
    if project_count > 0:
        for project_el in base.iterfind('project'):
            project = {}

            # an attempt to accomodate the "additional items" specified in the API docs but don't
            #     seem to be included in the response
            #     https://github.com/dtolabs/rundeck/issues/586
            resources_el = project_el.find('resources')
            if resources_el:
                project['resources'] = child2dict(resources_el)
                project_el.remove(resources_el)

            project.update(child2dict(project_el))
            projects.append(project)

    return projects


@is_transform
def job_import_status(resp):
    results = {
        'succeeded': None,
        'failed': None,
        'skipped': None,
        }

    for status in results.keys():
        status_el = resp.etree.find(status)
        if status_el is not None:
            results[status] = [child2dict(job_el) for job_el in status_el.iterfind('job')] or None

    return results


@is_transform
def jobs_delete(resp):
    base = resp.etree.find('deleteJobs')

    results ={
        'succeeded': None,
        'failed': None,
    }

    for status in results.keys():
        status_el = base.find(status)
        if status_el is not None:
            results[status] = {
                'count': int(status_el.attrib.get('count'))
                }
            jobs = []
            for job_req_el in status_el.iterfind('deleteJobResult'):
                jobs.append(node2dict(job_req_el))
            results[status]['jobs'] = jobs

    results['requestCount'] = int(base.attrib.get('requestCount'))
    results['allsuccessful'] = bool(base.attrib.get('allsuccessful'))

    return results


@is_transform
def execution_output(resp):
    return json.loads(resp.text)


_execution_abort = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
    <success>
        <message>Execution status: previously succeeded</message>
    </success>
    <abort reason="Job is not running" status="failed">
        <execution id="295" status="succeeded"/>
    </abort>
</result>
"""

@is_transform
def execution_abort(resp):
    return node2dict(resp.etree.find('abort'))


@is_transform
def run_execution(resp):
    execution = resp.etree.find('execution')
    if execution is not None:
        return int(execution.attrib.get('id', None))
    else:
        return None


_project_resources = """\
<?xml version="1.0" encoding="UTF-8"?>

<project>
  <node name="host1" description="I &lt;3 XML" tags="hot" hostname="hostname1" osArch="" osFamily="" osName="" osVersion="" username="user1" foo="bar"/>
  <node name="host2" description="" tags="cold" hostname="hostname2" osArch="" osFamily="" osName="" osVersion="" username="user2" foz="baz"/>
  <node name="host3" description="" tags="" hostname="hostname3" osArch="" osFamily="" osName="" osVersion="" username="user3"/>
  <node name="optimus-prime" description="Rundeck server node" tags="" hostname="optimus-prime" osArch="amd64" osFamily="unix" osName="Linux" osVersion="3.8.0-19-generic" username="root"/>
</project>
"""

@is_transform
def project_resources(resp):
    nodes = {}
    for node in list(resp.etree):
        node_attr = attr2dict(node)
        nodes[node_attr['name']] = node_attr
    return nodes


@is_transform
def success_message(resp):
    return {'success': resp.success, 'message': resp.message}


_history = """\
<?xml version="1.0" ?>
<result apiversion="9" success="true">
    <events count="20" max="20" offset="0" total="280">
        <event endtime="1385586242542" starttime="1385586242236">
            <title>adhoc</title>
            <status>succeeded</status>
            <summary>http://localhost:8000/hello_world.sh</summary>
            <node-summary failed="0" succeeded="1" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:04:02Z</date-started>
            <date-ended>2013-11-27T21:04:02Z</date-ended>
            <execution id="319"/>
        </event>
        <event endtime="1385586223580" starttime="1385586223263">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://localhost:8000/hello_world.sh</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:03:43Z</date-started>
            <date-ended>2013-11-27T21:03:43Z</date-ended>
            <execution id="318"/>
        </event>
        <event endtime="1385586167788" starttime="1385586167236">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:02:47Z</date-started>
            <date-ended>2013-11-27T21:02:47Z</date-ended>
            <execution id="317"/>
        </event>
        <event endtime="1385586158719" starttime="1385586158128">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:02:38Z</date-started>
            <date-ended>2013-11-27T21:02:38Z</date-ended>
            <execution id="316"/>
        </event>
        <event endtime="1385586106495" starttime="1385586106011">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:01:46Z</date-started>
            <date-ended>2013-11-27T21:01:46Z</date-ended>
            <execution id="315"/>
        </event>
        <event endtime="1385586083766" starttime="1385586082684">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:01:22Z</date-started>
            <date-ended>2013-11-27T21:01:23Z</date-ended>
            <execution id="314"/>
        </event>
        <event endtime="1385586001103" starttime="1385586000796">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T21:00:00Z</date-started>
            <date-ended>2013-11-27T21:00:01Z</date-ended>
            <execution id="313"/>
        </event>
        <event endtime="1385585991019" starttime="1385585990692">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T20:59:50Z</date-started>
            <date-ended>2013-11-27T20:59:51Z</date-ended>
            <execution id="312"/>
        </event>
        <event endtime="1385585842511" starttime="1385585842180">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T20:57:22Z</date-started>
            <date-ended>2013-11-27T20:57:22Z</date-ended>
            <execution id="311"/>
        </event>
        <event endtime="1385585823438" starttime="1385585823078">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T20:57:03Z</date-started>
            <date-ended>2013-11-27T20:57:03Z</date-ended>
            <execution id="310"/>
        </event>
        <event endtime="1385585685919" starttime="1385585685471">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T20:54:45Z</date-started>
            <date-ended>2013-11-27T20:54:45Z</date-ended>
            <execution id="309"/>
        </event>
        <event endtime="1385567180973" starttime="1385567180644">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T15:46:20Z</date-started>
            <date-ended>2013-11-27T15:46:20Z</date-ended>
            <execution id="308"/>
        </event>
        <event endtime="1385567131567" starttime="1385567131241">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T15:45:31Z</date-started>
            <date-ended>2013-11-27T15:45:31Z</date-ended>
            <execution id="307"/>
        </event>
        <event endtime="1385567062006" starttime="1385567061686">
            <title>adhoc</title>
            <status>failed</status>
            <summary>https://httpbin.org/html</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T15:44:21Z</date-started>
            <date-ended>2013-11-27T15:44:22Z</date-ended>
            <execution id="306"/>
        </event>
        <event endtime="1385566849484" starttime="1385566849142">
            <title>adhoc</title>
            <status>failed</status>
            <summary>http://localhost:8000/hello_world.sh</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T15:40:49Z</date-started>
            <date-ended>2013-11-27T15:40:49Z</date-ended>
            <execution id="305"/>
        </event>
        <event endtime="1385566717147" starttime="1385566716795">
            <title>adhoc</title>
            <status>failed</status>
            <summary>http://localhost:8000/hello_world.sh</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T15:38:36Z</date-started>
            <date-ended>2013-11-27T15:38:37Z</date-ended>
            <execution id="304"/>
        </event>
        <event endtime="1385562632886" starttime="1385562632535">
            <title>adhoc</title>
            <status>succeeded</status>
            <summary>echo &quot;Hello World!&quot;
</summary>
            <node-summary failed="0" succeeded="1" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T14:30:32Z</date-started>
            <date-ended>2013-11-27T14:30:32Z</date-ended>
            <execution id="303"/>
        </event>
        <event endtime="1385562592222" starttime="1385562591898">
            <title>adhoc</title>
            <status>succeeded</status>
            <summary>echo &quot;Hello World!&quot;
</summary>
            <node-summary failed="0" succeeded="1" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T14:29:51Z</date-started>
            <date-ended>2013-11-27T14:29:52Z</date-ended>
            <execution id="302"/>
        </event>
        <event endtime="1385562580027" starttime="1385562579687">
            <title>adhoc</title>
            <status>succeeded</status>
            <summary>echo &quot;monkey&quot;
</summary>
            <node-summary failed="0" succeeded="1" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T14:29:39Z</date-started>
            <date-ended>2013-11-27T14:29:40Z</date-ended>
            <execution id="301"/>
        </event>
        <event endtime="1385562485666" starttime="1385562485226">
            <title>adhoc</title>
            <status>failed</status>
            <summary>&quot;echo &quot;monkey&quot;&quot;
</summary>
            <node-summary failed="1" succeeded="0" total="1"/>
            <user>admin</user>
            <project>TestProject</project>
            <date-started>2013-11-27T14:28:05Z</date-started>
            <date-ended>2013-11-27T14:28:05Z</date-ended>
            <execution id="300"/>
        </event>
    </events>
</result>"""

@is_transform
def events(resp):
    base = resp.etree.find('events')

    from pprint import pprint

    events = []
    for event_el in base.iterfind('event'):
        pprint(event_el)

        event = {}
        job_el = event_el.find('job')
        if job_el is not None:
            event['job'] = attr2dict(job_el)
            event_el.remove(job_el)

        execution_el = event_el.find('execution')
        if execution_el is not None:
            event['execution'] = attr2dict(execution_el)
            event_el.remove(execution_el)

        node_summary_el = event_el.find('node-summary')
        if node_summary_el is not None:
            event['node-summary'] = attr2dict(node_summary_el)
            event_el.remove(node_summary_el)

        event.update(node2dict(event_el))

        event['date-started'] = datetime.strptime(event['date-started'], _DATETIME_ISOFORMAT)
        event['date-ended'] = datetime.strptime(event['date-ended'], _DATETIME_ISOFORMAT)

        events.append(event)

    return events


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

