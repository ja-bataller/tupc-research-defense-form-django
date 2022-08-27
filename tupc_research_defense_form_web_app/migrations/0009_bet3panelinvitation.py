# Generated by Django 4.0.4 on 2022-08-26 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0008_studentleader_research_title_defense_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BET3PanelInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('dit_head_username', models.CharField(max_length=256)),
                ('dit_head_full_name', models.CharField(max_length=256)),
                ('dit_head_response', models.CharField(max_length=256)),
                ('dit_head_response_date', models.CharField(max_length=256)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_response', models.CharField(max_length=256)),
                ('panel_response_date', models.CharField(max_length=256)),
                ('research_title_defense_date', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_start_time', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_start_end', models.CharField(blank=True, max_length=256)),
                ('form_date_sent', models.CharField(max_length=256)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
            ],
        ),
    ]
