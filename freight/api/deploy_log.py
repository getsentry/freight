from __future__ import absolute_import

from freight.api.bases.log import BaseLogApiView
from freight.models import Deploy


class DeployLogApiView(BaseLogApiView):
    def __init__(self):
        self.obj_model = Deploy
