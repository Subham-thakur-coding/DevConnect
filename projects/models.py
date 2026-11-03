from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class Project(models.Model):

    CATEGORY_CHOICES = [
        ("web", "Web Development"),
        ("mobile", "Mobile Development"),
        ("ai", "AI / Machine Learning"),
        ("data", "Data Science"),
        ("software", "Software Development"),
        ("game", "Game Development"),
        ("open_source", "Open Source"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("idea", "Idea"),
        ("building", "In Development"),
        ("launched", "Launched"),
        ("paused", "Paused"),
    ]

    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("unlisted", "Unlisted"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )

    title = models.CharField(max_length=150)

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
    )

    tagline = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
    )

    required_skills = models.CharField(
        max_length=500,
        blank=True,
        help_text="Enter skills separated by commas.",
    )

    repository_url = models.URLField(blank=True)

    demo_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="idea",
    )

    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
    )

    looking_for_members = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["category"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.title) or "project"
            candidate = base_slug
            counter = 1

            while Project.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base_slug}-{counter}"

            self.slug = candidate

        super().save(*args, **kwargs)

    @property
    def skill_list(self):
        return [
            skill.strip()
            for skill in self.required_skills.split(",")
            if skill.strip()
        ]

    @property
    def accepted_member_count(self):
        return self.memberships.filter(status="accepted").count() # type: ignore

    def __str__(self):
        return self.title


class ProjectMembership(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    message = models.TextField(
        max_length=500,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_membership",
            ),
        ]

        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.status})"


class ProjectUpdate(models.Model):

    UPDATE_TYPES = [
        ("update", "Progress Update"),
        ("milestone", "Milestone"),
        ("announcement", "Announcement"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="updates",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_updates",
    )

    title = models.CharField(max_length=150)

    content = models.TextField(max_length=3000)

    update_type = models.CharField(
        max_length=15,
        choices=UPDATE_TYPES,
        default="update",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.title} - {self.title}"