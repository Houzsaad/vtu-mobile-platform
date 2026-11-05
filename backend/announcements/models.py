from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    class Level(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning (service issue)"
        SUCCESS = "success", "Good news"

    title = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Optional. After this time the announcement hides itself.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @classmethod
    def current(cls):
        now = timezone.now()
        return (cls.objects.filter(is_active=True)
                .exclude(expires_at__lt=now))
    
# Create your models here.
