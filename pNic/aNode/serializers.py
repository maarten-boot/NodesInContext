from rest_framework import serializers


from aNode.models import NodeType
from aNode.models import Node
from aNode.models import EdgeType
from aNode.models import Edge


class NodeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeType
        fields = [
            "id",
            "name",
            "description",
        ]


class EdgeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdgeType
        fields = [
            "id",
            "name",
            "description",
        ]


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = [
            "id",
            "description",
            "eType",
            "fromNode",
            "toNode",
            "payLoad",
        ]


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = [
            "id",
            "name",
            "description",
            "nType",
            "parent",
            "payLoad",
        ]
