# Generated by Django 2.2 on 2021-01-23 07:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20210122_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(11, '숫자 11개를 입력해주세요')]),
        ),
    ]
