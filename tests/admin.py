import json
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Avg
from django.utils.html import format_html
from .models import CustomUser, Test, Question, TestResult, QuestionAnswer, UserActivity

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha Ma\'lumot', {'fields': ('fullname', 'date_of_birth', 'university', 'last_seen')}),
    )
    list_display = ('username', 'fullname', 'university', 'last_seen', 'is_staff')
    search_fields = ('username', 'fullname', 'university')
    readonly_fields = ('last_seen',)

    # Diagrammalar uchun maxsus HTML shablonni bog'laymiz
    change_form_template = "admin/custom_user_stats.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        user = self.get_object(request, object_id)
        
        # 1. Akademik ko'rsatkichlar (Radar diagrammasi uchun)
        # Har bir kategoriya bo'yicha o'rtacha foizni hisoblaymiz
        stats = TestResult.objects.filter(user=user).values('test__category').annotate(avg_score=Avg('score'))
        category_map = dict(Test.CATEGORIES)
        
        radar_labels = [category_map.get(s['test__category'], s['test__category']) for s in stats]
        radar_data = [float(s['avg_score']) for s in stats]

        # 2. O'sish dinamikasi (Line graph - barcha testlar tarixi)
        history = TestResult.objects.filter(user=user).order_by('submitted_at')
        line_labels = [h.submitted_at.strftime("%d-%m") for h in history]
        line_data = [h.score for h in history]

        # 3. Reytingdagi o'rni
        # Barcha foydalanuvchilarni o'rtacha bali bo'yicha saralaymiz
        rank_data = TestResult.objects.values('user').annotate(user_avg=Avg('score')).order_by('-user_avg')
        total_users = rank_data.count()
        current_rank = 0
        
        for i, entry in enumerate(rank_data):
            if entry['user'] == int(object_id):
                current_rank = i + 1
                break

        # Ma'lumotlarni JavaScript o'qiy oladigan formatga o'tkazamiz
        extra_context = extra_context or {}
        extra_context.update({
            'chart_labels': json.dumps(radar_labels),
            'chart_data': json.dumps(radar_data),
            'history_labels': json.dumps(line_labels),
            'history_data': json.dumps(line_data),
            'user_rank': current_rank,
            'total_users': total_users,
        })
        
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_link', 'action', 'ip_address')
    list_filter = ('action', 'timestamp', 'user__university')
    search_fields = ('user__username', 'user__fullname')
    readonly_fields = ('user', 'action', 'timestamp', 'ip_address')
    
    def user_link(self, obj):
        return format_html('<a href="/admin/tests/customuser/{}/change/">{}</a>', obj.user.id, obj.user.fullname or obj.user.username)
    user_link.short_description = 'Foydalanuvchi'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'image', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'get_question_count', 'created_at')
    list_filter = ('category', 'created_at')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'text', 'image', 'correct_answer')
    list_filter = ('test',)
    fields = ('test', 'text', 'image', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'correct_count', 'total_questions', 'submitted_at')
    list_filter = ('test', 'submitted_at', 'user__university')
    readonly_fields = ('user', 'test', 'score', 'correct_count', 'total_questions', 'time_taken', 'submitted_at')
    search_fields = ('user__username', 'user__fullname', 'test__title')


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'user_answer', 'is_correct')
    list_filter = ('is_correct',)
    readonly_fields = ('test_result', 'question', 'user_answer', 'is_correct', 'time_spent')