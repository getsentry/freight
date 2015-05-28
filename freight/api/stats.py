from __future__ import absolute_import

from datetime import date, timedelta
from sqlalchemy.sql import func

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db
from freight.models import Task


class StatsApiView(ApiView):
    def get(self):
        """
        Retrieve daily statistics for tasks.
        """
        end_date = date.today() - timedelta(days=30)

        results = dict(db.session.query(
            func.date(Task.date_started),
            func.count(),
        ).filter(
            Task.date_started > end_date,
        ).group_by(
            func.date(Task.date_started),
        ))

        points = []
        for day in range(31):
            point_date = end_date + timedelta(days=day)
            points.append((
                int(point_date.strftime('%s')),
                results.get(point_date, 0),
            ))

        return self.respond(serialize(points), status_code=200)
