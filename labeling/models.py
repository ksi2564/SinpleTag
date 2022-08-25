from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from category.models import TopCategory, Item, HeelHeight, Sole, Material, Printing, Detail, Color
from classification.models import ClassificationInspectImage


class LabelImage(models.Model):
    image = models.OneToOneField(ClassificationInspectImage, on_delete=models.CASCADE)
    top_category = models.ForeignKey(TopCategory, null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.CASCADE)
    heel_height = models.ForeignKey(HeelHeight, null=True, blank=True, on_delete=models.CASCADE)
    sole = models.ManyToManyField(Sole, null=True, blank=True, related_name="sole")
    material = models.ManyToManyField(Material, null=True, blank=True, related_name='meterial')
    printing = models.ManyToManyField(Printing, null=True, blank=True, related_name='printing')
    detail = models.ManyToManyField(Detail, null=True, blank=True, related_name='detail')
    color = models.ManyToManyField(Color, null=True, blank=True, related_name='color')
    date_labeled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.image.image.image.image).split('/')[-1]

    class Meta:
        verbose_name = '라벨링된 이미지'
        verbose_name_plural = '라벨링된 이미지'
        ordering = ['id']


class InspectImage(models.Model):
    image = models.OneToOneField(LabelImage, on_delete=models.CASCADE)
    top_category = models.ForeignKey(TopCategory, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    heel_height = models.ForeignKey(HeelHeight, on_delete=models.CASCADE)
    sole = models.ManyToManyField(Sole, related_name="inspect_sole")
    material = models.ManyToManyField(Material, related_name='inspect_meterial')
    printing = models.ManyToManyField(Printing, related_name='inspect_printing')
    detail = models.ManyToManyField(Detail, related_name='inspect_detail')
    color = models.ManyToManyField(Color, related_name='inspect_color')
    date_inspected = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.image.image.image.image.image).split('/')[-1]

    class Meta:
        verbose_name = '라벨링 검수된 이미지'
        verbose_name_plural = '라벨링 검수된 이미지'
        ordering = ['id']
