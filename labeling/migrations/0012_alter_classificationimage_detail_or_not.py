# Generated by Django 4.0.6 on 2022-08-02 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeling', '0011_rename_detail_or_model_classificationimage_detail_or_not'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classificationimage',
            name='detail_or_not',
            field=models.BooleanField(),
        ),
    ]