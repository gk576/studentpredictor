from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (
    CourseViewSet,
    PredictionRecordViewSet,
    StudentViewSet,
    health_check,
    model_stats,
    predict_view,
    register_view,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'predictions', PredictionRecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', register_view, name='register'),
    path('api/predict/', predict_view, name='predict'),
    path('api/stats/', model_stats, name='model-stats'),
    path('api/health/', health_check, name='health'),
    path('health/', health_check, name='root-health'),
]
