# Generated by Django 3.2.4 on 2021-08-04 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_site', '0007_alter_review_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='style',
            new_name='school',
        ),
    ]