from django.urls import path

from . import views

app_name = "chats"

urlpatterns = [
    path("", views.ChatListView.as_view(), name="chat_list"),
    path("<int:pk>/", views.ChatDetailView.as_view(), name="chat_detail"),
    path("create/", views.ChatCreateView.as_view(), name="chat_create"),
    path("<int:pk>/delete/", views.ChatDeleteView.as_view(), name="chat_delete"),
]
