from django.db import models


class AbsBase(models.Model):
    # The absolute Basics for all
    id = models.AutoField(primary_key=True)
    creStamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=False)
    updStamp = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return "<%d>" % (self.id)

    def __str__(self):
        return "<%d>" % (self.id)
