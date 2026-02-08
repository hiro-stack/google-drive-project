from django.urls import path
from .views import FolderListView, CacheRefreshView

urlpatterns = [
    path('', FolderListView.as_view(), name='folder-list'),
    path('cache/refresh/', CacheRefreshView.as_view(), name='cache-refresh'),
]
