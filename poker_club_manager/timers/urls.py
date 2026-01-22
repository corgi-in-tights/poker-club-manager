from django.urls import path

from . import views

app_name = "timers"
urlpatterns = [
    path("", views.active_timers, name="active"),
    path("create/", views.create_timer, name="create"),
    path("<int:timer_id>/", views.detail_timer, name="detail"),
    path("<int:timer_id>/stream/", views.stream, name="stream"),
]

urlpatterns += [
    path(
        "_control/<int:timer_id>/",
        views.timer_control,
        name="control",
    ),
]
