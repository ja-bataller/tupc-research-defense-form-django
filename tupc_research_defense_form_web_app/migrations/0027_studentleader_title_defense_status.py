# Generated by Django 4.0.4 on 2022-09-03 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0026_bet3panelinvitation_subject_teacher_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentleader',
            name='title_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
