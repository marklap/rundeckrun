"""
:summary: Default values

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
__docformat__ = "restructuredtext en"


def enum(name, *sequential, **named):
    values = dict(zip(sequential, range(len(sequential))), **named)
    values['values'] = list(values.values())
    values['keys'] = list(values.keys())
    return type(name, (), values)

Status = enum(
    'Status',
    RUNNING='running',
    SUCCEEDED='succeeded',
    FAILED='failed',
    ABORTED='aborted'
    )

DupeOption = enum(
    'DupeOption',
    SKIP='skip',
    CREATE='create',
    UPDATE='update'
    )

UuidOption = enum(
    'UuidOption',
    PRESERVE='preserve',
    REMOVE='remove'
    )

JobDefFormat = enum(
    'JobDefFormat',
    XML='xml',
    YAML='yaml'
    )

RUNDECK_API_VERSION = 9
GET = 'get'
POST = 'post'
DELETE = 'delete'
