# Generated by Django 4.0.4 on 2022-12-11 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0076_remove_finaldefenseform_end_critique_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchtitle',
            name='final_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
