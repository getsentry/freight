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
SHA_FAIL = "8474ed8fe807d4ec594606eeac8c551f24483f52" # SHA of build already failed
COMMAND = """gcloud container builds list --filter 'source.repo_source.repo_name={} AND source_provenance.resolved_repo_source.commit_sha={}' --format='json' """.format(REPO, SHA)
BUILD_DATA = json.loads(subprocess.check_output(shlex.split(COMMAND)))[0]
BUILD_ID = BUILD_DATA['id']
BUILD_STATUS = BUILD_DATA['status']

# if build status is successful, do nothing; if not successful, print log.
def check_build():
    if BUILD_STATUS is not 'FAILURE':
        print("""
Build status is {} and ID is {}.
See more details here:
    https://console.cloud.google.com/gcr/builds/{}
        """.format(BUILD_STATUS, BUILD_ID, BUILD_ID))
    else:
        print("""
    Build failed. Printing log...""")
        subprocess.check_output(shlex.split("gcloud container builds log {}".format(BUILD_ID)))

check_build()