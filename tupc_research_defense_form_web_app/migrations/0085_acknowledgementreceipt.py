# Generated by Django 4.0.4 on 2022-12-21 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0084_studentleader_acknowledgement_receipt'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcknowledgementReceipt',
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
                ('adaa_username', models.CharField(max_length=256)),
                ('adaa_full_name', models.CharField(max_length=256)),
                ('adaa_response', models.CharField(max_length=256)),
                ('adaa_response_date', models.CharField(max_length=256)),
                ('adaa_signature', models.BooleanField(default=False)),
                ('library_username', models.CharField(max_length=256)),
                ('library_full_name', models.CharField(max_length=256)),
                ('library_response', models.CharField(max_length=256)),
                ('library_response_date', models.CharField(max_length=256)),
                ('library_signature', models.BooleanField(default=False)),
                ('research_ext_username', models.CharField(max_length=256)),
                ('research_ext_full_name', models.CharField(max_length=256)),
                ('research_ext_response', models.CharField(max_length=256)),
                ('research_ext_response_date', models.CharField(max_length=256)),
                ('research_ext_signature', models.BooleanField(default=False)),
                ('adviser_ext_username', models.CharField(max_length=256)),
                ('adviser_ext_full_name', models.CharField(max_length=256)),
                ('adviser_ext_response', models.CharField(max_length=256)),
                ('adviser_ext_response_date', models.CharField(max_length=256)),
                ('adviser_ext_signature', models.BooleanField(default=False)),
                ('subject_teacher_ext_username', models.CharField(max_length=256)),
                ('subject_teacher_ext_full_name', models.CharField(max_length=256)),
                ('subject_teacher_ext_response', models.CharField(max_length=256)),
                ('subject_teacher_ext_response_date', models.CharField(max_length=256)),
                ('subject_teacher_ext_signature', models.BooleanField(default=False)),
                ('research_title', models.CharField(blank=True, max_length=256)),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
    ]
