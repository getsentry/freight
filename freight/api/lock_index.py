from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db
from freight.models import App, User, Lock
from freight.utils.auth import get_current_user


class LockIndexApiView(ApiView):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('app', location='args')
    get_parser.add_argument('user', location='args')
    get_parser.add_argument('env', location='args')
    get_parser.add_argument('active', location='args')

    def get(self):
        """
        Retrieve a list of locks.
        """
        args = self.get_parser.parse_args()

        qs_filters = []

        if args.app:
            app = App.query.filter(App.name == args.app).first()
            if not app:
                return self.respond([])
            qs_filters.append(Lock.app_id == app.id)

        if args.user:
            app = User.query.filter(User.name == args.app).first()
            if not app:
                return self.respond([])
            qs_filters.append(Lock.user_id == User.id)

        if args.env:
            qs_filters.append(Lock.environment == args.env)

        if args.active:
            qs_filters.append(not Lock.date_unlocked)

        lock_qs = Lock.query.filter(*qs_filters).order_by(Lock.id.desc())

        return self.paginate(lock_qs, on_results=serialize)

    post_parser = reqparse.RequestParser()
    get_parser.add_argument('app', required=True)
    get_parser.add_argument('user', required=True)
    get_parser.add_argument('env', required=True)
    get_parser.add_argument('msg', required=True)

    def post(self):
        """
        Create a new lock.
        """
        args = self.post_parser.parse_args()

        app = App.query.filter(App.name == args.app).first()
        if not app:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        user = App.query.filter(User.name == args.user).first()
        if not user:
            user = get_current_user()

        lock = Lock(
            app_id=app.id,
            user_id=user.id,
            environment=args.env,
            message=args.msg,
        )

        db.session.add(lock)
        db.session.commit()

        return self.respond(serialize(lock), status_code=201)
