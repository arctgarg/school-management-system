# Generated by Django 4.2.18 on 2025-01-15 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AcademicYear",
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
                ("name", models.CharField(max_length=20)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Grade",
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
                ("name", models.CharField(max_length=50)),
                ("annual_fee", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name="Student",
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
                ("admission_number", models.CharField(max_length=20, unique=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("date_of_birth", models.DateField()),
                ("admission_date", models.DateField()),
                ("parent_name", models.CharField(max_length=100)),
                ("contact_number", models.CharField(max_length=20)),
                ("address", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="StudentEnrollment",
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
                ("total_fee", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "fee_concession",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "academic_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school_management.academicyear",
                    ),
                ),
                (
                    "grade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school_management.grade",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school_management.student",
                    ),
                ),
            ],
            options={
                "unique_together": {("student", "academic_year")},
            },
        ),
        migrations.CreateModel(
            name="FeePayment",
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
                ("payment_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_mode", models.CharField(max_length=50)),
                ("receipt_number", models.CharField(max_length=50)),
                ("remarks", models.TextField(blank=True)),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="school_management.studentenrollment",
                    ),
                ),
            ],
        ),
    ]
