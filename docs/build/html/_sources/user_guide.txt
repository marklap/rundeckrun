.. _user_guide:

User Guide
==========

Getting Started
---------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install rundeckrun


"Hello World!"
~~~~~~~~~~~~~~

.. code-block:: python

    from rundeckrun.client import Rundeck
    rd = Rundeck(api_token='SECRET_API_TOKEN')
    rd.list_projects()

The code above should result in a list of projects on the target Rundeck server such as this...

.. code-block:: python

    [{
        'description': None,
        'name': 'TestProject',
        'resources': {'providerURL': 'http://localhost:8000/resources.xml'},
    }]
