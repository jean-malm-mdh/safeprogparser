# Generated by Django 4.2.6 on 2023-10-26 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlockModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("program_name", models.CharField(max_length=100)),
                ("program_content", models.FileField(upload_to="DATASTORE/")),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date uploaded"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReportModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("check_name", models.CharField(max_length=30)),
                ("check_verbose_name", models.CharField(max_length=100)),
                ("report_content", models.CharField(max_length=10000)),
                (
                    "block_program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="analyser.blockmodel",
                    ),
                ),
            ],
        ),
    ]
