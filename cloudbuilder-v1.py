#!/usr/bin/env python

"""Tool to track progress of a build in google cloud
does this build exist?
gcloud container builds list --filter "source.repo_source.repo_name=$REPO AND source_provenance.resolved_repo_source.commit_sha=$COMMIT_SHA"

if yes then assign build id to GCB_ID

using GCB_ID, print to stdout
- progress of build
GCB_ID=$(gcloud container builds list --filter "source.repo_source.repo_name="github-getsentry-brain" AND source_provenance.resolved_repo_source.commit_sha=$(git show-ref master --hash --heads) AND status=SUCCESS" --format="value(id)")
- status of build
gcloud container builds list --filter $GCB_ID --ongoing
gcloud container builds describe $GCB_ID --format="value(status)"
- last 10 lines of log
 gcloud container builds log $GCB_ID

Jira ticket: https://getsentry.atlassian.net/browse/OPS-111
"""


import shlex
import argparse
import json
import subprocess
import sys

REPO = "github-getsentry-brain"
# SHA = $(git show-ref master --hash --heads) this command assumes that it is being run from same filesystem
SHA = "82cce810fa298d99dabd176df9086a4ea043229d"  # only hardcoded now for testing purposes
SHA_NOT = "8888888888888888888888888" # fake SHA 

print("""
Does this build exist?
""")
COMMAND = """gcloud container builds list --filter 'source.repo_source.repo_name={} AND source_provenance.resolved_repo_source.commit_sha={}' --format='json' """.format(REPO, SHA)
print("""

{}

""".format(COMMAND))
BUILD_DATA = json.loads(subprocess.check_output(shlex.split(COMMAND)))[0]
print("""

{}

""".format(BUILD_DATA))
BUILD_ID = BUILD_DATA['id']
BUILD_STATUS = BUILD_DATA['status']
# note to self - top level status key returns overall status of build while steps[].status returns SUCCESS only once build is completed
BUILD_COMPLETE = BUILD_DATA['steps[].status']

print("""

build id is {}
build status is {}
build completion is {}

""".format(BUILD_ID, BUILD_STATUS, BUILD_COMPLETE))
# # Save unique gcloud build ID to use in future commands
# print("""
# Build ID is {}.
# See URL:
#     https://console.cloud.google.com/gcr/builds/{}""".format(GCB_ID.strip())
    
#     # Show currently progress of build
#     # GCB_ID = $(gcloud container builds list - -filter "source.repo_source.repo_name=" github - getsentry - brain " AND source_provenance.resolved_repo_source.commit_sha=$(git show-ref master --hash --heads) AND status=SUCCESS" - -format = "value(id)")
#     # gcloud container builds list --filter $GCB_ID --ongoing
#     STATUS = """gcloud container builds describe {} --format='value(status)'""".format(GCB_ID.strip())
#     subprocess.call(shlex.split(STATUS))
#     # print last 10 lines of log
#     LOG = "gcloud container builds log {}".format(GCB_ID.strip())
#     subprocess.call(shlex.split(LOG))
# try:

# except ValueError:
#     print('NO')
