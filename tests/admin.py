from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Test, Question, TestResult, QuestionAnswer

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha Ma\'lumot', {'fields': ('fullname', 'date_of_birth', 'university')}),
    )
    list_display = ('username', 'fullname', 'email', 'university', 'is_staff')
    search_fields = ('username', 'fullname', 'university')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    # REMOVED 'order'
    fields = ('text', 'image', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_question_count', 'created_at')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # REMOVED 'order'
    list_display = ('id', 'test', 'text', 'image', 'correct_answer')
    list_filter = ('test',)
    fields = ('test', 'text', 'image', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'correct_count', 'total_questions', 'submitted_at')
    readonly_fields = ('user', 'test', 'score', 'correct_count', 'total_questions', 'time_taken', 'submitted_at')


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'user_answer', 'is_correct')
    readonly_fields = ('test_result', 'question', 'user_answer', 'is_correct', 'time_spent')