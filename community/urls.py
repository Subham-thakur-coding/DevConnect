
from django.contrib import admin
from django.urls import path, include

from community import views


urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Public homepage
    path("", views.home, name="home"),

    # Authentication
    path("accounts/", include("community.auth_urls")),

    # Developer profiles
    path("profile/", views.my_profile, name="my_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # Developer directory
    path(
        "developers/",
        views.developer_directory,
        name="developer_directory",
    ),

    # Individual public developer profile
    path(
        "developers/<str:username>/",
        views.public_profile,
        name="public_profile",
    ),

    # Developer connections page
    path(
        "connections/",
        views.my_connections,
        name="my_connections",
    ),

    # Send a connection request
    path(
        "connections/send/<str:username>/",
        views.send_connection_request,
        name="send_connection_request",
    ),

    # Accept a connection request
    path(
        "connections/accept/<int:connection_id>/",
        views.accept_connection_request,
        name="accept_connection_request",
    ),

    # Reject a connection request
    path(
        "connections/reject/<int:connection_id>/",
        views.reject_connection_request,
        name="reject_connection_request",
    ),

    # Cancel a sent connection request
    path(
        "connections/cancel/<int:connection_id>/",
        views.cancel_connection_request,
        name="cancel_connection_request",
    ),
]
