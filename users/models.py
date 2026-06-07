from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=Roles.choices, default=Roles.USER
    )
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.email} - {self.role}"
