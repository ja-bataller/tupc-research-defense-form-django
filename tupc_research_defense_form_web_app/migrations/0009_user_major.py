# Generated by Django 4.0.4 on 2022-07-17 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0008_user_middle_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='major',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]