from django.contrib.auth.decorators import login_required
from .fusion_auth_service import find_by_fusion_auth_user_id, generate_secret, update_email, update_password, check_password, toggle_two_factor
from ninja import Router
from .api import APIUserSchema, TwoFactorSchema, EmailChangeSchema, PasswordChangeSchema, build_user, APIResponseBoolSchema, APIResponseSecretSchema


router = Router()


@router.get("current", response=APIUserSchema)
def current(request):
    if not request.user.is_anonymous:
        user = find_by_fusion_auth_user_id(request.user.username)
        if user is not None:
            return {"user": build_user(user)}
    return {"user": None}


@router.get("get-secret", response=APIResponseSecretSchema)
@login_required
def get_secret(request):
    return {"success": True, "response": generate_secret()}


@router.post("toggle-two-factor", response=APIResponseBoolSchema)
@login_required
def change_two_factor(request, data: TwoFactorSchema):
    return {"success": True, "response": toggle_two_factor(request.user.username, data)}


@router.post("change-email", response=APIResponseBoolSchema)
@login_required
def change_email(request, data: EmailChangeSchema):
    return {"success": True, "response": update_email(request.user.username, data.newEmail)}


@router.post("change-password", response=APIResponseBoolSchema)
@login_required
def change_password(request, data: PasswordChangeSchema):
    user = find_by_fusion_auth_user_id(request.user.username)
    if check_password(user["email"], data.currentPassword)[0] < 300:
        return {"success": True, "response": update_password(request.user.username, data.newPassword, False)}
    else:
        return {"success": True, "errorMessage": "Current password is incorrect."}
