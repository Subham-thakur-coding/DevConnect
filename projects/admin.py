from django.contrib import admin
from .models import Project, ProjectMembership, ProjectUpdate


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    readonly_fields = ("created_at", "updated_at")


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "category",
        "status",
        "visibility",
        "looking_for_members",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "visibility",
        "looking_for_members",
    )

    search_fields = (
        "title",
        "tagline",
        "description",
        "owner__username",
    )

    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    inlines = [
        ProjectMembershipInline,
        ProjectUpdateInline,
    ]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "user",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "project__title",
        "user__username",
    )

    readonly_fields = ("created_at", "updated_at")


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "author",
        "update_type",
        "created_at",
    )

    list_filter = ("update_type", "created_at")

    search_fields = (
        "title",
        "content",
        "project__title",
        "author__username",
    )

    readonly_fields = ("created_at",)