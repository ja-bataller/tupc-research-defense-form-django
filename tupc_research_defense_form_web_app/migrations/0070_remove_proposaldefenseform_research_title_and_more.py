# Generated by Django 4.0.4 on 2022-11-28 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0069_proposaldefenseform_research_title_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposaldefenseform',
            name='research_title',
        ),
        migrations.AddField(
            model_name='proposaldefensecritique',
            name='research_title',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
