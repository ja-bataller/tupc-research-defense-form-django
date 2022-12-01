# Generated by Django 4.0.4 on 2022-11-18 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0051_bet3adviserconforme_adviser_signature_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BET3ProposalDefensePanelInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('course_major_abbr', models.CharField(blank=True, max_length=256)),
                ('dit_head_username', models.CharField(max_length=256)),
                ('dit_head_full_name', models.CharField(max_length=256)),
                ('dit_head_response', models.CharField(max_length=256)),
                ('dit_head_response_date', models.CharField(max_length=256)),
                ('dit_head_signature', models.BooleanField(default=False)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_response', models.CharField(max_length=256)),
                ('panel_response_date', models.CharField(max_length=256)),
                ('panel_signature', models.BooleanField(default=False)),
                ('panel_attendance', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_date', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_start_time', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_end_time', models.CharField(blank=True, max_length=256)),
                ('form_date_sent', models.CharField(max_length=256)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BET3ProposalDefensePanelInvitationLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('course_major_abbr', models.CharField(blank=True, max_length=256)),
                ('dit_head_username', models.CharField(max_length=256)),
                ('dit_head_full_name', models.CharField(max_length=256)),
                ('dit_head_response', models.CharField(max_length=256)),
                ('dit_head_response_date', models.CharField(max_length=256)),
                ('dit_head_signature', models.BooleanField(default=False)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_response', models.CharField(max_length=256)),
                ('panel_response_date', models.CharField(max_length=256)),
                ('panel_signature', models.BooleanField(default=False)),
                ('panel_attendance', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_date', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_start_time', models.CharField(blank=True, max_length=256)),
                ('research_title_defense_end_time', models.CharField(blank=True, max_length=256)),
                ('form_date_sent', models.CharField(max_length=256)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='studentleader',
            name='bet3_proposal_defense_panel_invitation_status',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='studentleader',
            name='bet3_proposal_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='studentleader',
            name='research_proposal_defense_date',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='studentleader',
            name='research_proposal_defense_end_time',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='studentleader',
            name='research_proposal_defense_start_time',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]