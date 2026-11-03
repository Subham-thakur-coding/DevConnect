from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .services.email_service import send_devconnect_email
from django.urls import reverse

from .models import DeveloperProfile, DeveloperConnection

def get_connection_between(user_a, user_b):
    """
    Find a connection request between two users,
    regardless of who sent it.
    """
    return DeveloperConnection.objects.filter(
        Q(sender=user_a, receiver=user_b)
        | Q(sender=user_b, receiver=user_a)
    ).first()


def get_connection_status(current_user, other_user):
    """
    Return the connection status from the current user's perspective.
    """

    connection = get_connection_between(current_user, other_user)

    if not connection:
        return "none"

    if connection.status == "accepted":
        return "connected"

    if connection.status == "rejected":
        return "rejected"

    if connection.status == "pending":

        if connection.sender_id == current_user.id: # type: ignore
            return "sent"

        return "received"

    return "none"

def home(request):
    """Display the public NetVibe DevConnect homepage."""
    return render(request, "community/home.html")


@login_required
def my_profile(request):
    """Display the logged-in user's developer profile."""
    profile, created = DeveloperProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "community/profile.html",
        {"profile": profile},
    )


@login_required
def edit_profile(request):
    """Allow users to edit only their own developer profile."""
    profile, created = DeveloperProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        profile.profile_picture = request.POST.get(
            "profile_picture", ""
        ).strip()

        profile.bio = request.POST.get("bio", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.skills = request.POST.get("skills", "").strip()

        profile.github_url = request.POST.get(
            "github_url", ""
        ).strip()

        profile.linkedin_url = request.POST.get(
            "linkedin_url", ""
        ).strip()

        profile.portfolio_url = request.POST.get(
            "portfolio_url", ""
        ).strip()

        profile.save()

        messages.success(request, "Your developer profile was updated!")
        return redirect("my_profile")

    return render(
        request,
        "community/edit_profile.html",
        {"profile": profile},
    )
    
def developer_directory(request):
    """Display searchable public developer profiles."""

    profiles = DeveloperProfile.objects.select_related("user").all()

    search_query = request.GET.get("q", "").strip()

    if search_query:
        profiles = profiles.filter(
            Q(user__username__icontains=search_query)
            | Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(skills__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    paginator = Paginator(profiles, 9) # type: ignore
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "community/developer_directory.html",
        {
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )


def public_profile(request, username):
    """Display a developer's public profile with connection status."""

    profile = get_object_or_404(
        DeveloperProfile.objects.select_related("user"),
        user__username=username,
    )

    connection = None
    connection_status = "none"

    # Check connection status only for authenticated users
    if request.user.is_authenticated:

        # Don't check connections when viewing your own profile
        if request.user.pk != profile.user_id: # type: ignore

            connection = get_connection_between(
                request.user,
                profile.user,
            )

            connection_status = get_connection_status(
                request.user,
                profile.user,
            )

    return render(
        request,
        "community/public_profile.html",
        {
            "profile": profile,
            "connection": connection,
            "connection_status": connection_status,
        },
    )
    




@login_required
@require_POST
def accept_connection_request(request, connection_id):

    connection = get_object_or_404(
        DeveloperConnection,
        pk=connection_id,
        receiver=request.user,
        status="pending",
    )

    sender = connection.sender
    receiver = connection.receiver

    with transaction.atomic():

        connection.status = "accepted"
        connection.save(
            update_fields=["status", "updated_at"]
        )

        # Notify the original sender after the transaction commits
        transaction.on_commit(
            lambda: send_devconnect_email(
                subject=f"{receiver.username} accepted your connection request",
                recipient=sender.email,
                template_name="connection_accepted",
                context={
                    "sender_username": sender.username,
                    "receiver_username": receiver.username,
                    "profile_url": request.build_absolute_uri(
                        reverse(
                            "public_profile",
                            kwargs={
                                "username": receiver.username,
                            },
                        )
                    ),
                },
            )
        )

    messages.success(
        request,
        f"You are now connected with {sender.username}.",
    )

    return redirect("my_connections")

@login_required
@require_POST
def send_connection_request(request, username):

    User = get_user_model()

    receiver = get_object_or_404(
        User,
        username=username,
    )

    # Prevent sending a request to yourself
    if receiver.pk == request.user.pk:
        messages.error(
            request,
            "You cannot connect with yourself."
        )
        return redirect("public_profile", username=username)

    # Check whether a connection already exists
    existing = get_connection_between(
        request.user,
        receiver,
    )

    if existing:

        if existing.status == "accepted":
            messages.info(
                request,
                "You are already connected."
            )

        elif existing.status == "pending":

            if existing.sender_id == request.user.pk: # type: ignore
                messages.info(
                    request,
                    "Your connection request is already pending."
                )
            else:
                messages.info(
                    request,
                    "This developer has already sent you a request. "
                    "Please respond to it."
                )

        else:
            messages.info(
                request,
                "A previous request exists. Please review it before "
                "sending another request."
            )

        return redirect("public_profile", username=username)

    # Create a new connection request
    try:
        with transaction.atomic():

            DeveloperConnection.objects.create(
                sender=request.user,
                receiver=receiver,
                status="pending",
            )

            # Send email after successful database commit
            transaction.on_commit(
                lambda: send_devconnect_email(
                    subject=f"{request.user.username} sent you a connection request",
                    recipient=receiver.email,
                    template_name="connection_request",
                    context={
                        "receiver_username": receiver.username,
                        "sender_username": request.user.username,
                        "profile_url": request.build_absolute_uri(
                            reverse(
                                "public_profile",
                                kwargs={
                                    "username": request.user.username,
                                },
                            )
                        ),
                    },
                )
            )

        messages.success(
            request,
            "Connection request sent successfully!"
        )

    except IntegrityError:
        messages.info(
            request,
            "A connection request already exists."
        )

    return redirect("public_profile", username=username)

@login_required
@require_POST
def accept_connection_request(request, connection_id):

    connection = get_object_or_404(
        DeveloperConnection,
        pk=connection_id,
        receiver=request.user,
        status="pending",
    )

    sender = connection.sender
    receiver = connection.receiver

    with transaction.atomic():

        connection.status = "accepted"

        connection.save(
            update_fields=["status", "updated_at"]
        )

        # Notify original sender after successful commit
        transaction.on_commit(
            lambda: send_devconnect_email(
                subject=f"{receiver.username} accepted your connection request",
                recipient=sender.email,
                template_name="connection_accepted",
                context={
                    "sender_username": sender.username,
                    "receiver_username": receiver.username,
                    "profile_url": request.build_absolute_uri(
                        reverse(
                            "public_profile",
                            kwargs={
                                "username": receiver.username,
                            },
                        )
                    ),
                },
            )
        )

    messages.success(
        request,
        f"You are now connected with {sender.username}.",
    )

    return redirect("my_connections")


@login_required
@require_POST
def reject_connection_request(request, connection_id):
    connection = get_object_or_404(
        DeveloperConnection,
        pk=connection_id,
        receiver=request.user,
        status="pending",
    )

    connection.status = "rejected"
    connection.save(update_fields=["status", "updated_at"])

    messages.info(request, "Connection request rejected.")

    return redirect("my_connections")


@login_required
@require_POST
def cancel_connection_request(request, connection_id):
    connection = get_object_or_404(
        DeveloperConnection,
        pk=connection_id,
        sender=request.user,
        status="pending",
    )

    connection.delete()

    messages.success(request, "Connection request cancelled.")

    return redirect("my_connections")


@login_required
def my_connections(request):
    incoming_requests = DeveloperConnection.objects.filter(
        receiver=request.user,
        status="pending",
    ).select_related("sender")

    sent_requests = DeveloperConnection.objects.filter(
        sender=request.user,
        status="pending",
    ).select_related("receiver")

    accepted_connections = DeveloperConnection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted",
    ).select_related("sender", "receiver")

    return render(
        request,
        "community/my_connections.html",
        {
            "incoming_requests": incoming_requests,
            "sent_requests": sent_requests,
            "accepted_connections": accepted_connections,
        },
    )
    
def features(request):
    return render(request, "community/features.html")