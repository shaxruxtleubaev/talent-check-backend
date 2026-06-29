from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Sum, Avg
from django.utils import timezone
from .models import CustomUser, Test, Question, TestResult, QuestionAnswer, UserActivity
from .serializers import (
    CustomUserSerializer, LoginSerializer, TokenSerializer,
    TestSerializer, TestDetailSerializer, TestResultSerializer,
    TestResultListSerializer, SubmitTestSerializer, QuestionAnswerSerializer,
    FinalAnalyticsSerializer
)

class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login endpoint - returns access and refresh tokens"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # --- LOG ACTIVITY ---
        UserActivity.objects.create(
            user=user,
            action="Tizimga kirdi (Login)",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        user.last_seen = timezone.now()
        user.save()
        # --------------------
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': CustomUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Refresh access token"""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSet):
    """User profile endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            # --- LOG ACTIVITY (Portal opened) ---
            now = timezone.now()
            if not request.user.last_seen or (now - request.user.last_seen).total_seconds() > 900:
                UserActivity.objects.create(
                    user=request.user,
                    action="Portalni ochdi",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            
            request.user.last_seen = now
            request.user.save()
            # ------------------------------------

            serializer = CustomUserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        elif request.method == 'PUT':
            serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def results(self, request):
        """Get user's test results"""
        results = TestResult.objects.filter(user=request.user)
        serializer = TestResultListSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def final_analytics(self, request):
        """Psychometric results: Only available if ALL existing tests are completed."""
        user = request.user
        total_tests_available = Test.objects.count()
        completed_tests_count = TestResult.objects.filter(user=user).values('test').distinct().count()

        # Block if user hasn't tried every test type at least once
        if completed_tests_count < total_tests_available:
            return Response({
                'locked': True, 
                'message': 'Barcha mavjud testlarni yakunlang',
                'progress': f"{completed_tests_count}/{total_tests_available}"
            }, status=status.HTTP_403_FORBIDDEN)

        # Aggregate metrics
        user_results = TestResult.objects.filter(user=user)
        total_questions = user_results.aggregate(Sum('total_questions'))['total_questions__sum'] or 0
        total_correct = user_results.aggregate(Sum('correct_count'))['correct_count__sum'] or 0
        total_time = user_results.aggregate(Sum('time_taken'))['time_taken__sum'] or 0
        
        # PRECISENESS: Overall accuracy percentage across all tests
        preciseness = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # ATTENTIVENESS Logic:
        # We analyze individual answers. A "Careless Mistake" is when the user answers
        # incorrectly but spends very little time (< 5 seconds) on that specific question.
        all_answers = QuestionAnswer.objects.filter(test_result__user=user)
        fast_mistakes = all_answers.filter(is_correct=False, time_spent__lt=5).count()
        
        # Deduct 5% per careless mistake from a base of 100
        attentiveness = max(0, 100 - (fast_mistakes * 5))

        data = {
            'attentiveness_score': round(attentiveness, 2),
            'preciseness_score': round(preciseness, 2),
            'total_time_spent': total_time,
            'total_mistakes': total_questions - total_correct,
            'total_tests_completed': completed_tests_count,
            'overall_accuracy': round(preciseness, 2)
        }
        return Response(data)


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """Test management endpoints"""
    permission_classes = [IsAuthenticated]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestDetailSerializer
        return TestSerializer
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit test answers"""
        test = self.get_object()
        serializer = SubmitTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        answers_data = serializer.validated_data['answers']
        time_taken = serializer.validated_data['time_taken']
        
        with transaction.atomic():
            # Create test result
            test_result = TestResult.objects.create(
                user=request.user,
                test=test,
                total_questions=len(answers_data),
                time_taken=time_taken,
                score=0,
                correct_count=0
            )
            
            correct_count = 0
            score = 0
            
            # Create individual question answers
            for answer_data in answers_data:
                question_id = answer_data.get('question')
                try:
                    question = Question.objects.get(id=question_id, test=test)
                except Question.DoesNotExist:
                    continue
                
                user_answer = answer_data.get('user_answer', '')
                is_correct = user_answer == question.correct_answer
                
                if is_correct:
                    correct_count += 1
                    score += 1
                
                QuestionAnswer.objects.create(
                    test_result=test_result,
                    question=question,
                    user_answer=user_answer,
                    is_correct=is_correct,
                    time_spent=answer_data.get('time_spent', 0)
                )
            
            # Update test result with calculated score
            test_result.score = score
            test_result.correct_count = correct_count
            test_result.save()
        
        result_serializer = TestResultSerializer(test_result)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)