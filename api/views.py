from rest_framework import viewsets
from .models import Student
from .serializers import StudentSerializer
from .ml_logic import predict_student_success

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer  # ✅ Fixed

    def perform_create(self, serializer):
        hours = serializer.validated_data['study_hours']
        attendance = serializer.validated_data['attendance']
        result = predict_student_success(hours, attendance)
        serializer.save(prediction=result)