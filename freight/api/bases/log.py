from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.bases.details import BaseMixin
from freight.config import db
from freight.models import LogChunk


class BaseLogApiView(ApiView, BaseMixin):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', location='args', type=int, default=0)
    get_parser.add_argument('limit', location='args', type=int)

    def __init__(self):
        raise NotImplementedError
        # self.obj_model = Task

    def get(self, **kwargs):
        """
        Retrieve a log.
        """
        kwargs['obj_model'] = self.obj_model
        obj = self._get_obj(**kwargs)
        if obj is None:
            return self.error(
                'Invalid {}'.format(type(obj)),
                name='invalid_resource',
                status_code=404
            )

        args = self.get_parser.parse_args()

        queryset = db.session.query(
            LogChunk.text, LogChunk.offset, LogChunk.size
        ).filter(
            LogChunk.task_id == obj.task_id,
        ).order_by(LogChunk.offset.asc())

        if args.offset == -1:
            # starting from the end so we need to know total size
            tail = db.session.query(LogChunk.offset + LogChunk.size).filter(
                LogChunk.task_id == obj.task_id,
            ).order_by(LogChunk.offset.desc()).limit(1).scalar()

            if tail is None:
                logchunks = []
            else:
                if args.limit:
                    queryset = queryset.filter(
                        (LogChunk.offset + LogChunk.size) >= max(tail - args.limit + 1, 0),
                    )
        else:
            if args.offset:
                queryset = queryset.filter(
                    LogChunk.offset >= args.offset,
                )
            if args.limit:
                queryset = queryset.filter(
                    LogChunk.offset < args.offset + args.limit,
                )

        logchunks = list(queryset)

        if logchunks:
            next_offset = logchunks[-1].offset + logchunks[-1].size
        else:
            next_offset = args.offset

        links = [self.build_cursor_link('next', next_offset)]

        context = {
            'text': ''.join(l.text for l in logchunks),
            'nextOffset': next_offset,
        }

        return self.respond(context, links=links)
