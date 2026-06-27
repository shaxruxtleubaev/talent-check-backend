from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.utils import timezone
from .models import CustomUser, Test, Question, TestResult, QuestionAnswer, UserActivity
from .serializers import (
    CustomUserSerializer, LoginSerializer, TokenSerializer,
    TestSerializer, TestDetailSerializer, TestResultSerializer,
    TestResultListSerializer, SubmitTestSerializer, QuestionAnswerSerializer
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
            # We only create a new activity log if it's been more than 15 mins since last seen
            # to avoid spamming the DB on every page refresh
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
            
            for answer_data in answers_data:
                question_id = answer_data.get('question')
                try:
                    question = Question.objects.get(id=question_id, test=test)
                except Question.DoesNotExist:
                    return Response(
                        {'error': f'Question {question_id} not found in this test'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
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
            
            test_result.score = score
            test_result.correct_count = correct_count
            test_result.save()
        
        result_serializer = TestResultSerializer(test_result)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)