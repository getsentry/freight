import logging

from itertools import chain

from freight.exceptions import ApiError

from . import manager, NotifierEvent, queue


def parse_notifiers_config(value):
    result = []
    for data in value:
        try:
            instance = manager.get(data["type"])
        except KeyError:
            raise ApiError(
                message=f"Invalid notifier: {data['type']}", name="invalid_notifier"
            )

        config = data.get("config", {})
        all_options = chain(
            list(instance.get_default_options().items()),
            list(instance.get_options().items()),
        )
        for option, option_values in all_options:
            value = config.get(option)
            if value and option_values.get("type"):
                try:
                    config[option] = option_values["type"](value)
                except (ValueError, TypeError):
                    raise ApiError(
                        message=f'Option "{option}" is not a valid type for notifier: {data["type"]}',
                        name="invalid_check",
                    )
            if option_values.get("required") and not value:
                raise ApiError(
                    message=f'Missing required option "{option}" for notifier: {data["type"]}',
                    name="invalid_notifier",
                )
        result.append({"type": data["type"], "config": config})
    return result


def send_task_notifications(task, event):
    for data in task.notifiers:
        notifier = manager.get(data["type"])
        config = data.get("config", {})
        if not notifier.should_send(task, config, event):
            continue

        # We want to send task finished notifications immediately as we know
        # there is no possible followup event
        if event == NotifierEvent.TASK_FINISHED:
            try:
                notifier.send(task, config, event)
            except Exception:
                logging.exception(
                    "%s notifier failed to send Task(id=%s)", data["type"], task.id
                )
        else:
            queue.put(task=task, type=data["type"], config=data["config"], event=event)


def clear_task_notifications(task):
    for data in task.notifiers:
        queue.remove(task=task, type=data["type"])
