from django.db import models


class ApodEntry(models.Model):
    IMAGE = "image"
    VIDEO = "video"
    MEDIA_TYPE_CHOICES = [
        (IMAGE, "Image"),
        (VIDEO, "Video"),
    ]

    date = models.DateField(unique=True)
    title = models.CharField(max_length=255)
    explanation = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    url = models.URLField()
    hdurl = models.URLField(blank=True, null=True)
    copyright = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "APOD entries"

    def __str__(self):
        return f"{self.date} - {self.title}"
