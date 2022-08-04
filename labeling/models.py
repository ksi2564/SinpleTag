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


class InitialImage(models.Model):
    image = models.ImageField(upload_to="images")
    label_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='label_user')
    inspect_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='inspect_user')
    date_save = models.DateTimeField(auto_now_add=True)

    @property
    def classificated(self):
        try:
            return self.image is not None
        except ClassificationImage.DoesNotExist:
            return False

    def __str__(self):
        return str(self.date_save)

    class Meta:
        verbose_name = '원본 이미지'
        verbose_name_plural = '원본 이미지'
        ordering = ['id']


class ClassificationImage(models.Model):
    image = models.OneToOneField(InitialImage, on_delete=models.CASCADE)
    detail_or_not = models.BooleanField(null=False)
    date_classification = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_classification)

    class Meta:
        verbose_name = '분류된 이미지'
        verbose_name_plural = '분류된 이미지'
        ordering = ['id']


class ClassificationInspectImage(models.Model):
    image = models.OneToOneField(ClassificationImage, on_delete=models.CASCADE)
    date_inspected = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_inspected)

    class Meta:
        verbose_name = '분류 검수된 이미지'
        verbose_name_plural = '분류 검수된 이미지'
