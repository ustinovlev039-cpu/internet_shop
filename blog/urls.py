from django.urls import path

from blog import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="post_list"),
    path("<int:pk>/", views.BlogPostDetailView.as_view(), name="post_detail"),
    path("manage/", views.BlogPostManageListView.as_view(), name="manage_list"),
    path("manage/create/", views.BlogPostCreateView.as_view(), name="manage_create"),
    path("manage/<int:pk>/", views.BlogPostManageDetailView.as_view(), name="manage_detail"),
    path("manage/<int:pk>/edit/", views.BlogPostUpdateView.as_view(), name="manage_update"),
    path("manage/<int:pk>/delete/", views.BlogPostDeleteView.as_view(), name="manage_delete")
]