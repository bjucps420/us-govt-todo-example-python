from django.urls import path

from . import auth_views
from . import enum_views
from . import todo_views
from . import user_views

urlpatterns = [
    path('auth/get-csrf', auth_views.get_csrf, name='getcsrf'),
    path('auth/register', auth_views.register, name='register'),
    path('auth/forgot-password', auth_views.forgot_password, name='forgotpassword'),
    path('auth/login', auth_views.custom_login, name='login'),
    path('auth/logout', auth_views.custom_logout, name='logout'),
    path('enum/status/all', enum_views.all_status, name='allstatus'),
    path('enum/type/all', enum_views.all_type, name='alltype'),
    path('enum/type/all', enum_views.all_type, name='alltype'),
    path('todo/list/<status>', todo_views.todo_list, name='list'),
    path('todo/<int:id>', todo_views.by_id, name='byid'),
    path('todo/create', todo_views.create, name='create'),
    path('todo/update', todo_views.update, name='update'),
    path('todo/delete', todo_views.delete, name='delete'),
    path('user/current', user_views.current, name='current'),
    path('user/get-secret', user_views.get_secret, name='get_secret'),
    path('user/toggle-two-factor', user_views.change_two_factor, name='toggletwofactor'),
    path('user/change-email', user_views.change_email, name='changeemail'),
    path('user/change-password', user_views.change_password, name='changepassword'),
]
