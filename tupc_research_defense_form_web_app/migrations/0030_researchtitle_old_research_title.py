# Generated by Django 4.0.4 on 2022-09-06 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0029_bet3panelinvitation_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchtitle',
            name='old_research_title',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]