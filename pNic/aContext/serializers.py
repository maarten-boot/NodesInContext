from rest_framework import serializers

from aContext.models import Context


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = [
            "id",
            "parent",
            "name",
            "description",
        ]
