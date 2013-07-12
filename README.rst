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
    >>> pprint(rd.list_projects())
    [{'description': 'Test Project', 'name': 'TestProject'}]
    >>> pprint(rd.list_jobs('TestProject'))
    [{'description': 'Hello World!',
      'group': None,
      'id': 'a6e1e0f7-ad32-4b93-ba2c-9387be06a146',
      'name': 'HelloWorld',
      'project': 'ALFPoC'}]
    >>> pprint(rd.run_job_name('TestProject', 'HelloWorld', argString={'from':'rundeckrun'}))
    {'argstring': '-from rundeckrun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'rundeckrun'}


Documentation
-------------

Coming soon...