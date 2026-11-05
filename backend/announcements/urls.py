from django.urls import path
from .views import AnnouncementListView

urlpatterns = [
    path("", AnnouncementListView.as_view()),
]