# Generated by Django 5.1.5 on 2025-01-31 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_rename_questions_quizanswer_question'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quizanswer',
            old_name='question',
            new_name='questions',
        ),
    ]
