from ninja import Schema
from ninja.orm import create_schema
from typing import List
from .fusion_auth_service import get_roles_for_application
from .models import APIResponse


def build_user(user):
    result = {}
    if "firstName" in user and "lastName" in user:
        result["name"] = user["firstName"] + " " + user["lastName"]
    elif "fullName" in user:
        result["name"] = user["fullName"]
    if "username" in user:
        result["username"] = user["username"]
    else:
        result["username"] = None
    result["email"] = user["email"]
    result["fusionAuthUserId"] = user["id"]
    result["roles"] = get_roles_for_application(user["id"])
    result["authenticated"] = True
    if len(user["twoFactor"]["methods"]) > 0:
        result["twoFactorEnabled"] = True
    else:
        result["twoFactorEnabled"] = False
    return result


class RegisterSchema(Schema):
    name: str = None
    username: str = None
    password: str = None


class LoginSchema(Schema):
    username: str = None
    password: str = None
    newPassword: str = None
    twoFactorCode: str = None
    forgotPasswordCode: str = None
    success: bool = None
    requiresPasswordChange: bool = None
    requiresTwoFactorCode: bool = None


class UserSchema(Schema):
    name: str = None
    username: str = None
    email: str = None
    fusionAuthUserId: str = None
    roles: list = None
    authenticated: bool = None
    twoFactorEnabled: bool = None


class APIUserSchema(Schema):
    user: UserSchema = None


class SecretSchema(Schema):
    secret: str = None
    secretBase32Encoded: str = None


class TwoFactorSchema(Schema):
    secret: str = None
    code: str = None
    secretBase32: str = None
    enableTwoFactor: bool = None


class EmailChangeSchema(Schema):
    newEmail: str = None


class PasswordChangeSchema(Schema):
    currentPassword: str = None
    newPassword: str = None


class TodoSchema(Schema):
    id: int = None
    title: str = None
    description: str = None
    status: str = None
    type: str = None
    created_by: str = None
    updated_by: str = None


class TodoListSchema(Schema):
    total: int = None
    items: List[TodoSchema] = None


APIResponseTodoListSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", TodoListSchema, None)])
APIResponseTodoSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", TodoSchema, None)])
APIResponseBoolSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", bool, None)])
APIResponseSecretSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", SecretSchema, None)])
APIResponseRegisterSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", RegisterSchema, None)])
APIResponseLoginSchema = create_schema(APIResponse, name="APIResponseRegisterSchema", exclude=["id"], custom_fields=[("response", LoginSchema, None)])
