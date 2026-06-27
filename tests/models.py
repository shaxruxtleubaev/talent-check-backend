from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings 
from datetime import datetime

class CustomUser(AbstractUser):
    """Talabalar uchun qo'shimcha ma'lumotlar bilan kengaytirilgan foydalanuvchi modeli"""
    fullname = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    university = models.CharField(max_length=255, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Override username to use passport format AA0000000
    username = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{7}$',
                message='Username must be in format AA0000000 (2 letters + 7 digits)',
                code='invalid_username'
            )
        ]
    )
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
    
    def __str__(self):
        return f"{self.username} - {self.fullname}"


class UserActivity(models.Model):
    """Foydalanuvchining login va portalga kirish tarixi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100) # 'Login' yoki 'Portalni ochdi'
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kirish Faolligi"
        verbose_name_plural = "Kirish Faolliklari"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class Test(models.Model):
    """Test/Quiz modeli"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
    
    def __str__(self):
        return self.title
    
    def get_question_count(self):
        return self.questions.count()


class Question(models.Model):
    """Savol modeli"""
    ANSWER_CHOICES = [
        ('A', 'A variyant'),
        ('B', 'B variyant'),
        ('C', 'C variyant'),
        ('D', 'D variyant'),
    ]
    
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
    
    def __str__(self):
        return f"{self.test.title} - ID {self.id}: {self.text[:50]}"


class TestResult(models.Model):
    """Test natijasi/topshirish modeli"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    total_questions = models.IntegerField(default=20)
    correct_count = models.IntegerField()
    time_taken = models.IntegerField(help_text="Soniyalar bilan o'tgan vaqt")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Test Natijasi"
        verbose_name_plural = "Test Natijalari"
    
    def __str__(self):
        return f"{self.user.username} - {self.test.title} - Natija: {self.score}"
    
    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_count / self.total_questions) * 100, 2)


class QuestionAnswer(models.Model):
    """Test natijasidagi savolga bergan javob modeli"""
    ANSWER_CHOICES = [
        ('A', 'A variyant'),
        ('B', 'B variyant'),
        ('C', 'C variyant'),
        ('D', 'D variyant'),
        ('', 'Javob berilmadi'),
    ]
    
    test_result = models.ForeignKey('TestResult', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, blank=True)
    is_correct = models.BooleanField(default=False)
    time_spent = models.IntegerField(help_text="Bu savol uchun soniyalar bilan o'tgan vaqt")
    
    class Meta:
        ordering = ['test_result', 'id']
        verbose_name = "Savol Javob"
        verbose_name_plural = "Savol Javoblari"
    
    def __str__(self):
        return f"{self.test_result} - Q_ID {self.question.id}: {self.user_answer or 'Javob yoq'}"