from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.config import db
from freight.models import LogChunk

from .deploy_details import DeployMixin

# Edit this file so that I can actually seperate the chunks of data instead of
# appending them to one big ass text chunk.


class DeployLogApiView(ApiView, DeployMixin):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', location='args', type=int, default=0)
    get_parser.add_argument('limit', location='args', type=int)

    def get(self, **kwargs):
        """
        Retrieve deploy log.
        """
        deploy = self._get_deploy(**kwargs)
        if deploy is None:
            return self.error('Invalid deploy', name='invalid_resource', status_code=404)

        args = self.get_parser.parse_args()

        queryset = db.session.query(
            LogChunk.text, LogChunk.offset, LogChunk.size, LogChunk.date_created,
        ).filter(
            LogChunk.task_id == deploy.task_id,
        ).order_by(LogChunk.offset.asc())

        if args.offset == -1:
            # starting from the end so we need to know total size
            tail = db.session.query(LogChunk.offset + LogChunk.size).filter(
                LogChunk.task_id == deploy.task_id,
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
            'nextOffset': next_offset,
            'chunks': [{
                'text': c.text,
                'date': c.date_created.isoformat(),
            } for c in logchunks]
        }

        return self.respond(context, links=links)
