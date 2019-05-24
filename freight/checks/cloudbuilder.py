from subprocess import check_output

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

    required = True

    def get_options(self):
        return {"project": {"required": True}, "oauth_token": {"required": False}}

    def check(self, app, sha, config):
        """Check build status

        Arguments:
            app {str} -- optional
            sha {str} -- required, commit SHA of build to check
            config {dict} -- optional dict to pass additional args
        """
        api_root = (
            f"https://cloudbuild.googleapis.com/v1/projects/{config['project']}/builds"
        )

        oauth_token = config.get("oauth_token")
        if oauth_token is None:
            oauth_token = (
                check_output(["gcloud", "auth", "print-access-token"])
                .rstrip()
                .decode("utf-8")
            )

        params = {"filter": f'sourceProvenance.resolvedRepoSource.commitSha="{sha}"'}
        headers = {
            "Accepts": "application/json",
            "Authorization": f"Bearer {oauth_token}",
        }

        resp = http.get(api_root, headers=headers, params=params)
        if resp.status_code != 200:
            if resp.status_code == 503:
                raise CheckPending("Temporary Google failure")

            raise CheckFailed(
                f"[ ERROR {resp.status_code} ]\tNo data for build present"
            )

        build_data = resp.json()
        if "builds" not in build_data:
            raise CheckPending("Build has not started yet.")

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
            build_logtext = f"https://storage.googleapis.com/{build_logs[5:].rstrip('/')}/log-{build_id}.txt"
            log = http.get(build_logtext, headers=headers)
            raise CheckFailed(
                f"[ {build_status} ]\t{gcloudstatus['FAILURE']}\nSee details: {build_url}\nPrinting log...\n\n\n{log.text}"
            )

        if build_status in ["QUEUED", "WORKING"]:
            raise CheckPending(
                f"[ {build_status} ]\t{gcloudstatus[build_status]}\nSee details: {build_url}"
            )
        if build_status == "SUCCESS":
            return

        raise CheckFailed(f"[ {build_status} ]\t{gcloudstatus[build_status]}\n")
