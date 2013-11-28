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

