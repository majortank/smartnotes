# Generated by Django 5.0.6 on 2024-05-22 11:15

import django_quill.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0003_alter_notes_shared_with"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notes",
            name="text",
            field=django_quill.fields.QuillField(),
        ),
    ]
