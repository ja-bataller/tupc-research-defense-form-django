# Generated by Django 4.0.4 on 2022-08-13 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0011_studentleader_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentleader',
            name='is_student',
        ),
        migrations.RemoveField(
            model_name='studentleader',
            name='is_user',
        ),
    ]