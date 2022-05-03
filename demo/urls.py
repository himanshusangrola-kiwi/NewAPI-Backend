from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from apps.authentication.views import UserViewSet, ImageUploadView, LoginView, EmailVerify
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Signup API",
        default_version='v1',
        description="Welcome to Signup",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

router.register("api", UserViewSet, basename='api')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('verify-email/', EmailVerify.as_view(), name='verify-email'),
    path('upload/', ImageUploadView.as_view({'post': 'create'}), name='photo_upload'),
    path('login/', LoginView.as_view({'post': 'create'}), name='Login'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api-token-auth/', views.obtain_auth_token),
    # path('changepass/', ChangePassword.as_view({'post': 'update'}), name='change-pass')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
