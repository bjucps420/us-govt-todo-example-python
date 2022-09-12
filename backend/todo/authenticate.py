from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from .fusion_auth_service import check_password, update_password_via_forgot, get_user_by_login, complete_two_factor_login, update_password, get_roles_for_application
from todo.exceptions import TwoFactorAuthenticationCodeRequired, PasswordChangeRequired

PASSWORD_CHANGE_REQUIRED = 203
TWO_FACTOR_CODE_REQUIRED = 242


class FusionAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, login=None):
        response = check_password(login["username"], login["password"])

        user = None
        if response is None:
            return None
        else:
            user = response[1]

        if "forgotPasswordCode" in login and login["forgotPasswordCode"] is not None:
            if update_password_via_forgot(login["forgotPasswordCode"], login["newPassword"]):
                user = get_user_by_login(login["username"])
            else:
                return None
        elif response[1] is None:
            return None
        elif "twoFactorCode" in login and response[0] == TWO_FACTOR_CODE_REQUIRED and login["twoFactorCode"] is None:
            raise TwoFactorAuthenticationCodeRequired()
        elif "twoFactorCode" in login and response[0] == TWO_FACTOR_CODE_REQUIRED:
            if not complete_two_factor_login(user["twoFactorId"], login["twoFactorCode"]):
                return None
            user = get_user_by_login(login["username"])
        elif "newPassword" in login and response[0] == PASSWORD_CHANGE_REQUIRED and login["newPassword"] is None:
            raise PasswordChangeRequired()
        elif "newPassword" in login and response[0] == PASSWORD_CHANGE_REQUIRED:
            user = get_user_by_login(login["username"])
            update_password(user["id"], login["newPassword"], False)
        try:
            return User.objects.get(username=user["id"])
        except User.DoesNotExist:
            User.objects.create_user(user["id"])
            return User.objects.get(username=user["id"])

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def has_perm(self, user_obj, perm, obj=None):
        return perm in get_roles_for_application(user_obj.username)