"""
API URL routing for authentication endpoints.

Namespace: api
"""

from django.urls import path

from apps.api.views import TokenView

app_name = "api"

urlpatterns = [
    path("auth/token/", TokenView.as_view(), name="token"),
]
