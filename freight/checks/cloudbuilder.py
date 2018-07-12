from __future__ import absolute_import

import shlex
import subprocess

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

__all__ = ["GCPContainerBuilderCheck"]


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
        return {"project": {"required": True}, "oauth_token": {"required": False}}

    def check(self, app, sha, config):
        """Check build status

        Arguments:
            app {str} -- optional
            sha {str} -- required, commit SHA of build to check
            config {dict} -- optional dict to pass additional args
        """
        api_root = "https://cloudbuild.googleapis.com/v1/projects/{}/builds".format(
            config["project"]
        )

        oauth_command = "gcloud auth application-default print-access-token"

        oauth_token = config.get("oauth_token")
        if oauth_token is None:
            oauth_token = subprocess.check_output(shlex.split(oauth_command)).rstrip()

        params = {
            "filter": "sourceProvenance.resolvedRepoSource.commitSha={}".format(sha)
        }
        headers = {
            "Accepts": "application/json",
            "Authorization": "Bearer {}".format(oauth_token),
        }

        resp = http.get(api_root, headers=headers, params=params)
        if resp.status_code != 200:
            raise CheckFailed(
                "[ ERROR {} ]\tNo data for build present".format(resp.status_code)
            )

        build_data = resp.json()
        build_id = build_data["builds"][0]["id"]
        build_status = build_data["builds"][0]["status"]
        build_url = build_data["builds"][0]["logUrl"]
        build_logs = build_data["builds"][0]["logsBucket"]
        gcloudstatus = {
            "STATUS_UNKNOWN": "Status of the build is unknown.",
            "QUEUED": "Build or step is queued; work has not yet begun.",
            "WORKING": "Build or step is being executed.",
            "SUCCESS": "Build or step finished successfully.",
            "FAILURE": "Build or step failed to complete successfully.",
            "INTERNAL_ERROR": "Build or step failed due to an internal cause.",
            "TIMEOUT": "Build or step took longer than was allowed.",
            "CANCELLED": "Build or step was canceled by a user.",
        }

        if build_status == "FAILURE":
            print(build_id)
            build_logtext = "https://storage.googleapis.com/{}/log-{}.txt".format(
                build_logs[slice(5, None)], build_id
            )
            log = http.get(build_logtext, headers=headers)
            raise CheckFailed(
                "[ {} ]\t{}\nSee details: {}\nPrinting log...\n\n\n{}".format(
                    build_status, gcloudstatus["FAILURE"], build_url, log.text
                )
            )

        if build_status == "WORKING":
            raise CheckPending(
                "[ {} ]\t{}\nSee details: {}".format(
                    build_status, gcloudstatus["WORKING"], build_url
                )
            )
        if build_status == "SUCCESS":
            return
        raise CheckFailed
