from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .auth_forms import DevConnectRegistrationForm
from .services.email_service import send_devconnect_email

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = DevConnectRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Send welcome email after successful registration.
            transaction.on_commit(
                lambda: send_devconnect_email(
                    subject="Welcome to DevConnect!",
                    recipient=user.email,
                    template_name="welcome",
                    context={
                        "username": user.username,
                    },
                )
            )

            # Automatically log in the newly registered user.
            login(request, user)

            return redirect("/")

    else:
        # Initialize an empty form for GET requests.
        form = DevConnectRegistrationForm()

    return render(
        request,
        "community/auth/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = AuthenticationForm(
            request=request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
            )

            # Prevent redirects to external or untrusted websites.
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("/")

    else:
        form = AuthenticationForm(request=request)

    return render(
        request,
        "community/auth/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("/")