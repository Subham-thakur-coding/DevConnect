from django import forms

from .models import Project, ProjectUpdate


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project

        fields = [
            "title",
            "tagline",
            "description",
            "category",
            "required_skills",
            "repository_url",
            "demo_url",
            "status",
            "visibility",
            "looking_for_members",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: AI-powered Developer Platform",
                "maxlength": 150,
            }),

            "tagline": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "A short introduction to your project",
                "maxlength": 200,
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Explain your project, its purpose and features...",
            }),

            "category": forms.Select(attrs={
                "class": "form-select",
            }),

            "required_skills": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Python, Django, HTML, CSS, JavaScript",
            }),

            "repository_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://github.com/username/repository",
            }),

            "demo_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://your-live-project.com",
            }),

            "status": forms.Select(attrs={
                "class": "form-select",
            }),

            "visibility": forms.Select(attrs={
                "class": "form-select",
            }),

            "looking_for_members": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "title": "Project Name",
            "tagline": "Short Tagline",
            "description": "Project Description",
            "category": "Project Category",
            "required_skills": "Required Skills",
            "repository_url": "GitHub Repository",
            "demo_url": "Live Demo",
            "status": "Development Status",
            "visibility": "Project Visibility",
            "looking_for_members": "Looking for Team Members",
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if len(title) < 3:
            raise forms.ValidationError(
                "Project name must contain at least 3 characters."
            )

        return title

    def clean_description(self):
        description = self.cleaned_data["description"].strip()

        if len(description) < 30:
            raise forms.ValidationError(
                "Please provide a description of at least 30 characters."
            )

        return description


class ProjectUpdateForm(forms.ModelForm):

    class Meta:
        model = ProjectUpdate

        fields = [
            "title",
            "content",
            "update_type",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Update title",
                "maxlength": 150,
            }),

            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Share your project progress...",
            }),

            "update_type": forms.Select(attrs={
                "class": "form-select",
            }),
        }

        labels = {
            "title": "Update Title",
            "content": "What's happening with your project?",
            "update_type": "Update Type",
        }