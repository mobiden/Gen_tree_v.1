# Generated by Django 3.2.5 on 2022-11-28 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtree_db', '0021_alter_person_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='sex',
            field=models.CharField(blank=True, choices=[('F', 'Женский'), ('M', 'Мужской'), ('', '')], max_length=1, null=True, verbose_name='Пол'),
        ),
    ]
