# Generated by Django 5.1.5 on 2025-01-31 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_quiz_duration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quizanswer',
            old_name='questions',
            new_name='question',
        ),
    ]
