from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import BlogPost

class BlogPostListView(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = "blog/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by("-created_at")


class BlogPostDetailView(LoginRequiredMixin, DetailView):
    model = BlogPost
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)

        post.refresh_from_db(fields=["views_count"])
        return post

class BlogPostManageListView(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = "blog/manage/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return BlogPost.objects.all().order_by("-created_at")


class BlogPostManageDetailView(LoginRequiredMixin, DetailView):
    model = BlogPost
    template_name = "blog/manage/post_detail.html"
    context_object_name = "post"


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    template_name = "blog/manage/post_form.html"
    fields = ["title", "content", "preview", "is_published",]

    success_url = reverse_lazy("blog:manage_list")


class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    template_name = "blog/manage/post_form.html"
    fields = ["title", "content", "preview", "is_published",]

    def get_success_url(self):
        return reverse("blog:manage_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = "blog/manage/post_confirm_delete.html"
    success_url = reverse_lazy("blog:manage_list")
