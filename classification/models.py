from django.contrib.auth.models import User
from django.db import models


# Create your models here.
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


CHOICES_TYPE = (
    (0, '상세컷'),
    (1, '모델컷'),
    (2, '해당사항없음'),
)


class ClassificationImage(models.Model):
    image = models.OneToOneField(InitialImage, on_delete=models.CASCADE)
    image_type = models.IntegerField(null=False, choices=CHOICES_TYPE)
    date_classification = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_classification)

    class Meta:
        verbose_name = '분류 완료 이미지'
        verbose_name_plural = '분류 완료 이미지'
        ordering = ['id']


class ClassificationInspectImage(models.Model):
    image = models.OneToOneField(ClassificationImage, on_delete=models.CASCADE)
    labeling_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='labeling_user')
    label_inspect_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='label_inspect_user')
    date_inspected = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_inspected)

    class Meta:
        verbose_name = '검수 완료 이미지'
        verbose_name_plural = '검수 완료 이미지'
        ordering = ['id']
