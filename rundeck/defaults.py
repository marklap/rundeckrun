"""
:summary: Default values

:license: Apache License, Version 2.0
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2015
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
    ABORTED='aborted',
    SKIPPED='skipped',
    PENDING='pending'
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

ExecutionOutputFormat = enum(
    'ExecutionOutputFormat',
    TEXT='text',
    **dict(zip(JobDefFormat.keys, JobDefFormat.values))
    )

RUNDECK_API_VERSION = 11
GET = 'get'
POST = 'post'
DELETE = 'delete'
JOB_RUN_TIMEOUT = 60
JOB_RUN_INTERVAL = 3
