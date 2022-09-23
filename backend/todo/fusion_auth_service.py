from fusionauth.fusionauth_client import FusionAuthClient
from os import getenv
from uuid import uuid4, UUID


def get_client():
    return FusionAuthClient(getenv('FUSION_AUTH_API_KEY', ''), getenv('FUSION_AUTH_SERVER', ''))


def get_roles_for_application(fusion_auth_user_id):
    response = get_client().retrieve_registration(fusion_auth_user_id, UUID(getenv('FUSION_AUTH_APPLICATION_ID', '')))
    if response.was_successful():
        return response.success_response["registration"]["roles"]
    else:
        return []


def create_user(email, name, initial_password):
    registration_request = {
        "user": {
            "id": str(uuid4()),
            "email": email,
            "fullName": name,
            "password": initial_password,
        },
        "registration": {
            "applicationId": str(UUID(getenv('FUSION_AUTH_APPLICATION_ID', ''))),
            "skipRegistrationVerification": True,
        },
        "sendSetPasswordEmail": False,
        "skipVerification": True,
    }
    response = get_client().register(registration_request, registration_request["user"]["id"])
    if response.was_successful():
        return response.success_response["user"]
    return None


def find_by_email(email):
    response = get_client().retrieve_user_by_email(email)
    if response.was_successful():
        return response.success_response["user"]
    return None


def find_by_fusion_auth_user_id(fusion_auth_user_id):
    response = get_client().retrieve_user(UUID(fusion_auth_user_id))
    if response.was_successful():
        return response.success_response["user"]
    return None


def generate_secret():
    response = get_client().generate_two_factor_secret()
    return response.success_response if response.was_successful() else None


def toggle_two_factor(fusion_auth_user_id, two_factor_dto):
    AUTHENTICATOR = "authenticator"
    user = find_by_fusion_auth_user_id(fusion_auth_user_id)
    if user is not None:
        if two_factor_dto["enableTwoFactor"]:
            request = {
                "code": two_factor_dto["code"],
                "method": AUTHENTICATOR,
                "secret": two_factor_dto["secret"],
            }
            response = get_client().enable_two_factor(user["id"], request);
            if response.was_successful():
                return response.success_response
        else:
            response = get_client().disable_two_factor(user["id"], user["twoFactor"]["methods"][0]["id"], two_factor_dto["code"]);
            return {} if response.was_successful else None
    return None


def check_password(email, password):
    request = {
        "loginId": email,
        "password": password,
    }
    response = get_client().login(request)
    if response.was_successful():
        return response.status, response.success_response
    return response.status, None


def get_user_by_login(username):
    response = get_client().retrieve_user_by_login_id(username)
    if response.was_successful():
        return response.success_response["user"]
    return None


def update_password_via_forgot(password_reset_token, password):
    user = get_client().retrieve_user_by_change_password_id(password_reset_token)
    if user.was_successful():
        return update_password(user.success_response["user"]["id"], password, False)
    return False


def update_password(fusion_auth_user_id, password, require_change):
    user = find_by_fusion_auth_user_id(fusion_auth_user_id)
    if user is not None:
        request = {"user": user}
        request["user"]["password"] = password;
        request["user"]["passwordChangeReason"] = "Administrative"
        request["user"]["passwordChangeRequired"] = require_change
        return get_client().update_user(user["id"], request).was_successful()
    return False


def complete_two_factor_login(two_factor_id, two_factor_code):
    request = {
        "twoFactorId": two_factor_id,
        "code": two_factor_code
    }
    return get_client().two_factor_login(request).was_successful()


def start_forgot_password(username):
    user = get_user_by_login(username)
    if user is not None:
        request = {
            "sendForgotPasswordEmail": True,
            "applicationId": str(UUID(getenv('FUSION_AUTH_APPLICATION_ID', ''))),
            "loginId": username
        }
        return get_client().forgot_password(request).was_successful()
    return False


def update_email(fusion_auth_user_id, email):
    user = find_by_fusion_auth_user_id(fusion_auth_user_id)
    if user is not None:
        user["email"] = email
        return get_client().update_user(user["id"], {"user": user}).was_successful()
    return False
