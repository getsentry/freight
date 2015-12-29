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
            # TODO(dcramer): this is a mess, we should unify the API to just look
            # like JSON
            'default_ref': data.get('defaultRef', data.get('default_ref', 'master')),
        }
    return result
