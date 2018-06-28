"""Tool to track progress of builds created
by Google Cloud Platform Container Builder
Jira ticket: https://getsentry.atlassian.net/browse/OPS-111
"""
from __future__ import absolute_import

import argparse
import json
import shlex
import subprocess
import sys

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

__all__ = ['GCPContainerBuilderCheck']




ERR_CHECK = '[{state}] {context}: {description} ({target_url})'
ERR_MISSING_CONTEXT = '{} context was not found'


class GCPContainerBuilderCheck(Check):
    def check(self, app, sha, config):
        COMMAND = """gcloud container builds list --filter 'source.repo_source.repo_name={} AND source_provenance.resolved_repo_source.commit_sha={}' --format='json' """.format(REPO, SHA)
        BUILD_DATA = json.loads(subprocess.check_output(shlex.split(COMMAND)))[0]
        BUILD_ID = BUILD_DATA['id']
        BUILD_STATUS = BUILD_DATA['status']
        # if build status is successful, do nothing; if not successful, print log.
        def check_build(STATUS, GCB_ID):
            if STATUS is not 'FAILURE':
                print("""
        Build status is {} and ID is {}.
        See more details here:
            https://console.cloud.google.com/gcr/builds/{}
                """.format(STATUS, GCB_ID, GCB_ID))
            else:
                log = subprocess.check_output(shlex.split("gcloud container builds log {}".format(GCB_ID)))
                print("""
        Build failed. Printing log...
        {}
                """.format(log))

        check_build(BUILD_STATUS, BUILD_ID)

        FAIL_ID = "e9c8057c-f873-4982-b71e-efa89b1e9ec3" # ID of build known to failed
        check_build('FAILURE', FAIL_ID)
        # if < some logic that means its pending >:
        #     raise CheckPending('still goin')

        # if < some logic that means its failing >:
        #     raise CheckFailed( < some log lines > )
