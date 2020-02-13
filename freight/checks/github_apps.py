__all__ = ["GitHubAppsContextCheck"]


from flask import current_app

from freight import http
from freight.config import redis
from freight.models import App
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

ERR_CHECK = "[{status}] {name}: {description} ({details_url})"
ERR_MISSING_CONTEXT = "{} context was not found"
ERR_NO_CONTEXT_ON_FIRST_RUN = "No GitHub contexts found (yet)"
ERR_NO_CONTEXT = "No contexts were present on GitHub"

FIRST_CHECK_TIMEOUT = 120


class GitHubAppsContextCheck(Check):
    def get_options(self):
        return {
            "api_root": {"required": False},
            # if contexts is not set it will require all of them be valid
            "contexts": {"required": False},
            "repo": {"required": True},
        }

    def _retry_on_first_run(self, condition: bool, app: App, sha: str, reason: str,
                            msg_pending: str, msg_failed: str):
        """
        Retry the check later if the given condition is True and it's the first run

        We need to pass the condition and clean up if it's False because we have no
        information about deploy ID here. We rely on the fact that only one deploy and check
        can be executed for the same app at the given moment.
        """
        cache_key = f"github_apps:{app.name}:{sha}:{reason}"
        exists = b'1'

        if condition:
            if redis.get(cache_key) == exists:
                # Not the first run => probably a configuration error
                redis.delete(cache_key)
                raise CheckFailed(msg_failed)
            else:
                # First run => retry
                redis.set(cache_key, exists, ex=FIRST_CHECK_TIMEOUT)
                raise CheckPending(msg_pending)
        else:
            redis.delete(cache_key)

    def check(self, app: App, sha: str, config: dict):
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

        check_runs_dict = resp.json()
        # GitHub is sometimes slow to update commit context, so we can
        # tolerate empty context list on the first run
        self._retry_on_first_run(condition=(not check_runs_dict or not check_runs_dict.get("total_count")),
                                 app=app, sha=sha, reason="empty_context",
                                 msg_pending=ERR_NO_CONTEXT_ON_FIRST_RUN,
                                 msg_failed=ERR_NO_CONTEXT)

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

        # Retry on the first iteration, since GitHub might need some time
        first_context = next(iter(contexts)) if contexts else None
        self._retry_on_first_run(condition=bool(contexts),
                                 app=app, sha=sha, reason="missing_context",
                                 msg_pending=ERR_NO_CONTEXT_ON_FIRST_RUN,
                                 msg_failed=ERR_MISSING_CONTEXT.format(first_context))
