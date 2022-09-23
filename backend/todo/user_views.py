from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from .fusion_auth_service import find_by_fusion_auth_user_id, generate_secret, update_email, update_password, check_password, toggle_two_factor
from json import loads

from todo.dtos import UserDto


@never_cache
@csrf_exempt
def current(request):
    if not request.user.is_anonymous:
        user = find_by_fusion_auth_user_id(request.user.username)
        if user is not None:
            return JsonResponse({"user": UserDto(user).__dict__})
    return JsonResponse(None, safe=False)


@never_cache
@csrf_exempt
@login_required
def get_secret(request):
    return JsonResponse({
        "success": True,
        "response": generate_secret()
    })


@never_cache
@csrf_exempt
@login_required
def change_two_factor(request):
    body = loads(request.body)
    return JsonResponse({
        "success": True,
        "response": toggle_two_factor(request.user.username, body)
    })


@never_cache
@csrf_exempt
@login_required
def change_email(request):
    body = loads(request.body)
    return JsonResponse({
        "success": True,
        "response": update_email(request.user.username, body["newEmail"])
    })


@never_cache
@csrf_exempt
@login_required
def change_password(request):
    body = loads(request.body)
    user = find_by_fusion_auth_user_id(request.user.username)
    if check_password(user["email"], body["currentPassword"])[0] < 300:
        return JsonResponse({
            "success": True,
            "response": update_password(request.user.username, body["newPassword"], False)
        })
    else:
        return JsonResponse({
            "success": False,
            "errorMessage": "Current password is incorrect."
        })