# Generated by Django 5.1.5 on 2025-01-30 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_quizattempt_alter_quizanswer_session_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='duration',
            field=models.DurationField(help_text='Duration in HH:MM:SS format'),
        ),
    ]
