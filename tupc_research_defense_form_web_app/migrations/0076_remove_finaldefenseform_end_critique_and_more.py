# Generated by Django 4.0.4 on 2022-12-11 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0075_studentleader_research_final_defense_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finaldefenseform',
            name='end_critique',
        ),
        migrations.RemoveField(
            model_name='finaldefenseform',
            name='start_critique',
        ),
        migrations.RemoveField(
            model_name='finaldefenseformlog',
            name='end_critique',
        ),
        migrations.RemoveField(
            model_name='finaldefenseformlog',
            name='start_critique',
        ),
    ]
