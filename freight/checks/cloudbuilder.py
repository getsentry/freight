from __future__ import absolute_import

import shlex
import subprocess

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

__all__ = ['GCPContainerBuilderCheck']


class GCPContainerBuilderCheck(Check):
    """Track progress of builds created by Google Cloud Container Builder
    Jira ticket: OPS-111

    Add a Freight Check alongside the GitHub check that will:
    1) Print the "waiting for build yadda yadda <link to build>"
    2) Error if the build is not found, just like the GitHub check.
    3) Exit cleanly if the build for the repo+sha is successful.
    4) Print a sensible (50 lines to start) amount of the log if the build fails.

    Raises:
        CheckPending -- exception if build is in progress
        CheckFailed -- exception if build fails
    """
    def check_build(self, app, sha, config):
        """Check build status
        """
        api_root = 'https://cloudbuild.googleapis.com/v1/projects/internal-sentry/builds'
        commit_sha = "f8626d73efdd496c101f386179616c6229194a8e"   # this comes from the check() method

        oauth_command = "gcloud auth application-default print-access-token"
        oauth_token = subprocess.check_output(shlex.split(oauth_command)).rstrip()

        params = {'filter': 'sourceProvenance.resolvedRepoSource.commitSha = "{}"'.format(commit_sha)}
        headers = {
            'Accepts': 'application/json',
            'Authorization': 'Bearer {}'.format(oauth_token)
        }

        build_data = http.get(api_root, headers=headers, params=params).json()
        if not build_data:
            raise CheckFailed('No data for build present')
        # repo = config['repo']

        build_id = build_data['builds'][0]['id']
        build_status = build_data['builds'][0]['status']
        build_url = build_data['builds'][0]['logUrl']

        if build_status is not 'Failure':
            print("""Build status is {} and ID is {}.
            See more details here:
            {}
            """.format(build_status, build_id, build_url))
            raise CheckPending
        else:
            log = subprocess.check_output(shlex.split("gcloud container builds log {}".format(build_id)))
            print("""Build failed. Printing log...
            {} """.format(log))
            raise CheckFailed
