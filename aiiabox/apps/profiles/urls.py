from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/", views.ProfileDetailView.as_view(), name="profile_detail"),
]
