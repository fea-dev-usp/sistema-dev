# Generated by Django 5.0.1 on 2024-01-22 01:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemadev', '0005_alter_area_nome'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='diretor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diretor_area', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='grupo',
            name='lider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lider_grupo', to=settings.AUTH_USER_MODEL),
        ),
    ]
