# Generated by Django 4.0.4 on 2022-12-10 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0073_remove_proposaldefenseform_start_tie_vote_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalDefenseForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('course_major_abbr', models.CharField(blank=True, max_length=256)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_attendance', models.CharField(max_length=256)),
                ('panel_signature_response', models.BooleanField(default=False)),
                ('panel_signature_attach', models.BooleanField(default=False)),
                ('is_panel_chairman', models.BooleanField(default=False)),
                ('panel_chairman_signature_response', models.BooleanField(default=False)),
                ('panel_chairman_signature_attach', models.BooleanField(default=False)),
                ('form_date', models.CharField(max_length=256)),
                ('start_critique', models.BooleanField(default=False)),
                ('end_critique', models.BooleanField(default=False)),
                ('start_voting', models.BooleanField(default=False)),
                ('end_voting', models.BooleanField(default=False)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('defense_date', models.CharField(blank=True, max_length=256)),
                ('defense_start_time', models.CharField(blank=True, max_length=256)),
                ('defense_end_time', models.CharField(blank=True, max_length=256)),
                ('final_defense_response', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FinalDefenseFormLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_leader_username', models.CharField(max_length=256)),
                ('student_leader_full_name', models.CharField(max_length=256)),
                ('course_major_abbr', models.CharField(blank=True, max_length=256)),
                ('panel_username', models.CharField(max_length=256)),
                ('panel_full_name', models.CharField(max_length=256)),
                ('panel_attendance', models.CharField(max_length=256)),
                ('panel_signature_response', models.BooleanField(default=False)),
                ('panel_signature_attach', models.BooleanField(default=False)),
                ('is_panel_chairman', models.BooleanField(default=False)),
                ('panel_chairman_signature_response', models.BooleanField(default=False)),
                ('panel_chairman_signature_attach', models.BooleanField(default=False)),
                ('form_date', models.CharField(max_length=256)),
                ('start_critique', models.BooleanField(default=False)),
                ('end_critique', models.BooleanField(default=False)),
                ('start_voting', models.BooleanField(default=False)),
                ('end_voting', models.BooleanField(default=False)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('defense_date', models.CharField(blank=True, max_length=256)),
                ('defense_start_time', models.CharField(blank=True, max_length=256)),
                ('defense_end_time', models.CharField(blank=True, max_length=256)),
                ('final_defense_response', models.CharField(blank=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FinalPanelInvitation',
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
                ('research_final_defense_date', models.CharField(blank=True, max_length=256)),
                ('research_final_defense_start_time', models.CharField(blank=True, max_length=256)),
                ('research_final_defense_end_time', models.CharField(blank=True, max_length=256)),
                ('form_date_sent', models.CharField(max_length=256)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FinalPanelInvitationLog',
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
                ('research_final_defense_date', models.CharField(blank=True, max_length=256)),
                ('research_final_defense_start_time', models.CharField(blank=True, max_length=256)),
                ('research_final_defense_end_time', models.CharField(blank=True, max_length=256)),
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
            name='bet5_final_defense_panel_invitation_status',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='studentleader',
            name='bet5_final_defense_status',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
