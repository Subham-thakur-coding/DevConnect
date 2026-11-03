from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_POST


from community.services.email_service import send_devconnect_email
from .forms import ProjectForm
from .models import Project, ProjectMembership


def project_list(request):
    """
    Display public projects with search and filters.
    """

    projects = Project.objects.filter(
        visibility="public"
    ).select_related("owner").prefetch_related("memberships")

    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()
    selected_status = request.GET.get("status", "").strip()

    if query:
        projects = projects.filter(
            Q(title__icontains=query)
            | Q(tagline__icontains=query)
            | Q(description__icontains=query)
            | Q(required_skills__icontains=query)
            | Q(owner__username__icontains=query)
        )

    if selected_category:
        projects = projects.filter(category=selected_category)

    if selected_status:
        projects = projects.filter(status=selected_status)

    context = {
        "projects": projects,
        "query": query,
        "selected_category": selected_category,
        "selected_status": selected_status,
        "categories": Project.CATEGORY_CHOICES,
        "statuses": Project.STATUS_CHOICES,
        "total_projects": projects.count(),
    }

    return render(request, "projects/project_list.html", context)


@login_required
def project_create(request):
    """
    Allow authenticated developers to create projects.
    """

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            messages.success(
                request,
                "Your project has been created successfully!"
            )

            return redirect("projects:detail", slug=project.slug)

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "page_title": "Create a Project",
            "submit_label": "Publish Project",
        },
    )


def project_detail(request, slug):
    """
    Display project details.
    Unlisted projects are visible only to their owner
    and accepted members.
    """

    project = get_object_or_404(
        Project.objects.select_related("owner"),
        slug=slug,
    )

    is_owner = (
        request.user.is_authenticated
        and project.owner_id == request.user.id
    )

    membership = None

    if request.user.is_authenticated:
        membership = ProjectMembership.objects.filter(
            project=project,
            user=request.user,
        ).first()

    is_member = (
        membership is not None
        and membership.status == "accepted"
    )

    if project.visibility == "unlisted" and not (
        is_owner or is_member
    ):
        from django.http import Http404
        raise Http404("Project not found.")

    updates = project.updates.select_related("author").all()

    context = {
        "project": project,
        "membership": membership,
        "is_owner": is_owner,
        "is_member": is_member,
        "updates": updates,
    }

    return render(request, "projects/project_detail.html", context)


@login_required
def request_to_join(request, slug):
    """
    Submit a request to join a public project.
    Notify the project owner when a new request is created
    or a previously rejected request is submitted again.
    """

    if request.method != "POST":
        return redirect("projects:detail", slug=slug)

    project = get_object_or_404(
        Project.objects.select_related("owner"),
        slug=slug,
        visibility="public",
    )

    if project.owner_id == request.user.id:
        messages.warning(
            request,
            "You already own this project."
        )
        return redirect("projects:detail", slug=slug)

    if not project.looking_for_members:
        messages.warning(
            request,
            "This project is not currently accepting members."
        )
        return redirect("projects:detail", slug=slug)

    notify_owner = False

    with transaction.atomic():

        membership, created = ProjectMembership.objects.get_or_create(
            project=project,
            user=request.user,
            defaults={
                "status": "pending",
            },
        )

        if created:
            notify_owner = True

            messages.success(
                request,
                "Your request to join has been submitted!"
            )

        elif membership.status == "pending":
            messages.info(
                request,
                "You have already requested to join this project."
            )

        elif membership.status == "accepted":
            messages.info(
                request,
                "You are already a member of this project."
            )

        else:
            membership.status = "pending"
            membership.save(
                update_fields=["status", "updated_at"]
            )

            notify_owner = True

            messages.success(
                request,
                "Your join request has been submitted again."
            )

        if notify_owner:
            transaction.on_commit(
                lambda: send_devconnect_email(
                    subject=f"New join request for {project.title}",
                    recipient=project.owner.email,
                    template_name="project_join_request",
                    context={
                        "owner_username": project.owner.username,
                        "applicant_username": request.user.username,
                        "project_title": project.title,
                        "project_url": request.build_absolute_uri(
                            reverse(
                                "projects:detail",
                                kwargs={"slug": project.slug},
                            )
                        ),
                        "management_url": request.build_absolute_uri(
                            reverse("projects:mine")
                        ),
                    },
                )
            )

    return redirect("projects:detail", slug=slug)

@login_required
@require_POST
def delete_project(request, slug):
    """
    Allow only the project owner to delete their project.
    """

    project = get_object_or_404(
        Project,
        slug=slug,
        owner=request.user,
    )

    project_title = project.title
    project.delete()

    messages.success(
        request,
        f'"{project_title}" has been deleted successfully.'
    )

    return redirect("projects:mine")


@login_required
def accept_project_request(request, membership_id):
    """
    Allow only the project owner to accept a pending membership.
    Notify the applicant after successful database commit.
    """

    if request.method != "POST":
        return redirect("projects:mine")

    membership = get_object_or_404(
        ProjectMembership.objects.select_related(
            "project",
            "project__owner",
            "user",
        ),
        pk=membership_id,
        project__owner=request.user,
        status="pending",
    )

    project = membership.project
    applicant = membership.user

    with transaction.atomic():

        membership.status = "accepted"
        membership.save(
            update_fields=["status", "updated_at"]
        )

        transaction.on_commit(
            lambda: send_devconnect_email(
                subject=f"Your request to join {project.title} was accepted!",
                recipient=applicant.email,
                template_name="project_membership_accepted",
                context={
                    "applicant_username": applicant.username,
                    "project_title": project.title,
                    "owner_username": request.user.username,
                    "project_url": request.build_absolute_uri(
                        reverse(
                            "projects:detail",
                            kwargs={"slug": project.slug},
                        )
                    ),
                },
            )
        )

    messages.success(
        request,
        f"{applicant.username} has been accepted into {project.title}."
    )

    return redirect("projects:mine")

@login_required
def reject_project_request(request, membership_id):
    """
    Allow only the project owner to reject a pending membership.
    """

    if request.method != "POST":
        return redirect("projects:mine")

    membership = get_object_or_404(
        ProjectMembership.objects.select_related(
            "project",
            "user",
        ),
        pk=membership_id,
        project__owner=request.user,
        status="pending",
    )

    applicant_username = membership.user.username
    project_title = membership.project.title

    membership.status = "rejected"
    membership.save(
        update_fields=["status", "updated_at"]
    )

    messages.info(
        request,
        f"{applicant_username}'s request for {project_title} was rejected."
    )

    return redirect("projects:mine")


@login_required
def my_projects(request):
    """
    Display projects owned by the current user
    and projects they have joined.
    """

    owned_projects = Project.objects.filter(
        owner=request.user
    ).order_by("-updated_at")

    memberships = ProjectMembership.objects.filter(
        user=request.user,
        status="accepted",
    ).select_related(
        "project",
        "project__owner",
    ).order_by("-updated_at")

    pending_requests = ProjectMembership.objects.filter(
        project__owner=request.user,
        status="pending",
    ).select_related(
        "project",
        "user",
    ).order_by("-created_at")

    context = {
        "owned_projects": owned_projects,
        "memberships": memberships,
        "pending_requests": pending_requests,
    }

    return render(request, "projects/my_projects.html", context)