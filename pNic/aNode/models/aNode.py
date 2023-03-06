from django.db import models

from aMain.models import AbsCommonName
from .aNodeType import NodeType

# from aContext.models import Context


class Node(AbsCommonName):
    # context = models.ForeignKey(Context, on_delete=models.RESTRICT, null=True, blank=True)
    name = models.CharField(max_length=128, unique=False, null=False)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="parentNode",
    )

    nType = models.ForeignKey(
        NodeType,
        on_delete=models.CASCADE,
    )
    payLoad = models.JSONField(
        encoder=None,
        decoder=None,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Node"
        ordering = (
            "parent_id",
            "nType",
            "name",
        )
        unique_together = [
            [
                "parent",
                "nType",
                "name",
            ],
        ]
        indexes = [
            models.Index(
                fields=[
                    "parent",
                    "nType",
                    "name",
                ]
            ),
            models.Index(
                fields=[
                    "name",
                    "nType",
                    "parent",
                ]
            ),
        ]

    def __repr__(self):
        return "<%d>" % (self.id)

    def __str__(self):
        if self.parent:
            return "%s.%s" % (self.parent, self.name)
            # return "%s.%s[%s]" % (self.parent, self.nType.name, self.name)
        else:
            return ".%s" % (self.name)
            # return ".%s[%s]" % (self.nType.name, self.name)
