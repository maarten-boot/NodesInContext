"""pNic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import (
    include,
    path,
    re_path,
)

from rest_framework import routers

from aNode import views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()

router.register(r"api/aNode/NodeType", views.NodeTypeViewSet)
router.register(r"api/aNode/EdgeType", views.EdgeTypeViewSet)
router.register(r"api/aNode/Node", views.NodeViewSet)
router.register(r"api/aNode/Edge", views.EdgeViewSet)

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", include("aMain.urls")),
    #
    re_path(r"^api/aNode/NodeType/$", views.NodeTypeAPIView.as_view(), name="nodetype_list"),
    path("api/aNode/NodeType/name=<str:name>", views.NodeTypeAPIView.as_view()),
    path("api/aNode/NodeType/", views.NodeTypeAPIView.as_view()),
    path("api/aNode/EdgeType/", views.EdgeTypeAPIView.as_view()),
    path("api/aNode/Node/", views.NodeAPIView.as_view()),
    path("api/aNode/Edge/", views.EdgeAPIView.as_view()),
    #
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
