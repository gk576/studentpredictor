from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase

from .ml_logic import get_model_metrics, predict_student
from .models import Course, PredictionRecord, Student


class MLPipelineTests(TestCase):
    def test_evaluation_metrics_are_reasonable(self):
        metrics = get_model_metrics()
        self.assertGreaterEqual(metrics['accuracy'], 70)
        self.assertIn('confusion_matrix', metrics)
        self.assertGreaterEqual(metrics['dataset_samples'], 100)

    def test_prediction_returns_expected_fields(self):
        result = predict_student(12, 92, 80)
        self.assertIn(result['prediction'], {'Pass', 'Fail'})
        self.assertGreaterEqual(result['probability'], 0)
        self.assertLessEqual(result['probability'], 1)
        self.assertGreaterEqual(result['confidence'], 50)
        self.assertIn(result['risk_level'], {'Low', 'Medium', 'High'})
        self.assertIn('model_version', result)

    def test_high_and_low_risk_inputs_differ(self):
        strong = predict_student(18, 96, 88)
        weak = predict_student(2, 45, 38)
        self.assertEqual(strong['prediction'], 'Pass')
        self.assertEqual(weak['prediction'], 'Fail')
        self.assertGreater(strong['probability'], weak['probability'])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            predict_student(-1, 80, 70)
        with self.assertRaises(ValueError):
            predict_student(10, 120, 70)
        with self.assertRaises(ValueError):
            predict_student(10, 80, 120)


class StudentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.com', 'StrongPass123!')
        self.other = User.objects.create_user('bob', 'bob@example.com', 'StrongPass123!')
        self.course = Course.objects.create(code='CS101', title='BSc Computer Science', credits=20)
        self.client.force_authenticate(self.user)

    def payload(self, number='STU9001'):
        return {
            'student_number': number,
            'full_name': 'Test Student',
            'email': 'test@example.edu',
            'course': self.course.id,
            'study_hours': 9,
            'attendance': 85,
            'previous_score': 72,
            'actual_result': '',
        }

    def test_create_student_generates_prediction_and_history(self):
        response = self.client.post('/api/students/', self.payload(), format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn(response.data['prediction'], {'Pass', 'Fail'})
        self.assertIsNotNone(response.data['confidence'])
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(PredictionRecord.objects.count(), 1)

    def test_update_re_runs_prediction(self):
        created = self.client.post('/api/students/', self.payload(), format='json').data
        response = self.client.put(
            f'/api/students/{created["id"]}/',
            {**self.payload(), 'attendance': 40, 'previous_score': 35, 'study_hours': 2},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['prediction'], 'Fail')
        self.assertEqual(PredictionRecord.objects.count(), 2)

    def test_predict_endpoint_logs_ad_hoc_inference(self):
        response = self.client.post(
            '/api/predict/',
            {'study_hours': 10, 'attendance': 88, 'previous_score': 75},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('prediction', response.data)
        self.assertEqual(PredictionRecord.objects.filter(student__isnull=True).count(), 1)

    def test_stats_endpoint_returns_model_metrics(self):
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, 200)
        for key in ['accuracy', 'precision', 'recall', 'confusion_matrix']:
            self.assertIn(key, response.data)

    def test_students_are_isolated_per_user(self):
        self.client.post('/api/students/', self.payload(), format='json')
        self.client.force_authenticate(self.other)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_anonymous_access_is_rejected(self):
        client = APIClient()
        response = client.get('/api/students/')
        self.assertEqual(response.status_code, 401)


class AuthAPITests(APITestCase):
    def test_register_and_login(self):
        register = self.client.post(
            '/api/auth/register/',
            {'username': 'newuser', 'email': 'new@example.com', 'password': 'S3curePass!23'},
            format='json',
        )
        self.assertEqual(register.status_code, 201, register.data)
        login = self.client.post(
            '/api/auth/login/',
            {'username': 'newuser', 'password': 'S3curePass!23'},
            format='json',
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn('access', login.data)
