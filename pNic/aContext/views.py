# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from aContext.serializers import ContextSerializer
from aContext.models import Context


class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer
    permission_classes = [permissions.IsAuthenticated]
