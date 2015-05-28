from __future__ import absolute_import

__all__ = ['GitHubContextCheck']


from flask import current_app

from freight import http
from freight.exceptions import CheckFailed, CheckPending

from .base import Check

ERR_CHECK = '{} context is {}'
ERR_MISSING_CONTEXT = '{} context was not found'


class GitHubContextCheck(Check):
    def get_options(self):
        return {
            'api_root': {'required': False},
            'contexts': {'required': True},
            'repo': {'required': True},
        }

    def check(self, app, sha, config):
        token = current_app.config['GITHUB_TOKEN']
        if not token:
            raise CheckFailed('GITHUB_TOKEN is not set')

        api_root = (
            config.get('api_root') or current_app.config['GITHUB_API_ROOT']
        ).rstrip('/')

        contexts = set(config['contexts'])
        repo = config['repo']

        url = '{api_root}/repos/{repo}/commits/{ref}/statuses'.format(
            api_root=api_root,
            repo=repo,
            ref=sha,
        )

        headers = {
            'Accepts': 'application/json',
            'Authorization': 'token {}'.format(token),
        }

        resp = http.get(url, headers=headers)

        for data in resp.json():
            if data['context'] not in contexts:
                continue
            if data['state'] == 'pending':
                raise CheckPending(ERR_CHECK.format(data['context'], data['state']))
            elif data['state'] != 'success':
                raise CheckFailed(ERR_CHECK.format(data['context'], data['state']))
            contexts.remove(data['context'])

        if contexts:
            raise CheckFailed(ERR_MISSING_CONTEXT.format(iter(contexts).next()))
