from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from json import loads
from .fusion_auth_service import find_by_email, create_user, start_forgot_password

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from todo.exceptions import TwoFactorAuthenticationCodeRequired, PasswordChangeRequired


@never_cache
@csrf_exempt
def register(request):
    body = loads(request.body)

    user = find_by_email(body["username"])
    if user is None:
        user = create_user(body["username"], body["name"], body["password"])
        user = User.objects.create_user(user["id"])
        if user is not None:
            login(request, user)
            return JsonResponse({
                "success": True,
                "response": body
            })
        else:
            return JsonResponse({
                "success": False,
                "errorMessage": "User account could not be created."
            })
    else:
        return JsonResponse({
            "success": False,
            "errorMessage": "An account already exists for this email.  Please use forgot password to reset your password."
        })


@never_cache
@csrf_exempt
def forgot_password(request):
    user = request.GET.get('user', None)
    start_forgot_password(user)
    return JsonResponse({
        "success": True,
    })


@never_cache
@csrf_exempt
def custom_login(request):
    body = loads(request.body)

    body["success"] = False
    user = None
    try:
        user = authenticate(login=body)
    except TwoFactorAuthenticationCodeRequired:
        body["requiresTwoFactorCode"] = True
        body["success"] = True
    except PasswordChangeRequired:
        body["requiresPasswordChange"] = True
        body["success"] = True

    if user is not None:
        login(request, user)
        body["success"] = True

    return JsonResponse({
        "success": True,
        "response": body
    })


@never_cache
@csrf_exempt
@login_required
def custom_logout(request):
    logout(request)
    return JsonResponse({"success": True})