from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "is_active", "expires_at", "created_at")
    list_filter = ("level", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title", "message")
    
# Register your models here.
