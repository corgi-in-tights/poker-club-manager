from django.urls import path

from . import views

app_name = "timers"
urlpatterns = [
    path("", views.active_timers, name="active"),
    path("create/", views.create_timer, name="create"),
    path("<int:timer_id>/", views.detail_timer, name="detail"),
]

urlpatterns += [
    path(
        "_control/<int:timer_id>/",
        views.control_timer,
        name="control",
    ),
    path("_level_field/", views.level_field_partial, name="level_field"),
]
