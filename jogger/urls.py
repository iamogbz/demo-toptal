"""
Jogger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import (
    include,
    path,
)
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from api.views import (
    auth_reset,
    auth_user,
    AccountViewSet,
    AuthViewSet,
    ScopeViewSet,
    TripViewSet,
)

ROUTER = DefaultRouter(trailing_slash=False)
ROUTES = {
    'scopes': ScopeViewSet,
    'accounts': AccountViewSet,
    'auths': AuthViewSet,
    'trips': TripViewSet,
}
for r, v in ROUTES.items():
    ROUTER.register(r, v)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(ROUTER.urls)),
    path('api/', include(
        'rest_framework.urls',
        namespace='rest_framework'
    )),
    path('api/auth/reset', auth_reset, name='auth-reset'),
    path('api/auth/user', auth_user, name='auth-user'),
]
