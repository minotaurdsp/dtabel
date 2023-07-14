from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'table', views.DynamicTableViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]