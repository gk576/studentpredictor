from django.conf import settings
from django.db import models


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=120)
    credits = models.PositiveSmallIntegerField(default=20)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.title}'


class Student(models.Model):
    class Result(models.TextChoices):
        PASS = 'Pass', 'Pass'
        FAIL = 'Fail', 'Fail'

    class Risk(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'

    student_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='students',
        null=True,
        blank=True,
    )

    study_hours = models.FloatField(help_text='Self-reported study hours per week')
    attendance = models.PositiveSmallIntegerField(help_text='Attendance percentage (0-100)')
    previous_score = models.FloatField(help_text='Previous assessment score (0-100)')

    prediction = models.CharField(max_length=10, choices=Result.choices, blank=True)
    probability = models.FloatField(
        null=True, blank=True, help_text='Probability of passing (0-1)'
    )
    confidence = models.FloatField(
        null=True, blank=True, help_text='Model confidence in the chosen class (0-100)'
    )
    risk_level = models.CharField(max_length=10, choices=Risk.choices, blank=True)

    actual_result = models.CharField(max_length=10, choices=Result.choices, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='students',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_number']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(attendance__gte=0) & models.Q(attendance__lte=100),
                name='student_attendance_0_100',
            ),
            models.CheckConstraint(
                condition=models.Q(previous_score__gte=0) & models.Q(previous_score__lte=100),
                name='student_previous_score_0_100',
            ),
            models.CheckConstraint(
                condition=models.Q(study_hours__gte=0),
                name='student_study_hours_positive',
            ),
        ]

    def __str__(self):
        return f'{self.student_number} - {self.full_name}'


class PredictionRecord(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='prediction_history',
        null=True,
        blank=True,
    )

    study_hours = models.FloatField()
    attendance = models.PositiveSmallIntegerField()
    previous_score = models.FloatField()

    prediction = models.CharField(max_length=10, choices=Student.Result.choices)
    probability = models.FloatField()
    confidence = models.FloatField()
    risk_level = models.CharField(max_length=10, choices=Student.Risk.choices)
    model_version = models.CharField(max_length=40)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student or "ad-hoc"} -> {self.prediction} ({self.confidence}%)'
