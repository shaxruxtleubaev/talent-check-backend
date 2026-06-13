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
    list_filter = ('is_staff', 'is_superuser', 'date_joined', 'university')


class QuestionInline(admin.TabularInline):
    """Savollarni testda tahrirlash"""
    model = Question
    extra = 1
    fields = ('order', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
    ordering = ['order']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_question_count', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Asosiy Ma\'lumot', {'fields': ('title', 'description')}),
        ('Metama\'lumot', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'order', 'text', 'correct_answer')
    list_filter = ('test', 'correct_answer', 'created_at')
    search_fields = ('text', 'test__title')
    ordering = ['test', 'order']
    
    fieldsets = (
        ('Savol Tafsillari', {'fields': ('test', 'order', 'text')}),
        ('Variantlar', {'fields': ('option_a', 'option_b', 'option_c', 'option_d')}),
        ('Javob', {'fields': ('correct_answer',)}),
        ('Metama\'lumot', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


class QuestionAnswerInline(admin.TabularInline):
    """Test natijasidagi javoblarni ko'rish"""
    model = QuestionAnswer
    extra = 0
    readonly_fields = ('question', 'user_answer', 'is_correct', 'time_spent')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'correct_count', 'total_questions', 'get_percentage', 'submitted_at')
    list_filter = ('test', 'submitted_at', 'user__university')
    search_fields = ('user__username', 'user__fullname', 'test__title')
    readonly_fields = ('user', 'test', 'score', 'correct_count', 'total_questions', 'time_taken', 'submitted_at', 'get_percentage')
    inlines = [QuestionAnswerInline]
    
    fieldsets = (
        ('Talaba Ma\'lumoti', {'fields': ('user',)}),
        ('Test Ma\'lumoti', {'fields': ('test',)}),
        ('Natijalar', {'fields': ('score', 'correct_count', 'total_questions', 'get_percentage')}),
        ('Vaqt', {'fields': ('time_taken', 'submitted_at')}),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'user_answer', 'is_correct', 'time_spent')
    list_filter = ('is_correct', 'test_result__test', 'question__test')
    search_fields = ('test_result__user__username', 'question__text')
    readonly_fields = ('test_result', 'question', 'user_answer', 'is_correct', 'time_spent')
    
    def has_add_permission(self, request):
        return False
