from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from classification.models import ClassificationInspectImage


class LabelImage(models.Model):
    image = models.OneToOneField(ClassificationInspectImage, on_delete=models.CASCADE)

