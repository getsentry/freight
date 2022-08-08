from flask_restful import reqparse

from freight import vcsremote
from freight.api.base import ApiView
from freight.models import App, Repository


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

        remote = vcsremote.get_by_repo(repo)

        shas = remote.get_sha_range(args.startRef, args.endRef)
        changes = remote.get_commits_info(shas)

        return self.respond(changes)
