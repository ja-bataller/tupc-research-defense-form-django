# Generated by Django 4.0.4 on 2022-08-13 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0012_remove_studentleader_is_student_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefenseSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('course', models.CharField(max_length=256)),
                ('form', models.CharField(max_length=256)),
                ('date', models.CharField(max_length=256)),
                ('time', models.CharField(max_length=256)),
                ('status', models.CharField(max_length=256)),
            ],
        ),
    ]
