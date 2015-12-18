from __future__ import absolute_import

import logging

from freight.config import db, queue
from freight.models import App


models = {
    'App': App,
}


@queue.job()
def delete_object(model, object_id):
    try:
        Model = models[model]
    except KeyError:
        logging.error('DeleteObject fired with missing model(name=%s)', model)
        return

    obj = Model.query.get(object_id)
    if not obj:
        logging.warning('DeleteObject fired with missing %s(id=%s)', model, object_id)
        return

    db.session.delete(obj)
