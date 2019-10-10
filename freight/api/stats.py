from datetime import date, timedelta

from flask_restful import reqparse
from sqlalchemy.sql import func

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db
from freight.models import App, Task


class StatsApiView(ApiView):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument("app", location="args")

    def get(self):
        """
        Retrieve daily statistics for tasks.
        """
        args = self.get_parser.parse_args()
        end_date = date.today() - timedelta(days=30)

        qs_filters = [Task.date_started > end_date]

        if args.app:
            try:
                app = App.query.filter(App.name == args.app).first()
                qs_filters.append(Task.app_id == app.id)
            except IndexError:
                # TODO: what to do if app is not found?
                return []

        results = dict(
            db.session.query(func.date(Task.date_started), func.count())
            .filter(*qs_filters)
            .group_by(func.date(Task.date_started))
        )

        points = []
        for day in range(31):
            point_date = end_date + timedelta(days=day)
            points.append((int(point_date.strftime("%s")), results.get(point_date, 0)))

        return self.respond(serialize(points), status_code=200)
