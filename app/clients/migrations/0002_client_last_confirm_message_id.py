# Generated by Django 3.0.7 on 2020-08-07 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='last_confirm_message_id',
            field=models.IntegerField(null=True),
        ),
    ]
