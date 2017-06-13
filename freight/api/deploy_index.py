from __future__ import absolute_import

from freight.api.bases.index import BaseIndexApiView
from freight.models import Deploy, DeploySequence


class DeployIndexApiView(BaseIndexApiView):
    def __init__(self):
        self.obj_model = Deploy
        self.sequence_model = DeploySequence
