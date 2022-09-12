from .fusion_auth_service import get_roles_for_application

class UserDto:
    def __init__(self, user):
        if "firstName" in user and "lastName" in user:
            self.name = user["firstName"] + " " + user["lastName"]
        elif "fullName" in user:
            self.name = user["fullName"]
        if "username" in user:
            self.username = user["username"]
        else:
            self.username = None
        self.email = user["email"]
        self.fusionAuthUserId = user["id"]
        self.roles = get_roles_for_application(user["id"])
        self.authenticated = True
        if len(user["twoFactor"]["methods"]) > 0:
            self.twoFactorEnabled = True
        else:
            self.twoFactorEnabled = False
