Jobs
====

A guide to working with Rundeck Jobs.


Listing
-------

.. code-block:: pycon

    >>> rd.list_jobs('TestProject')
    [{'description': 'Hello World!',
      'group': None,
      'id': 'a6e1e0f7-ad32-4b93-ba2c-9387be06a146',
      'name': 'HelloWorld',
      'project': 'TestProject'}]


Run a Job
---------

.. code-block:: pycon

    >>> rd.run_job('a6e1e0f7-ad32-4b93-ba2c-9387be06a146', argString={'from': 'RundeckRun'})
    {'argstring': '-from RundeckRun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'rundeckrun'}
