# Generated by Django 2.2 on 2021-01-27 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_auto_20210123_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='question',
            field=models.ManyToManyField(through='survey.SurveyAnswer', to='survey.Question'),
        ),
    ]
