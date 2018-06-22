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
SHA = "61ca573635fc6c7265baea7cba189a1a153ee955"  # only hardcoded now for testing purposes
SHA_NOT = "8888888888888888888888888" # fake SHA 

gcloud container builds list --filter "source.repo_source.repo_name=$REPO AND source_provenance.resolved_repo_source.commit_sha=$COMMIT_SHA"

COMMAND = "gcloud container builds list --filter 'source.repo_source.repo_name=" + REPO + " AND source_provenance.resolved_repo_source.commit_sha=" + SHA + " AND status=SUCCESS' --format=value(id)"
# command = 'gcloud container builds list --filter "source.repo_source.repo_name=github-getsentry-brain AND source_provenance.resolved_repo_source.commit_sha=61ca573635fc6c7265baea7cba189a1a153ee955 AND status=SUCCESS" --format="value(id)"'
GCP_PROJECT = "internal-sentry"
GCP_ID = 225313812765
DATA = subprocess.check_output(shlex.split(COMMAND))
print("""
ID created.
See URL:
https://console.cloud.google.com/gcr/builds/{}?project={}&organizationId={}""".format(DATA.strip(), GCP_PROJECT, GCP_ID))

# def track_cloud_builder():
#     pass
