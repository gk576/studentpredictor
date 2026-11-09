from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Course, PredictionRecord, Student


class CourseSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'title', 'credits', 'student_count']


class StudentSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'student_number',
            'full_name',
            'email',
            'course',
            'course_detail',
            'study_hours',
            'attendance',
            'previous_score',
            'prediction',
            'probability',
            'confidence',
            'risk_level',
            'actual_result',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'prediction',
            'probability',
            'confidence',
            'risk_level',
            'created_at',
            'updated_at',
        ]

    def validate_study_hours(self, value):
        if value < 0 or value > 168:
            raise serializers.ValidationError('Study hours must be between 0 and 168 per week.')
        return value

    def validate_attendance(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Attendance must be between 0 and 100.')
        return value

    def validate_previous_score(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Previous score must be between 0 and 100.')
        return value


class PredictionRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_number = serializers.CharField(source='student.student_number', read_only=True)

    class Meta:
        model = PredictionRecord
        fields = [
            'id',
            'student',
            'student_name',
            'student_number',
            'study_hours',
            'attendance',
            'previous_score',
            'prediction',
            'probability',
            'confidence',
            'risk_level',
            'model_version',
            'created_at',
        ]


class PredictRequestSerializer(serializers.Serializer):
    study_hours = serializers.FloatField(min_value=0, max_value=168)
    attendance = serializers.FloatField(min_value=0, max_value=100)
    previous_score = serializers.FloatField(min_value=0, max_value=100)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'username': {'min_length': 3}}

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with that email already exists.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
