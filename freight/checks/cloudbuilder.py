from __future__ import absolute_import

import json
import shlex
import subprocess

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
        repo = config['repo']
        command = """gcloud container builds list
            --filter 'source.repo_source.repo_name={} AND
            source_provenance.resolved_repo_source.commit_sha={}'
            --format='json' """.format(repo, sha)
        build_data = json.loads(
            subprocess.check_output(shlex.split(command)))[0]
        build_id = build_data['id']
        build_status = build_data['status']

        if build_status is not 'Failure':
            print("""Build status is {} and ID is {}.
            See more details here:
            https://console.cloud.google.com/gcr/builds/{}
            """.format(build_status, build_id, build_id))
            raise CheckPending
        else:
            log = subprocess.check_output(shlex.split("gcloud container builds log {}".format(build_id)))
            print("""Build failed. Printing log...
            {} """.format(log))
            raise CheckFailed
