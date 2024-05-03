# Generated by Django 5.0.4 on 2024-05-03 11:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0009_auto_20240503_0915'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='share_with',
            field=models.ManyToManyField(blank=True, related_name='shared_notes', to=settings.AUTH_USER_MODEL),
        ),
    ]
