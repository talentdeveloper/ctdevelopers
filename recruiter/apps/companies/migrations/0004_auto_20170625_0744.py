# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-25 06:44
from __future__ import unicode_literals
import itertools
from django.db import migrations, models
from django.utils.text import slugify


def generate_unique_slug(apps, schema_editor):
    """
        Populates new relationship from old one.
    """
    Company = apps.get_model('companies', 'Company')

    for company in Company.objects.all():
        company.slug = slug_copy = slugify(company.name)
        for i in itertools.count(1):
            if not Company.objects.filter(slug=company.slug).exists():
                break
            company.slug = '{}-{}'.format(slug_copy, i)
        company.save()


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20170524_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='alias',
        ),
        migrations.AddField(
            model_name='company',
            name='slug',
            field=models.SlugField(default=1, max_length=120, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.RunPython(generate_unique_slug)
    ]
