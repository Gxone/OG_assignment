# Generated by Django 2.2 on 2021-01-27 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_user_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveytype',
            name='name',
            field=models.CharField(max_length=45),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=45),
        ),
    ]