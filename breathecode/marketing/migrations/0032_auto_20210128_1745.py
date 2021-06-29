# Generated by Django 3.1.4 on 2021-01-28 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0031_auto_20210123_0259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formentry',
            name='ac_academy',
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='marketing.activecampaignacademy'),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
