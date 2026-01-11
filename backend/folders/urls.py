from django.urls import path
from .views import FolderListView

urlpatterns = [
    path('', FolderListView.as_view(), name='folder-list'),
]
