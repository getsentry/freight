from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.schema import Index, UniqueConstraint

from freight.config import db
from freight.db.types.json import JSONEncodedDict


class TaskConfigType(object):
    deploy = 0

    @classmethod
    def get_label(cls, status):
        return TYPE_LABELS[status]

    @classmethod
    def label_to_id(cls, label):
        return TYPE_LABELS_REV[label]


TYPE_LABELS = {TaskConfigType.deploy: "deploy"}
TYPE_LABELS_REV = {v: k for k, v in list(TYPE_LABELS.items())}


class TaskConfig(db.Model):
    """
    Example TaskConfig:

    {
        "provider_config": {
            "timeout": 1200,
            "command": "bin/fab --colorize-errors -a -i {ssh_key} -R {environment} deploy:branch_name={sha}"
        },
        "provider": "shell",
        "checks": [
            {
                "type": "github",
                "config": {
                    "contexts": [
                        "ci/circleci"
                    ],
                    "repo": "getsentry/getsentry"
                }
            }
        ],
        "notifiers": [
            {
                "type": "slack",
                "config": {
                    "webhook_url": "..."
                }
            },
            {
                "type": "datadog",
                "config": {
                    "webhook_url": "..."
                }
            }
        ]
    }
    """

    __tablename__ = "taskconfig"
    __table_args__ = (
        Index("idx_taskconfig_app_id", "app_id"),
        Index("idx_taskconfig_type", "type"),
        UniqueConstraint("app_id", "type", name="unq_app_id_type"),
    )

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(64), nullable=False)
    type = Column(Integer)
    data = Column(JSONEncodedDict)

    @property
    def checks(self):
        return self.data.get("checks", [])

    @property
    def notifiers(self):
        return self.data.get("notifiers", [])

    @property
    def provider_config(self):
        return self.data.get("provider_config", {})

    @property
    def environments(self):
        return self.data.get("environments", {})

    @property
    def type_label(self):
        return TYPE_LABELS[self.type]
