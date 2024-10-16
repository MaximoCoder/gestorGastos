# Generated by Django 5.0.6 on 2024-07-13 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestor', '0005_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='management',
            name='disponible',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='management',
            name='fecha_fin',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='management',
            name='gastado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, null=True),
        ),
    ]
