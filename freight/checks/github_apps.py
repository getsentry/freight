__all__ = ["GitHubAppsContextCheck"]

import json

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

    def check(self, app, sha, config):
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

        resp = http.get(url, headers=headers)

        check_runs_dict = json.loads(resp.data.decode("utf8"))
        if not check_runs_dict or not check_runs_dict.get("total_count"):
            raise CheckFailed("No contexts were present in GitHub")

        valid_contexts = set()
        for check_run in check_runs_dict.get("check_runs", []):
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

        if contexts:
            raise CheckFailed(ERR_MISSING_CONTEXT.format(next(iter(contexts))))
