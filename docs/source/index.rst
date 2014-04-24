.. RundeckRun documentation master file, created by
   sphinx-quickstart on Wed Dec  4 10:45:34 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RundeckRun
==========

[Version |version|]

This is a lightweight wrapper written in Python to interact with the Rundeck
API. It uses the awesome `requests <http://docs.python-requests.org/>`_
library.


Installation
------------
.. note:: Requires `requests <http://docs.python-requests.org/>`_

.. code-block:: bash

    $ pip install rundeckrun


Basic Example
-------------

Initialize
~~~~~~~~~~

.. code-block:: pycon

    >>> from rundeck.client import Rundeck
    >>> rd = Rundeck('rundeck.server.com', api_token='SECRET_API_TOKEN')

List Projects
~~~~~~~~~~~~~

.. code-block:: pycon

    >>> rd.projects()
    [{
        'description': None,
        'name': 'TestProject',
        'resources': {'providerURL': 'http://localhost:8000/resources.xml'},
    }]


List Jobs for a Project
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: pycon

    >>> rd.jobs('TestProject')
    [{'description': 'Hello World!',
      'group': None,
      'id': 'a6e1e0f7-ad32-4b93-ba2c-9387be06a146',
      'name': 'HelloWorld',
      'project': 'TestProject'}]


Execute a Job
~~~~~~~~~~~~~

.. code-block:: pycon

    >>> rd.job_run('HelloWorld', 'TestProject', argString={'from':'rundeckrun'})
    {'argstring': '-from rundeckrun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'rundeckrun'}


User Guide
----------

.. toctree::
  :maxdepth: 2

  user_guide/index

API
---

.. toctree::
  :maxdepth: 2

  api

