RundeckRun
==========

A client library written in Python to interact with the Rundeck
API. It uses the awesome `requests`_
library.

Documentation is hosted on `Read the Docs`_

*DISCLAIMER:* Test suite is not comprehensive, but most features have been tested and should work.
Should work on at least Python 2.7 and Python 3.3.

Installation
------------

Requires
~~~~~~~~
* `requests`_

.. code-block:: bash

    $ pip install rundeckrun


Use
---

.. code-block:: pycon

    >>> from rundeck.client import Rundeck
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
    >>> rd.run_job('a6e1e0f7-ad32-4b93-ba2c-9387be06a146', argString={'from':'RundeckRun'})
    {'argstring': '-from RundeckRun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'rundeckrun'}


Running Tests
-------------

.. note:: You'll probably want to create a `virtualenv <http://www.virtualenv.org/en/latest/>`_
    for this.

Running the tests requires a running Rundeck server (the Rundeck standalone jar works well) and an
API token for said Rundeck server.

You'll have to at least set the API token environment variable of ``RUNDECK_API_TOKEN`` but there
are other environment variables to be aware of. The list is below and can be found at the head of
the tests/\_\_init\_\_.py file. They should be fairly self-explanatory (OK, RUNDECK_PROTOCOL might
not be self-explanatory... use either 'http' or 'https' there).

.. code-block:: bash

    RUNDECK_API_TOKEN
    RUNDECK_SERVER
    RUNDECK_PORT
    RUNDECK_PROTOCOL

Next clone the repo.

.. code-block:: bash

    git clone https://github.com/marklap/rundeckrun

.. note:: activate your `virtualenv <http://www.virtualenv.org/en/latest/>`_

Then install the requirements and dev requirements.

.. code-block:: bash

    pip install -r requirements.txt
    pip install -r requirements_dev.txt

Lastly, execute nose tests.

.. code-block:: bash

    nosetests

.. _requests: http://docs.python-requests.org/
.. _Read the Docs:  http://rundeckrun.readthedocs.org/
