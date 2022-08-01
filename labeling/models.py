from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class RequestPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=30)
    date_request = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + ' / ' + self.name


class InitialImage(models.Model):
    image = models.ImageField(upload_to="images")
    label_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='label_user')
    inspect_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='inspect_user')
    date_save = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_save)

    class Meta:
        ordering = ['id']
