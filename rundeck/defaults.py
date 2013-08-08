__docformat__ = "restructuredtext en"
"""
:summary: Default values

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""
def enum(name, *sequential, **named):
    values = dict(zip(sequential, range(len(sequential))), **named)
    return type(name, (), values)

Status = enum(
    'Status',
    RUNNING='running',
    SUCCEEDED='succeeded',
    FAILED='failed',
    ABORTED='aborted'
    )

RUNDECK_API_VERSION = 7
GET = 'get'
POST = 'post'
