from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Test, Question, TestResult, QuestionAnswer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'fullname', 'date_of_birth', 'university', 'email')
        read_only_fields = ('id',)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class OptionSerializer(serializers.Serializer):
    """Helper serializer to return question options in a structured way"""
    A = serializers.CharField()
    B = serializers.CharField()
    C = serializers.CharField()
    D = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'options', 'order')
    
    def get_options(self, obj):
        return {
            'A': obj.option_a,
            'B': obj.option_b,
            'C': obj.option_c,
            'D': obj.option_d,
        }


class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Admin view: question with correct answer"""
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'options', 'correct_answer', 'order')
    
    def get_options(self, obj):
        return {
            'A': obj.option_a,
            'B': obj.option_b,
            'C': obj.option_c,
            'D': obj.option_d,
        }


class TestSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source='get_question_count', read_only=True)
    
    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'question_count', 'created_at')
        read_only_fields = ('created_at',)


class TestDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'questions')
    
    def get_questions(self, obj):
        questions = obj.questions.all().order_by('?')[:20]
        return QuestionSerializer(questions, many=True).data


class QuestionAnswerSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    user_answer = serializers.CharField(required=False, allow_blank=True)
    time_spent = serializers.IntegerField()


class SubmitTestSerializer(serializers.Serializer):
    """Serializer for submitting test answers"""
    answers = QuestionAnswerSerializer(many=True)
    time_taken = serializers.IntegerField()
    
    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required")
        return value


class QuestionAnswerResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    correct_answer = serializers.CharField(source='question.correct_answer', read_only=True)
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionAnswer
        fields = ('question_text', 'options', 'user_answer', 'correct_answer', 'is_correct', 'time_spent')
    
    def get_options(self, obj):
        return {
            'A': obj.question.option_a,
            'B': obj.question.option_b,
            'C': obj.question.option_c,
            'D': obj.question.option_d,
        }


class TestResultSerializer(serializers.ModelSerializer):
    answers = QuestionAnswerResultSerializer(many=True, read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = TestResult
        fields = ('id', 'test_title', 'score', 'correct_count', 'total_questions', 'percentage', 'time_taken', 'submitted_at', 'answers')
        read_only_fields = ('id', 'submitted_at')
    
    def get_percentage(self, obj):
        return obj.get_percentage()


class TestResultListSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = TestResult
        fields = ('id', 'test_title', 'score', 'correct_count', 'total_questions', 'percentage', 'time_taken', 'submitted_at')
        read_only_fields = ('submitted_at',)
    
    def get_percentage(self, obj):
        return obj.get_percentage()
