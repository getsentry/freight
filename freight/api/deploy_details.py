from __future__ import absolute_import

from freight.api.bases.details import BaseDetailsApiView
from freight.models import Deploy


class DeployDetailsApiView(BaseDetailsApiView):
    def __init__(self):
        self.obj_model = Deploy
