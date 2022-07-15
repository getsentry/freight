__all__ = ["GitHubAppsContextCheck"]


from flask import current_app

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

ERR_CHECK = "[{status}] {name}: {description} ({details_url})"
ERR_MISSING_CONTEXT = "{} context was not found"


class GitHubAppsContextCheck(Check):
    def get_options(self):
        return {
            "api_root": {"required": False},
            # if contexts is not set it will require all of them be valid
            "contexts": {"required": False},
            "repo": {"required": True},
        }

    def _check(self, app, sha, config, fatal=False):
        token = current_app.config["GITHUB_TOKEN"]
        if not token:
            raise CheckFailed("GITHUB_TOKEN is not set")

        api_root = (
            config.get("api_root") or current_app.config["GITHUB_API_ROOT"]
        ).rstrip("/")

        all_contexts = set(config.get("contexts") or [])
        contexts = all_contexts.copy()
        repo = config["repo"]

        url = f"{api_root}/repos/{repo}/commits/{sha}/check-runs"

        headers = {
            "Accept": "application/vnd.github.antiope-preview+json",
            "Authorization": f"token {token}",
        }

        params = {
            "per_page": 100,
            "page": 1,
        }

        total_count = None
        check_runs = []

        while True:
            resp = http.get(url, headers=headers, params=params)

            check_runs_dict = resp.json()
            if not check_runs_dict or not check_runs_dict.get("total_count"):
                raise CheckFailed(
                    "No contexts were present in GitHub. "
                    "This means that no statuses, like CI results, "
                    "were found for the commit. You may want to wait a bit, "
                    "or failing that, deploy a new commit."
                )

            if total_count is None:
                total_count = int(check_runs_dict["total_count"])

            check_runs.extend(check_runs_dict.get("check_runs", []))

            if params["per_page"] * params["page"] >= total_count:
                break
            else:
                params["page"] += 1

        valid_contexts = set()
        for check_run in check_runs:
            check_name = check_run["name"]
            if all_contexts and check_name not in all_contexts:
                continue
            if check_run["conclusion"] == "success":
                valid_contexts.add(check_name)
                try:
                    contexts.remove(check_name)
                except KeyError:
                    pass
            if check_name in valid_contexts:
                continue
            if contexts and check_name not in contexts:
                continue

            check_run["description"] = check_run["output"]["title"]
            if check_run["status"] in ["queued", "in_progress"]:
                raise CheckPending(ERR_CHECK.format(**check_run))
            elif check_run["conclusion"] != "success":
                raise CheckFailed(ERR_CHECK.format(**check_run))
            contexts.remove(check_name)

        if contexts and fatal:
            raise CheckFailed(ERR_MISSING_CONTEXT.format(next(iter(contexts))))

    def check(self, app, sha, config):
        retries = int(config.get("retries")) or 0
        while retries:
            retries -= 1
            self._check(app, sha, config)
        self._check(app, sha, config, fatal=True)
