# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-15 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vodmanagement', '0002_auto_20170415_1627'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VideoCategoryType',
        ),
        migrations.AlterModelOptions(
            name='videocategory',
            options={'verbose_name_plural': 'Video Categorys'},
        ),
        migrations.AlterField(
            model_name='videocategory',
            name='type',
            field=models.CharField(choices=[('Common', 'Common'), ('Special', 'Special purpose')], default='Common', max_length=128),
        ),
    ]