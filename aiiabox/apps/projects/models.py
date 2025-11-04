from django.db import models


class Project(models.Model):
    """
    Stub Project model for Phase 1.

    Full implementation will be in Phase 4 (Projects & Organization).
    For now, this model exists to support the ForeignKey reference
    in UserSettings.default_project.
    """

    name = models.CharField(max_length=255)

    def __str__(self):  # pragma: no cover
        return self.name
