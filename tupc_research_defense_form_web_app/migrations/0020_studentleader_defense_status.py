# Generated by Django 4.0.4 on 2022-08-17 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0019_defenseschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentleader',
            name='defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]