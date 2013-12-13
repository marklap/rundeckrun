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

    from rundeck.client import Rundeck
    rd = Rundeck(api_token='SECRET_API_TOKEN')
    rd.list_projects()

The code above should result in a list of projects on the target Rundeck server such as this...

.. code-block:: python

    [{
        'description': None,
        'name': 'TestProject',
        'resources': {'providerURL': 'http://localhost:8000/resources.xml'},
    }]

From this point on in the documentation, assume the ``rd`` variable is an instance of the
:py:class:`Rundeck <rundeck.client.Rundeck>` class.

Interacting with Rundeck
------------------------

An instance of the :py:class:`Rundeck <rundeck.client.Rundeck>` class is where you'll spend most
with RundeckRun. If you want a more *raw* interface to the Rundeck API, check out the
:py:class:`RundeckApi <rundeck.api.RundeckApi>` class. In this case, you'll definitely want to
check out the `Rundeck API Reference`_.

.. _Rundeck API Reference: http://rundeck.org/docs/api/index.html

.. toctree::

    server

Projects
--------

.. toctree::

    projects

Jobs
----

.. toctree::

    jobs


Resources
---------

.. toctree::

    resources

Importing and Exporting
-----------------------

.. toctree::

    import_export

