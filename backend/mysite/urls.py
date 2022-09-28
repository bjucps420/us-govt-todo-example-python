"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
import time

from django.contrib import admin
from django.urls import path
from django.utils.http import http_date

from ninja import NinjaAPI

from todo.auth_views import router as auth_router
from todo.enum_views import router as enum_router
from todo.todo_views import router as todo_router
from todo.user_views import router as user_router


class MyApi(NinjaAPI):
    def create_temporal_response(self, request):
        response = super().create_temporal_response(request)
        response.headers["Expires"] = http_date(time.time() + 1)
        return response


api = MyApi()

api.add_router("/auth/", auth_router)
api.add_router("/enum/", enum_router)
api.add_router("/todo/", todo_router)
api.add_router("/user/", user_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
