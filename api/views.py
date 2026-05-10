from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Student
from .serializers import StudentSerializer, RegisterSerializer
from .ml_logic import predict_student_success, get_model_and_accuracy

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        hours = serializer.validated_data['study_hours']
        attendance = serializer.validated_data['attendance']
        result, confidence, _ = predict_student_success(hours, attendance)
        serializer.save(prediction=result, confidence=confidence)

    def perform_update(self, serializer):
        hours = serializer.validated_data.get('study_hours', serializer.instance.study_hours)
        attendance = serializer.validated_data.get('attendance', serializer.instance.attendance)
        result, confidence, _ = predict_student_success(hours, attendance)
        serializer.save(prediction=result, confidence=confidence)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_stats(request):
    _, accuracy = get_model_and_accuracy()
    total = Student.objects.count()
    passes = Student.objects.filter(prediction='Pass').count()
    fails = Student.objects.filter(prediction='Fail').count()
    return Response({
        'accuracy': accuracy,
        'total_students': total,
        'pass_count': passes,
        'fail_count': fails,
    })
