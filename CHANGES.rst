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
