from __future__ import absolute_import

__all__ = ['GitHubHooks']

from flask import current_app, request, Response

from .base import Hook
from freight.testutils.client import AuthenticatedTestClient


class GitHubHooks(Hook):
    def ok(self):
        return Response()

    def deploy(self, app, env):
        payload = request.get_json()
        event = request.headers.get('X-GitHub-Event')

        if event != 'push':
            # Gracefully ignore everything except push events
            return self.ok()

        default_ref = app.get_default_ref(env)
        ref = payload['ref']

        if ref != 'refs/heads/{}'.format(default_ref):
            return self.ok()

        head_commit = payload['head_commit']
        committer = head_commit['committer']

        client = AuthenticatedTestClient(
            current_app, current_app.response_class
        )

        return client.post('/api/0/deploys/', data={
            'env': env,
            'app': app.name,
            'ref': head_commit['id'],
            'user': head_commit['committer']['email'],
        })
