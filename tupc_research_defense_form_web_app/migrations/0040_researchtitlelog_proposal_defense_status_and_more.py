# Generated by Django 4.0.4 on 2022-09-24 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0039_alter_user_advisee_count_alter_user_advisee_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchtitlelog',
            name='proposal_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='researchtitlelog',
            name='title_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]