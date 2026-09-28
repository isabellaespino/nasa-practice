from django.contrib import admin

from .models import ApodEntry


@admin.register(ApodEntry)
class ApodEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "media_type")
    ordering = ("-date",)
    search_fields = ("title", "explanation")
