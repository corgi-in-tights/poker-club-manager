from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.list_events, name="list"),
    path("check-in", views.check_into_first_active, name="check_into_first_active"),
    path("<int:event_id>/", views.EventDetailView.as_view(), name="detail"),
    path("<int:event_id>/check-in", views.check_in, name="check_in"),
    path("create/", views.create_event, name="create"),
    path("<int:event_id>/manage/", views.manage_event, name="manage"),
]
