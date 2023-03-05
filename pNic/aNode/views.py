from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics

# from rest_framework import filters

from aNode.models import EdgeType
from aNode.models import NodeType
from aNode.models import Edge
from aNode.models import Node

from aNode.serializers import EdgeTypeSerializer
from aNode.serializers import NodeSerializer
from aNode.serializers import NodeTypeSerializer
from aNode.serializers import EdgeSerializer

from django_filters.rest_framework import DjangoFilterBackend
import django_filters


class NodeTypeViewSet(viewsets.ModelViewSet):
    queryset = NodeType.objects.all()
    serializer_class = NodeTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class NodeTypeAPIView(generics.ListCreateAPIView):
    # search_fields = ["name"]
    # filter_backends = (filters.SearchFilter,)
    filter_backends = [DjangoFilterBackend]
    queryset = NodeType.objects.all()
    serializer_class = NodeTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [
        "name",
    ]


class EdgeTypeViewSet(viewsets.ModelViewSet):
    queryset = EdgeType.objects.all()
    serializer_class = EdgeTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeTypeAPIView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    queryset = EdgeType.objects.all()
    serializer_class = EdgeTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [
        "name",
    ]


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class EdgeAPIView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = [
        "fromNode",
        "toNode",
        "eType",
    ]


class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class NodeFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr="iexact")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Node
        fields = [
            "name",
            "nType",
            "parent",
        ]


class NodeAPIView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = NodeFilter
    #    filterset_fields = [
    #        "name",
    #        "nType",
    #        "parent",
    #    ]
