# Generated by Django 5.0.6 on 2024-05-18 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='content',
            field=models.TextField(default=0),
        ),
    ]
