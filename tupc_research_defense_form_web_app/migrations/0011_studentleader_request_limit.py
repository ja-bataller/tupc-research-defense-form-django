# Generated by Django 4.0.4 on 2022-08-26 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0010_rename_research_title_defense_start_end_studentleader_research_title_defense_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentleader',
            name='request_limit',
            field=models.IntegerField(blank=True, default=5),
            preserve_default=False,
        ),
    ]