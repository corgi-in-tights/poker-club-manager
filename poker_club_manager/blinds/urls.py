from django.urls import path

from . import views

app_name = "blinds"
urlpatterns = [
    path("", views.timer, name="timer"),
]
