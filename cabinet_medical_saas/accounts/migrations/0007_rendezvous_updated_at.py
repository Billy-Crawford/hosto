# Generated by Django 5.2 on 2025-04-11 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_customuser_email_rendezvous'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendezvous',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
