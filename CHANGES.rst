0.1.13
------
- In response to `Issue #23 <https://github.com/marklap/rundeckrun/issues/23>`_, change license to
  to Apache 2.0. Versions 0.1.12 will maintain the CC license (added a cc-by-sa tag to repo to
  make it easy to find).

0.1.12
------
- In response to `Issue #18 <https://github.com/marklap/rundeckrun/issues/18>`_
  (many thanks @bobnelson0), update docs to provide information about
  `Multi-valued <http://rundeck.org/docs/manual/jobs.html#defining-an-option>`_ job options.

0.1.11
------
- Merged `Issue #16 <https://github.com/marklap/rundeckrun/issues/16>`_: Fix typo in isinstance
  call (many thanks @boosh)
- Fixed broken test init validation

0.1.10
------
- Fixed `Issue #15 <https://github.com/marklap/rundeckrun/issues/15>`_: job_executions() in api.py
  should use GET not POST

0.1.9
-----
- Add username/password authentication support (thanks to brendan-sterne)
- Fix project API call - was using POST, should be GET (thanks to shawnchasse)
- Various fixes to get tests to pass with a Rundeck 2.x version server
- Last release before version 1

0.1.8
-----
- Minor documentation changes: autodoc for all interesting modules and other misc changes
- Fix api.jobs_export to actually call the Rundeck /jobs/export endpoint with proper params

0.1.7
-----
- Add switch for Rundeck server SSL certificate validation (thank you @shlomosh)
- Fix silly typo exceptions.RundeckServerError

0.1.6
-----
- Put some decent effort into documentation

0.1.0
-----
- Create an API class that attempts to mirror the Rundeck API as closely as possible
- Refactor the Client class to provide conveniences for the user
- Wrap Client class methods in "transforms" - really just changes the XML from Rundeck into
  friendly Python dicts
- Increase test coverage of the API class significantlyu

0.0.2
-----
- Add support to block and wait for a completed status from ``run_job`` invoke
