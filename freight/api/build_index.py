from __future__ import absolute_import

from freight.api.bases.index import BaseIndexApiView
from freight.models import Build, BuildSequence


class BuildIndexApiView(BaseIndexApiView):
    def __init__(self):
        self.obj_model = Build
        self.sequence_model = BuildSequence
