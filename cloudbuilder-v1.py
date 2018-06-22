#!/usr/bin/env python

"""Tool to track progress of a build in google cloud
does this build exist?
if yes then assign build id to GCB_ID

using GCB_ID, print to stdout
- progress of build
- status of build
- last 10 lines of log

Jira ticket: https://getsentry.atlassian.net/browse/OPS-111
"""


import shlex
import argparse
import json
import subprocess
import sys

REPO = "github-getsentry-brain"
# SHA = $(git show-ref master --hash --heads) this command assumes that it is being run from repo
SHA = "61ca573635fc6c7265baea7cba189a1a153ee955" # only hardcoded now for testing purposes
command = "gcloud container builds list --filter 'source.repo_source.repo_name=" + REPO + " AND source_provenance.resolved_repo_source.commit_sha=" + SHA + " AND status=SUCCESS' --format=value(id)"
# command = 'gcloud container builds list --filter "source.repo_source.repo_name=github-getsentry-brain AND source_provenance.resolved_repo_source.commit_sha=61ca573635fc6c7265baea7cba189a1a153ee955 AND status=SUCCESS" --format="value(id)"'
data = subprocess.check_output(shlex.split(command))
print data
# def track_cloud_builder():
#     pass
