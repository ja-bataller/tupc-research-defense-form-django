# Generated by Django 4.0.4 on 2022-11-21 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0053_rename_research_title_defense_date_bet3proposaldefensepanelinvitation_research_proposal_defense_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='BET3ResearchProposalDefenseForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('course_major_abbr', models.CharField(blank=True, max_length=256)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_attendance', models.CharField(max_length=256)),
                ('is_panel_chairman', models.BooleanField(default=False)),
                ('panel_chairman_signature_response', models.BooleanField(default=False)),
                ('panel_chairman_signature_attach', models.BooleanField(default=False)),
                ('form_date', models.CharField(max_length=256)),
                ('start_comment', models.BooleanField(default=False)),
                ('start_voting', models.BooleanField(default=False)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('defense_date', models.CharField(blank=True, max_length=256)),
                ('defense_start_time', models.CharField(blank=True, max_length=256)),
                ('defense_end_time', models.CharField(blank=True, max_length=256)),
            ],
        ),
    ]
