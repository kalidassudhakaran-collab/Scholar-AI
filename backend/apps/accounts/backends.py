from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Allow Django admin login with email (default) or username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        login = username or kwargs.get(UserModel.USERNAME_FIELD)
        if not login or password is None:
            return None

        user = None
        if "@" in login:
            try:
                user = UserModel.objects.get(email__iexact=login)
            except UserModel.DoesNotExist:
                return None
        else:
            try:
                user = UserModel.objects.get(username__iexact=login)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
