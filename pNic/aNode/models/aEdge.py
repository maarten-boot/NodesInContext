from django.db import models

from aMain.models import AbsBase
from .aEdgeType import EdgeType
from .aNode import Node


class Edge(AbsBase):
    fromNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="fromNode")
    toNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="toNode")
    eType = models.ForeignKey(EdgeType, on_delete=models.CASCADE)
    #
    description = models.TextField(blank=True, null=True)
    payLoad = models.JSONField(
        encoder=None,
        decoder=None,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Edge"
        indexes = [
            models.Index(fields=["fromNode", "toNode", "eType"]),
            models.Index(fields=["toNode", "fromNode", "eType"]),
            models.Index(fields=["eType", "fromNode", "toNode"]),
            models.Index(fields=["eType", "toNode", "fromNode"]),
        ]
        unique_together = [["fromNode", "toNode", "eType"]]

        ordering = (
            "fromNode",
            "toNode",
            "eType",
        )

    def __repr__(self):
        return "<%d>" % (self.id)

    def __str__(self):
        return "<%d>" % (self.id)
