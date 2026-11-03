from django.urls import path

from . import views


app_name = "projects"


urlpatterns = [
    path("", views.project_list, name="list"),
    path("create/", views.project_create, name="create"),
    path("mine/", views.my_projects, name="mine"),

    path(
        "membership/<int:membership_id>/accept/",
        views.accept_project_request,
        name="accept_request",
    ),

    path(
        "membership/<int:membership_id>/reject/",
        views.reject_project_request,
        name="reject_request",
    ),

    path(
        "<slug:slug>/join/",
        views.request_to_join,
        name="join",
    ),

    path(
        "<slug:slug>/delete/",
        views.delete_project,
        name="delete",
    ),

    path(
        "<slug:slug>/",
        views.project_detail,
        name="detail",
    ),
]