# Generated by Django 4.0.4 on 2022-11-28 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0071_proposaldefenseform_start_tie_vote_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposaldefenseformlog',
            name='start_tie_vote',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='proposaldefenseformlog',
            name='tie_response',
            field=models.BooleanField(default=False),
        ),
    ]