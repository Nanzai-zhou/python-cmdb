# Generated by Django 2.2.13 on 2022-02-17 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0003_auto_20220217_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(db_index=True, default='0.0.0.0')),
                ('cpu_usage', models.FloatField(default=0)),
                ('mem_usage', models.FloatField(default=0)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='host',
            name='cpu_usage',
        ),
        migrations.RemoveField(
            model_name='host',
            name='mem_usage',
        ),
    ]
