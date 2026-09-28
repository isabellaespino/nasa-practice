from django.urls import path

from . import views

app_name = "apod"

urlpatterns = [
    path("", views.home, name="home"),
    path("archive/", views.archive_form, name="archive_form"),
    path("date/<str:entry_date>/", views.detail, name="detail"),
]
