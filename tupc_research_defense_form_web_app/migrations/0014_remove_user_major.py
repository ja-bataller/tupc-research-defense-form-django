# Generated by Django 4.0.4 on 2022-07-26 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0013_user_honorific'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='major',
        ),
    ]