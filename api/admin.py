from django.contrib import admin

from .models import Course, PredictionRecord, Student

admin.site.site_header = 'EduPredict Local Administration'
admin.site.site_title = 'EduPredict Admin'
admin.site.index_title = 'Student Performance Predictor MVP'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'credits']
    search_fields = ['code', 'title']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_number',
        'full_name',
        'course',
        'study_hours',
        'attendance',
        'previous_score',
        'prediction',
        'confidence',
        'risk_level',
    ]
    list_filter = ['prediction', 'risk_level', 'course', 'actual_result']
    search_fields = ['student_number', 'full_name', 'email']
    readonly_fields = [
        'prediction',
        'probability',
        'confidence',
        'risk_level',
        'created_at',
        'updated_at',
    ]
    ordering = ['student_number']


@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'student',
        'prediction',
        'probability',
        'confidence',
        'risk_level',
        'model_version',
        'created_at',
    ]
    list_filter = ['prediction', 'risk_level', 'model_version']
    readonly_fields = [field.name for field in PredictionRecord._meta.fields]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
