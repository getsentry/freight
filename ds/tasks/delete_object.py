from __future__ import absolute_import, unicode_literals

import logging

from ds.config import celery, db
from ds.models import App


models = {
    'App': App,
}


@celery.task(name='ds.delete_object', max_retries=None)
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
