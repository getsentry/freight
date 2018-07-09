from __future__ import absolute_import

import shlex
import subprocess

from flask import current_app

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
        CheckPending -- exception to raise if build status is in progress
        CheckFailed -- exception to raise when check for build status fails
    """
    def get_options(self):
        return {
            'project': {'required': True},
            'oauth_token': {'required': False},
        }

    def check(self, app, sha, config):
        """Check build status

        Arguments:
            app {str} -- optional
            sha {str} -- required, commit SHA of build to check
            config {dict} -- optional dict to pass additional args
        """
        project = config.get('project')

        api_root = 'https://cloudbuild.googleapis.com/v1/projects/{}/builds'.format(
            project
        )

        all_contexts = set(config.get('contexts') or [])
        contexts = all_contexts.copy()

        oauth_command = "gcloud auth application-default print-access-token"
        try:
            oauth_token = current_app.config['oauth_token'] or config.get('oauth_token')
        except:
            oauth_token = subprocess.check_output(shlex.split(oauth_command)).rstrip()

        params = {
            'filter': 'sourceProvenance.resolvedRepoSource.commitSha={}'.format(sha)
        }
        headers = {
            'Accepts': 'application/json',
            'Authorization': 'Bearer {}'.format(oauth_token)
        }

        build_data = http.get(api_root, headers=headers, params=params).json()
        if not build_data:
            raise CheckFailed('No data for build present')

        build_id = build_data['builds'][0]['id']
        build_status = build_data['builds'][0]['status']
        build_url = build_data['builds'][0]['logUrl']
        build_logs = build_data['builds'][0]['logsBucket'].lstrip('gs:/')

        if build_status == "Failure":
            build_logtext = 'https://storage.googleapis.com/{}/log-{}.txt'.format(build_logs, build_id)
            log = http.get(build_logtext, headers=headers)
            # log = subprocess.check_output(shlex.split("gcloud container builds log {}".format(build_id)))
            print("Build failed. Printing log...\n\n\n{}".format(log.text))
            raise CheckFailed()

        if build_status != 'SUCCESS':
            print("Build status is {} and ID is {}.\n\n".format(build_status, build_id))
            # raise CheckPending("See more details here:\n{}".format(build_url))
            raise CheckPending('build not complete')

        if build_status == 'SUCCESS':
            print "Build succeeded. See details: {}".format(build_url)
