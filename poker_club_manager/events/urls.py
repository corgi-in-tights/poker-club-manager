from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.browse_events, name="browse"),
    path("<int:event_id>/", views.EventDetailView.as_view(), name="detail"),
]
