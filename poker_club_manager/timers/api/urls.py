from rest_framework import routers

router = routers.SimpleRouter()
router.register(r""
router.register(r'accounts', AccountViewSet)
urlpatterns = router.urls
