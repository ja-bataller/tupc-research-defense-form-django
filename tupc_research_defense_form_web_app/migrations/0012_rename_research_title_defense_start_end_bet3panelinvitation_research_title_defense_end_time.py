# Generated by Django 4.0.4 on 2022-08-26 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0011_studentleader_request_limit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bet3panelinvitation',
            old_name='research_title_defense_start_end',
            new_name='research_title_defense_end_time',
        ),
    ]
