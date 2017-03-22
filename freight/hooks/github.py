from __future__ import absolute_import

__all__ = ['GitHubHooks']

from flask import request, Response

from .base import Hook


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
        if not head_commit:
            # Deleting a branch is one case, not sure of others
            return self.ok()

        committer = head_commit['committer']

        return self.client().post('/api/0/deploys/', data={
            'env': env,
            'app': app.name,
            'ref': head_commit['id'],
            'user': head_commit['committer']['email'],
        })
