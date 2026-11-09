import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=120)),
                ('credits', models.PositiveSmallIntegerField(default=20)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_number', models.CharField(max_length=20, unique=True)),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('study_hours', models.FloatField(help_text='Self-reported study hours per week')),
                ('attendance', models.PositiveSmallIntegerField(help_text='Attendance percentage (0-100)')),
                ('previous_score', models.FloatField(help_text='Previous assessment score (0-100)')),
                ('prediction', models.CharField(blank=True, choices=[('Pass', 'Pass'), ('Fail', 'Fail')], max_length=10)),
                ('probability', models.FloatField(blank=True, help_text='Probability of passing (0-1)', null=True)),
                ('confidence', models.FloatField(blank=True, help_text='Model confidence in the chosen class (0-100)', null=True)),
                ('risk_level', models.CharField(blank=True, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=10)),
                ('actual_result', models.CharField(blank=True, choices=[('Pass', 'Pass'), ('Fail', 'Fail')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='students', to='api.course')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['student_number'],
            },
        ),
        migrations.CreateModel(
            name='PredictionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_hours', models.FloatField()),
                ('attendance', models.PositiveSmallIntegerField()),
                ('previous_score', models.FloatField()),
                ('prediction', models.CharField(choices=[('Pass', 'Pass'), ('Fail', 'Fail')], max_length=10)),
                ('probability', models.FloatField()),
                ('confidence', models.FloatField()),
                ('risk_level', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=10)),
                ('model_version', models.CharField(max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prediction_history', to='api.student')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.CheckConstraint(condition=models.Q(('attendance__gte', 0), ('attendance__lte', 100)), name='student_attendance_0_100'),
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.CheckConstraint(condition=models.Q(('previous_score__gte', 0), ('previous_score__lte', 100)), name='student_previous_score_0_100'),
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.CheckConstraint(condition=models.Q(('study_hours__gte', 0)), name='student_study_hours_positive'),
        ),
    ]
