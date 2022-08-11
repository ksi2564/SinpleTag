from django.db import models


# Create your models here.

class TopCategory(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'


class Item(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '아이템'
        verbose_name_plural = '아이템'


class HeelHeight(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '굽 높이'
        verbose_name_plural = '굽 높이'


class Sole(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '밑창 모양'
        verbose_name_plural = '밑창 모양'


class Material(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '소재감'
        verbose_name_plural = '소재감'


class Printing(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '프린팅'
        verbose_name_plural = '프린팅'


class Detail(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '디테일'
        verbose_name_plural = '디테일'


class Color(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '색상'
        verbose_name_plural = '색상'
