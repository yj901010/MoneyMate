from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from finlife.models import DepositProducts
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('사용자 이름(username)은 필수 항목입니다.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    profile_image = ProcessedImageField(
        blank=True,
        null=True,
        upload_to='profile_image/%Y/%m',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70},
    )
    subscribed_products = models.ManyToManyField(DepositProducts, blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    job = models.TextField(blank=True, null=True)
    birth = models.DateField(null=False, blank=False)
    phone = PhoneNumberField(region='KR', unique=True, null=False, blank=False)
    main_bank = models.TextField(blank=True, null=True)

    objects = UserManager()

    def __str__(self):
        return self.username
