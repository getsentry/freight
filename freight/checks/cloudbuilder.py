from __future__ import absolute_import

import json
import shlex
import subprocess

from freight.exceptions import CheckFailed, CheckPending

from .base import Check

__all__ = ['GCPContainerBuilderCheck']


ERR_CHECK = '[{state}] {context}: {description} ({target_url})'
ERR_MISSING_CONTEXT = '{} context was not found'


class GCPContainerBuilderCheck(Check):
    """Track progress of builds created by Google Cloud Container Builder
    Jira ticket: https: // getsentry.atlassian.net / browse / OPS - 111

    Arguments:
        Check {[type]} -- [description]

    Raises:
        CheckPending -- [description]
        CheckFailed -- [description]
    """

    def check_build(self, app, sha, config, repo):
        """Check build status
        """
        COMMAND = """gcloud container builds list
            --filter 'source.repo_source.repo_name={} AND
            source_provenance.resolved_repo_source.commit_sha={}'
            --format='json' """.format(repo, sha)
        BUILD_DATA = json.loads(
            subprocess.check_output(shlex.split(COMMAND)))[0]
        BUILD_ID = BUILD_DATA['id']
        BUILD_STATUS = BUILD_DATA['status']
        # if build status is successful, do nothing; if not successful, print log.

        if BUILD_STATUS is not 'FAILURE':
            print("""Build status is {} and ID is {}.
            See more details here:
            https://console.cloud.google.com/gcr/builds/{}
            """.format(BUILD_STATUS, BUILD_ID, BUILD_ID))
            raise CheckPending
        else:
            raise CheckFailed
            log = subprocess.check_output(shlex.split("gcloud container builds log {}".format(BUILD_ID)))
            print("""Build failed. Printing log...
            {} """.format(log))
