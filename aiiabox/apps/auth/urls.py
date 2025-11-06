"""
Auth URL routing for authentication endpoints.

Namespace: auth
"""

from django.urls import path

from apps.auth.views import TokenView

app_name = "auth"

urlpatterns = [
    path("token/", TokenView.as_view(), name="token"),
]
