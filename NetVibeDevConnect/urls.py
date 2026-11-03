from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from community.services.password_reset_form import DevConnectPasswordResetForm
from community import views


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Public homepage
    path("", views.home, name="home"),

    # Authentication
    path("accounts/", include("community.auth_urls")),

    # Password Reset
    path(
        "accounts/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",

            form_class=DevConnectPasswordResetForm,

            email_template_name="registration/password_reset_email.txt",

            html_email_template_name="registration/password_reset_email.html",

            subject_template_name="registration/password_reset_subject.txt",

            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),

    path(
        "accounts/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # User profiles
    path("profile/", views.my_profile, name="my_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # Developer directory
    path(
        "developers/",
        views.developer_directory,
        name="developer_directory",
    ),

    # Individual developer profile
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

    # Send connection request
    path(
        "connections/send/<str:username>/",
        views.send_connection_request,
        name="send_connection_request",
    ),

    # Accept connection request
    path(
        "connections/accept/<int:connection_id>/",
        views.accept_connection_request,
        name="accept_connection_request",
    ),

    # Reject connection request
    path(
        "connections/reject/<int:connection_id>/",
        views.reject_connection_request,
        name="reject_connection_request",
    ),

    # Cancel connection request
    path(
        "connections/cancel/<int:connection_id>/",
        views.cancel_connection_request,
        name="cancel_connection_request",
    ),

    # Developer Projects
    path("projects/", include("projects.urls")),

    # Features
    path("features/", views.features, name="features"),
]