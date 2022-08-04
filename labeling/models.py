from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class RequestPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=30)
    date_request = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + ' / ' + self.name
    
    class Meta:
        verbose_name = '전문가 권한 요청'
        verbose_name_plural = '전문가 권한 요청'


