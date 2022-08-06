__all__ = ["GitHubVcsRemote"]

import re
from typing import List, Tuple, TypedDict, Union, cast
from flask import current_app
from itertools import groupby

from freight import http

from .base import VcsRemote


def build_commit_query(repo_owner: str, repo_name: str, sha_list: List[str]):
    """
    Constructs a GraphQL query to query info for each sha in the sha_list.

    Note that the resulting object has each sha object aliased as `sha_N`,
    where N maps back to the index of the sha in the list.
    """
    sha_indexes = range(len(sha_list))

    sha_vars = [f"$sha_{i}: GitObjectID!," for i in sha_indexes]
    commit_objects = [
        f"sha_{i}: object(oid: $sha_{i}) {{ ...commitInfo }}" for i in sha_indexes
    ]

    query = """
      fragment commitInfo on Commit {{
        oid
        committedDate
        messageHeadline
        author {{
          email
          name
          avatarUrl
        }}
        associatedPullRequests(first: 1) {{
          nodes {{
            title
            url
            number
            labels(first: 10) {{
              nodes {{
                name
                color
              }}
            }}
          }}
        }}
      }}

      query(
          $repo_owner: String!,
          $repo_name: String!,
          {sha_vars}
      ) {{
        repository(owner: $repo_owner, name: $repo_name) {{
          {queries}
        }}
      }}
    """.format(
        sha_vars=" ".join(sha_vars),
        queries="\n".join(commit_objects),
    )

    variables = {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        **{f"sha_{i}": sha for i, sha in enumerate(sha_list)},
    }

    return {
        "query": query,
        "variables": variables,
    }


class ExternalCommit(TypedDict):
    repo_owner: str
    repo_name: str
    sha: str


def match_external_commit_message(message: str) -> Union[None, ExternalCommit]:
    result = re.search(
        r"(?P<repo_owner>[^\/]+)\/(?P<repo_name>[^\/]+)@(?P<sha>[0-9a-f]{5,40})",
        message,
    )

    if result is None:
        return None

    return cast(ExternalCommit, result.groupdict())


class GitHubVcsRemote(VcsRemote):
    hostname = "github.com"

    @property
    def repo_url(self) -> str:
        result = re.search(r"(?<=:)(?P<repo>[^\/]+\/[^.]+)", self.repo.url)

        if result is None:
            raise RuntimeError(
                "GitHub repo URL does not match expected format github.com:owner/repo.git"
            )

        repo = result.group("repo")
        return f"https://github.com/{repo}"

    @property
    def repo_parts(self) -> Tuple[str, str]:
        result = re.search(r"(?<=:)((?P<owner>[^\/]+)\/(?P<repo>[^.]+))", self.repo.url)

        if result is None:
            raise RuntimeError(
                "GitHub repo URL does not match expected format github.com:owner/repo.git"
            )

        return (result.group("owner"), result.group("repo"))

    def get_commit_url(self, sha: str) -> str:
        return f"{self.repo_url}/commit/{sha}"

    def get_commits_info(self, shas: List[str]):
        """
        Retrieves a list of changes, including pull request information, for a
        range of commit shas.

        The shas should be a contiguous list of shas from the git
        repository.
        """
        token = current_app.config["GITHUB_TOKEN"]
        headers = {
            "Authorization": f"token {token}",
        }

        if len(shas) == 0:
            return []

        repo_owner, repo_name = self.repo_parts
        query = build_commit_query(repo_owner, repo_name, shas)

        commits_resp = http.post(
            "https://api.github.com/graphql",
            json=query,
            headers=headers,
        )
        commits_dict = {
            commit["oid"]: commit
            for commit in commits_resp.json()["data"]["repository"].values()
        }

        # Resolve commits that are of the pattern `owner/repo@sha`. This
        # results in a map of the origin sha to a ExternalCommit dict.
        external_commits = {
            commit["oid"]: match_external_commit_message(commit["messageHeadline"])
            for commit in commits_dict.values()
        }

        # Filter out commits that don't have associated external commits
        external_commits = {k: c for k, c in external_commits.items() if c is not None}

        # Group external commits by repo so we can batch query for each repo
        external_commits_by_repo = groupby(
            external_commits.items(),
            key=lambda ec: (ec[1]["repo_owner"], ec[1]["repo_name"]),
        )

        # Fetch external_commit info for each repo
        for repo_info, repo_external_commits in external_commits_by_repo:
            repo_external_commits = dict(repo_external_commits)

            external_shas = [ec["sha"] for ec in repo_external_commits.values()]

            repo_owner, repo_name = repo_info
            query = build_commit_query(repo_owner, repo_name, external_shas)

            external_commits_resp = http.post(
                "https://api.github.com/graphql",
                headers=headers,
                json=query,
            )
            external_commits_dict = {
                c["oid"]: c
                for c in external_commits_resp.json()["data"]["repository"].values()
            }

            # Add an extra "external_commit" key to the associated commit in
            # the commits_dict
            for origin_sha, external_commit in repo_external_commits.items():
                external_sha = external_commit["sha"]

                # Add an `externalCommit` key to the commit on the commits_dict
                commit = external_commits_dict[external_sha]
                commits_dict[origin_sha]["externalCommit"] = commit

        # TODO Ensure order matches the shas list

        return list(commits_dict.values())

    def get_sha_range(self, ref1, ref2):
        token = current_app.config["GITHUB_TOKEN"]
        headers = {
            "Authorization": f"token {token}",
        }

        repo_owner, repo_name = self.repo_parts

        # XXX(epurkhiser): There is no graphql equivalent of the compare API.
        # Not a huge problem though, we can just use the REST API.
        compare_resp = http.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/compare/{ref2}...{ref1}",
            headers=headers,
        )

        return list(
            reversed([commit["sha"] for commit in compare_resp.json()["commits"]])
        )
