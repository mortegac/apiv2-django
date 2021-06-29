# Generated by Django 3.2 on 2021-04-30 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0033_auto_20210302_0102'),
    ]

    operations = [
        migrations.AddField(
            model_name='formentry',
            name='ac_contact_id',
            field=models.CharField(blank=True,
                                   default=None,
                                   help_text='Active Campaign Contact ID',
                                   max_length=20,
                                   null=True),
        ),
        migrations.AddField(
            model_name='formentry',
            name='ac_deal_id',
            field=models.CharField(blank=True,
                                   default=None,
                                   help_text='Active Campaign Deal ID',
                                   max_length=20,
                                   null=True),
        ),
        migrations.CreateModel(
            name='ActiveCampaignWebhook',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('webhook_type',
                 models.CharField(blank=True,
                                  default=None,
                                  max_length=100,
                                  null=True)),
                ('run_at',
                 models.DateTimeField(
                     help_text='Date/time that the webhook ran')),
                ('initiated_by',
                 models.CharField(
                     help_text=
                     'Source/section of the software that triggered the webhook to run',
                     max_length=100)),
                ('payload',
                 models.JSONField(
                     help_text=
                     'Extra info that came on the request, it varies depending on the webhook type'
                 )),
                ('status',
                 models.CharField(choices=[('PENDING', 'Pending'),
                                           ('DONE', 'Done'),
                                           ('ERROR', 'Error')],
                                  default='PENDING',
                                  max_length=9)),
                ('status_text',
                 models.CharField(blank=True,
                                  default=None,
                                  max_length=255,
                                  null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ac_academy',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='marketing.activecampaignacademy')),
                ('contact',
                 models.ForeignKey(blank=True,
                                   default=None,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='marketing.contact')),
                ('form_entry',
                 models.ForeignKey(blank=True,
                                   default=None,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='marketing.formentry')),
            ],
        ),
    ]
