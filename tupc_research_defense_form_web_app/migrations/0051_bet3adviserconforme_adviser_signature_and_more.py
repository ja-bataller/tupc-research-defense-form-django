# Generated by Django 4.0.4 on 2022-11-17 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0050_remove_bet3researchtitlevote_start_voting_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet3adviserconforme',
            name='adviser_signature',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bet3adviserconforme',
            name='dit_head_signature',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bet3adviserconformelog',
            name='adviser_signature',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bet3adviserconformelog',
            name='dit_head_signature',
            field=models.BooleanField(default=False),
        ),
    ]