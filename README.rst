RundeckRun
==========

This is a lightweight wrapper written in Python to interact with the Rundeck
API. It uses the awesome `requests <http://docs.python-requests.org/>`_
library.

*DISCLAIMER:* Still in early stages of development

Installation
------------

Requires
~~~~~~~~
* `requests <http://docs.python-requests.org/>`_

.. code-block:: bash

    $ pip install rundeckrun


Use
---

.. code-block:: pycon

    >>> from rundeckrun.client import Rundeck
    >>> rd = Rundeck('rundeck.server.com', api_token='SECRET_API_TOKEN')
    >>> rd.list_projects()
    [{'description': 'Test Project', 'name': 'TestProject'}]
    >>> rd.list_jobs('TestProject')
    [{'description': 'Hello World!',
      'group': None,
      'id': 'a6e1e0f7-ad32-4b93-ba2c-9387be06a146',
      'name': 'HelloWorld',
      'project': 'TestProject'}]
    >>> rd.run_job('HelloWorld', 'TestProject', argString={'from':'rundeckrun'})
    {'argstring': '-from rundeckrun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'rundeckrun'}
    >>> # Use the block arg to wait for the job to complete
    >>> rd.run_job('HelloWorld', 'TestProject', argString={'from':'rundeck'}, block=True)
    {'argstring': '-from rundeckrun',
     'date-ended': datetime.datetime(2013, 8, 8, 6, 21, 51),
     'date-started': datetime.datetime(2013, 8, 8, 6, 21, 51),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/16',
     'id': '16',
     'job': {'averageDuration': '291',
             'description': None,
             'group': 'RundeckRun/Tests',
             'id': 'cb973e3a-e682-4b45-9dbe-9e5301a4361e',
             'name': 'HelloWorld',
             'project': 'TestProject'},
     'status': 'succeeded',
     'user': 'rundeckrun'}




Documentation
-------------

Coming soon...
