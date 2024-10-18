from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as OriginalGroup, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

username_validator = UnicodeUsernameValidator()

# Register your models here


class UserManager(BaseUserManager):
    """
    Model manager for our custom User object, which uses email
    addresses instead of usernames.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email address must be provided.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):  # type: ignore
    """
    A custom user model, which uses email instead of username as
    the identifier.
    """

    username = models.CharField(
        _("username"),
        max_length=150,
        primary_key=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    objects = UserManager()  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        OriginalGroup,
        verbose_name=_('groups'),
        blank=True,
        related_name='user_set',  # TODO: Add a related_name here
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='user_set',  # TODO: Add a related_name here
        related_query_name='user',
    )

    def __str__(self):
        return str(self.username or self.email)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super(User, self).save(*args, **kwargs)

    def clean(self):
        # Si el username no está vacío o nulo, se verifica si ya existe
        if self.username and User.objects.exclude(pk=self.pk).filter(username=self.username).exists():
            raise ValidationError({"username": _("A user with that username already exists.")})

        # Llamar a la validación original de clean para otras validaciones
        super().clean()


class Group(OriginalGroup):
    class Meta:
        proxy = True
        verbose_name = _("group")
        verbose_name_plural = _("groups")
