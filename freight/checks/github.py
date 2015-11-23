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
            # if contexts is not set it will require all of them be valid
            'contexts': {'required': False},
            'repo': {'required': True},
        }

    def check(self, app, sha, config):
        token = current_app.config['GITHUB_TOKEN']
        if not token:
            raise CheckFailed('GITHUB_TOKEN is not set')

        api_root = (
            config.get('api_root') or current_app.config['GITHUB_API_ROOT']
        ).rstrip('/')

        contexts = set(config.get('contexts') or [])
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

        context_list = resp.json()
        if not context_list:
            raise CheckFailed('No contexts were present in GitHub')

        valid_contexts = set()
        for data in context_list:
            if data['state'] == 'success':
                valid_contexts.add(data['context'])
                try:
                    contexts.remove(data['context'])
                except KeyError:
                    pass
            if data['context'] in valid_contexts:
                continue
            if contexts and data['context'] not in contexts:
                continue
            if data['state'] == 'pending':
                raise CheckPending(ERR_CHECK.format(data['context'], data['state']))
            elif data['state'] != 'success':
                raise CheckFailed(ERR_CHECK.format(data['context'], data['state']))
            contexts.remove(data['context'])

        if contexts:
            raise CheckFailed(ERR_MISSING_CONTEXT.format(iter(contexts).next()))
