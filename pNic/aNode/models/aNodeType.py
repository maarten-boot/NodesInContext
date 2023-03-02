# from django.db import models

from aMain.models import AbsCommonName


class NodeType(AbsCommonName):
    class Meta:
        verbose_name_plural = "NodeType"
        ordering = ("name",)

    def __repr__(self):
        return "<%s>" % (self.name)

    def __str__(self):
        return "<%s>" % (self.name)
