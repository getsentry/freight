from flask_restful import reqparse

from freight import vcs, vcsremote
from freight.api.base import ApiView
from freight.models import App, Repository
from freight.utils.workspace import Workspace
from freight.utils.redis import lock
from freight.config import redis


class RemoteChangesApiView(ApiView):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("startRef", location="args", type=str, required=True)
    get_parser.add_argument("endRef", location="args", type=str, required=True)

    def get(self, app):
        """
        Get a specified list of changes from the VCS remote for an app
        """
        args = self.get_parser.parse_args()

        app = App.query.filter(App.name == app).first()
        repo = Repository.query.get(app.repository_id)

        workspace = Workspace(path=repo.get_path())
        vcs_backend = vcs.get(repo.vcs, url=repo.url, workspace=workspace)

        # Ensure the repo is cloned and up to date so we can get a list of
        # changes for the ref range
        with lock(redis, f"repo:update:{repo.id}"):
            vcs_backend.clone_or_update()

        shas = vcs_backend.get_sha_range(args.startRef, args.endRef)

        # Limit the number of shas so we don't end up making our API requests
        # to the VCS remote too big.
        shas = shas[:75]

        remote = vcsremote.get_by_repo(repo)
        changes = remote.get_commits_info(shas)

        return self.respond(changes)
