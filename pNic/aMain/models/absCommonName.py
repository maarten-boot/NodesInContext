from django.db import models

from .absBase import AbsBase


class AbsCommonName(AbsBase):
    # having Name
    name = models.CharField(max_length=128, unique=True, null=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return "<%s>" % (self.name)

    def __str__(self):
        return "<%s>" % (self.name)
