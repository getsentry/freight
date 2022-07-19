from freight.exceptions import ApiError

from . import manager


def parse_provider_config(type, config):
    try:
        instance = manager.get(type)
    except KeyError:
        raise ApiError(message=f"Invalid provider: {type}", name="invalid_provider")

    result = {}
    all_options = {**instance.get_default_options(), **instance.get_options()}

    for key in config:
        if not all_options.get(key):
            raise ApiError(
                message=f"You specified config key {key}, but it isn't recognized for the provider {type}.",
                name="invalid_provider",
            )

    for option, option_values in all_options.items():
        value = config.get(option)
        if value and option_values.get("type"):
            try:
                config[option] = option_values["type"](value)
            except (ValueError, TypeError):
                raise ApiError(
                    message=f'Option "{option}" is not a valid type for provider: {type}',
                    name="invalid_check",
                )
        if option_values.get("required") and not value:
            raise ApiError(
                message=f'Missing required option "{option}" for provider: {type}',
                name="invalid_provider",
            )
        result[option] = value
    return result
