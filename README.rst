RundeckRun
==========

A client library written in Python to interact with the Rundeck
API. It uses the awesome `requests <http://docs.python-requests.org/>`_
library.

Documentation is hosted on `Read the Docs <http://rundeckrun.readthedocs.org/>`_

*DISCLAIMER:* Still in active development, but most features have been tested and should work. Only
tested on Python 2.7 but *should* work on Python 3.x as well.


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
    [{
        'description': None,
        'name': 'TestProject',
        'resources': {'providerURL': 'http://localhost:8000/resources.xml'},
    }]
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
