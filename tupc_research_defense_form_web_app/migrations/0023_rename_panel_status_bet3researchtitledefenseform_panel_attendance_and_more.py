# Generated by Django 4.0.4 on 2022-08-31 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0022_bet3researchtitledefenseform'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bet3researchtitledefenseform',
            old_name='panel_status',
            new_name='panel_attendance',
        ),
        migrations.AddField(
            model_name='bet3panelinvitation',
            name='panel_attendance',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
