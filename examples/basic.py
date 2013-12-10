import os
import sys
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rundeck.client import Rundeck

_RUNDECK_API_TOKEN_VAR = 'RUNDECK_API_TOKEN'

api_token = os.environ.get(_RUNDECK_API_TOKEN_VAR, None)

if api_token is None:
    raise ValueError('{0} environment variable is not set; must provide a valid Rundeck API token')

rd = Rundeck(api_token=api_token)

# list projects
projects = rd.list_projects()
pprint(projects)
example_project = projects[0]['name']

# list jobs
jobs = rd.list_jobs(example_project)
pprint(jobs)
example_job_id = jobs[0]['id']

# run job
execution = rd.run_job(example_job_id)
pprint(execution)
