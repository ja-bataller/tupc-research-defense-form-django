# Generated by Django 4.0.4 on 2022-11-10 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0046_bet3panelinvitationlog_dit_head_signature_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet3researchtitledefenseform',
            name='panel_signature',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bet3researchtitledefenseformlog',
            name='panel_signature',
            field=models.BooleanField(default=False),
        ),
    ]
