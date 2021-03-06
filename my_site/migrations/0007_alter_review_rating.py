# Generated by Django 3.2.4 on 2021-07-22 14:11

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_site', '0006_alter_review_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MinValueValidator(Decimal('0.1')), django.core.validators.MaxValueValidator(Decimal('5.0'))]),
        ),
    ]
