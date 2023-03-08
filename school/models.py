from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class SchoolManager(BaseUserManager):

    def create_user(self, email, name, city, pin_code, password=None):
        if not email:
            raise ValueError('School must have an email address')
        if not name:
            raise ValueError('School must have a name')
        if not city:
            raise ValueError('School must have a city')
        if not pin_code:
            raise ValueError('School must have a pin code')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            city=city,
            pin_code=pin_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, city, pin_code, password):

        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            city=city,
            pin_code=pin_code,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class School(AbstractBaseUser):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=10)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'city', 'pin_code']

    objects = SchoolManager()

    def __str__(self):
        return self.name

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
