from django.db import models

from aMain.models import AbsCommonName


class Context(AbsCommonName):
    parent = models.ForeignKey(
        "self",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="parentContext",
    )

    class Meta:
        verbose_name_plural = "Context"
        ordering = (
            "parent_id",
            "name",
        )

        unique_together = [
            ["parent", "name"],
        ]
        indexes = [
            models.Index(fields=["parent", "name"]),
            models.Index(fields=["name", "parent"]),
        ]

    def __repr__(self):
        return "<%d>" % (self.id)

    def __str__(self):
        if self.parent:
            return "%s.%s" % (self.parent, self.name)
        else:
            return ".%s" % (self.name)
