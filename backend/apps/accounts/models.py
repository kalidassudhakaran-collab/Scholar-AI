import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    avatar = models.URLField(max_length=500, blank=True)
    plan = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        default="free",
    )
    is_verified = models.BooleanField(default=False)
    daily_requests = models.IntegerField(default=0)
    monthly_requests = models.IntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.email
