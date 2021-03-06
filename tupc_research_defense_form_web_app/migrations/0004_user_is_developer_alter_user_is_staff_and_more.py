# Generated by Django 4.0.4 on 2022-07-13 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tupc_research_defense_form_web_app', '0003_remove_user_is_developer_alter_user_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_developer',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=True),
        ),
    ]
