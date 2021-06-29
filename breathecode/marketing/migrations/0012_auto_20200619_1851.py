# Generated by Django 3.0.7 on 2020-06-19 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0011_auto_20200619_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automation',
            name='status',
            field=models.CharField(choices=[('2', 'Active'),
                                            ('1', 'Innactive'),
                                            ('0', 'Uknown')],
                                   default='0',
                                   help_text='2 = inactive, 1=active',
                                   max_length=1),
        ),
    ]
