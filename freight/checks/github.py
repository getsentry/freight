__all__ = ["GitHubContextCheck"]


from flask import current_app

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

ERR_CHECK = "[{state}] {context}: {description} ({target_url})"
ERR_MISSING_CONTEXT = "{} context was not found"


class GitHubContextCheck(Check):
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

        url = f"{api_root}/repos/{repo}/commits/{sha}/statuses"

        headers = {"Accepts": "application/json", "Authorization": f"token {token}"}

        resp = http.get(url, headers=headers)

        context_list = resp.json()
        if not context_list:
            raise CheckFailed("No contexts were present in GitHub")

        valid_contexts = set()
        for data in context_list:
            if all_contexts and data["context"] not in all_contexts:
                continue
            if data["state"] == "success":
                valid_contexts.add(data["context"])
                try:
                    contexts.remove(data["context"])
                except KeyError:
                    pass
            if data["context"] in valid_contexts:
                continue
            if contexts and data["context"] not in contexts:
                continue
            if data["state"] == "pending":
                raise CheckPending(ERR_CHECK.format(**data))
            elif data["state"] != "success":
                raise CheckFailed(ERR_CHECK.format(**data))
            contexts.remove(data["context"])

        if contexts:
            raise CheckFailed(ERR_MISSING_CONTEXT.format(next(iter(contexts))))
