# Generated by Django 4.2.16 on 2024-09-06 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ExitReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason_category', models.CharField(choices=[('money', 'Money'), ('miscommunication', 'Miscommunication'), ('other', 'Other')], max_length=50)),
                ('detailed_reason', models.TextField(blank=True, null=True)),
                ('exit_date', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.driver')),
            ],
        ),
    ]
