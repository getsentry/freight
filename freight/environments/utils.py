from __future__ import absolute_import

from freight.exceptions import ApiError


def parse_environments_config(value):
    if not isinstance(value, dict):
        raise ApiError(
            message='Invalid data type for environments',
            name='invalid_environment',
        )

    result = {}
    for env_name, data in value.iteritems():
        if not isinstance(data, dict):
            raise ApiError(
                message='Invalid data type for environment "{}"'.format(env_name),
                name='invalid_environment',
            )

        result[env_name] = {
            'default_ref': data.get('default_ref', 'master'),
        }
    return result
