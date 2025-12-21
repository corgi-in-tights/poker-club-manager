from django.urls import path

from . import views

app_name = "timers"
urlpatterns = [
    path("", views.active_timers, name="active"),
    path("new/", views.new_timer, name="new"),
    path("<int:timer_id>/", views.timer_detail, name="detail"),
]
