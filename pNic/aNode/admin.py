from django.contrib import admin

from aNode.models import NodeType
from aNode.models import Node
from aNode.models import EdgeType
from aNode.models import Edge


@admin.register(NodeType)
class NodeType(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "updStamp",
    )
    list_per_page = 50
    search_fields = ("name",)
    list_filter = ("updStamp",)


@admin.register(EdgeType)
class EdgeType(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "updStamp",
    )
    list_per_page = 50
    search_fields = ("name",)
    list_filter = ("updStamp",)


@admin.register(Edge)
class Edge(admin.ModelAdmin):
    list_display = (
        "id",
        "fromNode",
        "eType",
        "toNode",
        "description",
        "payLoad",
        "updStamp",
    )
    list_per_page = 50
    search_fields = (
        "fromNode__name",
        "toNode__name",
    )
    list_filter = (
        "updStamp",
        "eType",
    )


@admin.register(Node)
class Node(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "name",
        "nType",
        "description",
        "payLoad",
        "updStamp",
    )
    list_per_page = 50
    search_fields = ("name",)
    list_filter = (
        "updStamp",
        "nType",
    )
