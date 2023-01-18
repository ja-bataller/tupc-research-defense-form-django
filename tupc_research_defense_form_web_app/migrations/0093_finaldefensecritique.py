# Generated by Django 4.0.4 on 2023-01-15 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0092_titledefensecritique_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalDefenseCritique',
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
                ('critique', models.CharField(max_length=256)),
                ('form_status', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('subject_teacher_username', models.CharField(blank=True, max_length=256)),
                ('subject_teacher_full_name', models.CharField(blank=True, max_length=256)),
                ('defense_date', models.CharField(blank=True, max_length=256)),
                ('defense_start_time', models.CharField(blank=True, max_length=256)),
                ('defense_end_time', models.CharField(blank=True, max_length=256)),
                ('research_title', models.CharField(blank=True, max_length=256)),
            ],
        ),
    ]
