# Generated by Django 5.0.4 on 2024-05-03 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0006_alter_notes_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notes',
            name='category',
            field=models.CharField(choices=[('Personal', 'Personal'), ('Work', 'Work'), ('School/Education', 'School/Education'), ('Shopping', 'Shopping'), ('Travel', 'Travel'), ('Recipes', 'Recipes'), ('Health/Fitness', 'Health/Fitness'), ('Finance', 'Finance'), ('Projects', 'Projects'), ('Ideas', 'Ideas')], default='Personal', max_length=20),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]