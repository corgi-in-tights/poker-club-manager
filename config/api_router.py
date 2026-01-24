from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from poker_club_manager.events.api.urls import router as events_router
from poker_club_manager.timers.api.views import TimerViewSet
from poker_club_manager.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet, basename="user")
router.register("timers", TimerViewSet, basename="timer")

app_name = "api"
urlpatterns = router.urls + events_router.urls
