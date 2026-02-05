from django.contrib import admin
from .models import (
    Subject, Grade, CurriculumCapsule, Quiz, Question,
    LearnerProfile, LearningProgress, QuizAttempt
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    fields = ['name', 'description', 'icon']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level']
    list_filter = ['level']
    ordering = ['level']
    fields = ['name', 'level', 'description']


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0
    fields = ['title', 'instructions', 'passing_score']


@admin.register(CurriculumCapsule)
class CurriculumCapsuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'grade', 'order', 'estimated_duration', 'is_published', 'created_at']
    list_filter = ['subject', 'grade', 'is_published']
    search_fields = ['title', 'description']
    list_editable = ['is_published', 'order']
    fields = [
        'title', 
        'subject', 
        'grade', 
        'description', 
        'content',
        'objectives',
        'order',
        'estimated_duration',
        'is_published'
    ]
    inlines = [QuizInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'options', 'correct_answer', 'explanation', 'points', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'capsule', 'passing_score', 'created_at']
    list_filter = ['capsule__subject', 'capsule__grade']
    search_fields = ['title', 'capsule__title']
    fields = ['capsule', 'title', 'instructions', 'passing_score']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['get_short_text', 'quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text']
    fields = ['quiz', 'question_text', 'question_type', 'options', 'correct_answer', 'explanation', 'points', 'order']
    
    def get_short_text(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    get_short_text.short_description = 'Question'


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade', 'school_name', 'created_at']
    list_filter = ['grade']
    search_fields = ['user__username', 'school_name']
    fields = ['user', 'grade', 'school_name', 'date_of_birth']


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ['learner', 'capsule', 'completion_percentage', 'is_completed', 'last_accessed']
    list_filter = ['is_completed', 'capsule__subject', 'capsule__grade']
    search_fields = ['learner__username', 'capsule__title']
    readonly_fields = ['started_at', 'last_accessed']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['learner', 'quiz', 'score', 'max_score', 'passed', 'completed_at']
    list_filter = ['passed', 'quiz']
    search_fields = ['learner__username', 'quiz__title']
    readonly_fields = ['completed_at']
