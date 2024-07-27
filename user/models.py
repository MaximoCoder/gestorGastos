from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    auth_code = models.CharField(max_length=5, null=True, blank=True)
    image_user = models.ImageField(upload_to='users/', null=True, blank=True)