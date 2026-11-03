from django.conf import settings
from django.db import models
from django.core.validators import URLValidator
from django.db.models import Q

class DeveloperProfile(models.Model):
    """Additional profile information for a DevConnect user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="developer_profile",
    )

    profile_picture = models.URLField(
        blank=True,
        help_text="Optional URL for your profile picture.",
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell the community about yourself.",
    )

    location = models.CharField(
        max_length=100,
        blank=True,
    )

    skills = models.CharField(
        max_length=300,
        blank=True,
        help_text="Example: Python, Django, HTML, CSS, JavaScript",
    )

    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Developer Profile"
        verbose_name_plural = "Developer Profiles"

    def __str__(self):
        return f"{self.user.username}'s Developer Profile"
    
    def get_skills_list(self):
        return [
            skill.strip()
            for skill in self.skills.split(",")
            if skill.strip()
        ]
        
        
class DeveloperConnection(models.Model):
    """
    Stores a connection request between two developers.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_connection_requests",
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_connection_requests",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_directed_connection",
            ),
            models.CheckConstraint(
                condition=~Q(sender=models.F("receiver")),
                name="prevent_self_connection",
            ),
        ]

    def __str__(self):
        return (
            f"{self.sender.username} -> "
            f"{self.receiver.username} "
            f"({self.status})"
        )