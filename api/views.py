from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .ml_logic import get_model_metrics, predict_student
from .models import Course, PredictionRecord, Student
from .serializers import (
    CourseSerializer,
    PredictRequestSerializer,
    PredictionRecordSerializer,
    RegisterSerializer,
    StudentSerializer,
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.annotate(student_count=Count('students'))
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Student.objects.filter(created_by=self.request.user)
            .select_related('course')
            .order_by('student_number')
        )

    def _save_with_prediction(self, serializer, creating: bool):
        instance = serializer.instance
        study_hours = serializer.validated_data.get(
            'study_hours', getattr(instance, 'study_hours', 0)
        )
        attendance = serializer.validated_data.get(
            'attendance', getattr(instance, 'attendance', 0)
        )
        previous_score = serializer.validated_data.get(
            'previous_score', getattr(instance, 'previous_score', 0)
        )

        result = predict_student(study_hours, attendance, previous_score)

        extra = {
            'prediction': result['prediction'],
            'probability': result['probability'],
            'confidence': result['confidence'],
            'risk_level': result['risk_level'],
        }
        if creating:
            extra['created_by'] = self.request.user

        student = serializer.save(**extra)

        PredictionRecord.objects.create(
            student=student,
            study_hours=study_hours,
            attendance=attendance,
            previous_score=previous_score,
            prediction=result['prediction'],
            probability=result['probability'],
            confidence=result['confidence'],
            risk_level=result['risk_level'],
            model_version=result['model_version'],
        )
        return student

    def perform_create(self, serializer):
        self._save_with_prediction(serializer, creating=True)

    def perform_update(self, serializer):
        self._save_with_prediction(serializer, creating=False)


class PredictionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredictionRecord.objects.all()
    serializer_class = PredictionRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PredictionRecord.objects.filter(
            student__created_by=self.request.user
        ).select_related('student')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_view(request):
    request_serializer = PredictRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    result = predict_student(**data)

    PredictionRecord.objects.create(
        student=None,
        study_hours=data['study_hours'],
        attendance=data['attendance'],
        previous_score=data['previous_score'],
        prediction=result['prediction'],
        probability=result['probability'],
        confidence=result['confidence'],
        risk_level=result['risk_level'],
        model_version=result['model_version'],
    )

    return Response({**data, **result})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Account created successfully'},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_stats(request):
    metrics = get_model_metrics()
    students = Student.objects.filter(created_by=request.user)
    total = students.count()
    passes = students.filter(prediction='Pass').count()
    fails = students.filter(prediction='Fail').count()

    with_outcomes = students.exclude(actual_result='')
    outcome_matches = sum(
        1 for student in with_outcomes if student.prediction == student.actual_result
    )

    return Response(
        {
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'confusion_matrix': metrics['confusion_matrix'],
            'feature_importance': metrics['feature_importance'],
            'model_version': metrics['model_version'],
            'algorithm': metrics['algorithm'],
            'dataset_samples': metrics['dataset_samples'],
            'total_students': total,
            'pass_count': passes,
            'fail_count': fails,
            'high_risk_count': students.filter(risk_level='High').count(),
            'known_outcomes': with_outcomes.count(),
            'outcome_matches': outcome_matches,
        }
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'mode': 'local'})
