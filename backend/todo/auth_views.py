from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .fusion_auth_service import find_by_email, create_user, start_forgot_password
from .api import RegisterSchema, APIResponseRegisterSchema, APIResponse, APIResponseLoginSchema, LoginSchema
from ninja import Router
from ninja.security import django_auth

from todo.exceptions import TwoFactorAuthenticationCodeRequired, PasswordChangeRequired


router = Router()


@router.post("/register", response=APIResponseRegisterSchema)
def register(request, data: RegisterSchema):
    user = find_by_email(data.username)
    if user is None:
        user = create_user(data.username, data.name, data.password)
        user = User.objects.create_user(user["id"])
        if user is not None:
            login(request, user)
            return {"success": True, "response": user}
        else:
            return {"success": False, "errorMessage": "User account could not be created."}
    else:
        return {"success": False, "errorMessage": "An account already exists for this email.  Please use forgot password to reset your password."}


@router.get("/forgot-password", response=APIResponse)
def forgot_password(request, user: str = ""):
    start_forgot_password(user)
    return {"success": True}


@router.post("/login", response=APIResponseLoginSchema)
def custom_login(request, data: LoginSchema):
    data.success = False
    user = None
    try:
        user = authenticate(login=data)
    except TwoFactorAuthenticationCodeRequired:
        data.requiresTwoFactorCode = True
        data.success = True
    except PasswordChangeRequired:
        data.requiresPasswordChange = True
        data.success = True

    if user is not None:
        login(request, user)
        data.success = True

    return {"success": True, "response": data}


@router.get("/logout", response=APIResponse)
@login_required
def custom_logout(request):
    logout(request)
    return {"success": True}