from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Subject, Grade, CurriculumCapsule, Quiz, Question,
    LearnerProfile, LearningProgress, QuizAttempt,
    TextbookChapter, GeneratedLesson, LessonSection, GeneratedQuestion
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


# AI-Assisted Lesson Generation Admin


@admin.register(TextbookChapter)
class TextbookChapterAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject', 'grade', 'chapter_number', 
        'status_badge', 'word_count', 'uploaded_by', 'created_at'
    ]
    list_filter = ['status', 'subject', 'grade', 'created_at']
    search_fields = ['title', 'source_book', 'chapter_number']
    readonly_fields = ['uploaded_by', 'status', 'processing_notes', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subject', 'grade', 'chapter_number')
        }),
        ('Content', {
            'fields': ('raw_content', 'source_book', 'page_numbers')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['generate_lessons_action']
    
    def status_badge(self, obj):
        colors = {
            'uploaded': 'blue',
            'processing': 'orange',
            'generated': 'green',
            'published': 'darkgreen',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def word_count(self, obj):
        count = len(obj.raw_content.split())
        return f'{count:,} words'
    word_count.short_description = 'Word Count'
    
    def generate_lessons_action(self, request, queryset):
        from api.services import LessonGeneratorService
        generator = LessonGeneratorService()
        
        success = 0
        for chapter in queryset:
            if chapter.status in ['uploaded', 'failed']:
                lesson = generator.generate_lesson_from_chapter(chapter)
                if lesson:
                    success += 1
        
        self.message_user(request, f'Successfully generated {success} lessons from {queryset.count()} chapters.')
    generate_lessons_action.short_description = 'Generate lessons from selected chapters'


class LessonSectionInline(admin.TabularInline):
    model = LessonSection
    extra = 0
    fields = ['section_type', 'title', 'order', 'has_interactive_elements']
    readonly_fields = ['section_type', 'title', 'order']


class GeneratedQuestionInline(admin.TabularInline):
    model = GeneratedQuestion
    extra = 0
    fields = ['question_text_short', 'question_type', 'difficulty_level', 'order']
    readonly_fields = ['question_text_short', 'question_type', 'difficulty_level', 'order']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(GeneratedLesson)
class GeneratedLessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject_display', 'grade_display', 'status_badge',
        'quality_score', 'sections_count', 'questions_count',
        'reviewed_by', 'created_at'
    ]
    list_filter = [
        'status', 'difficulty_level', 'source_chapter__subject',
        'source_chapter__grade', 'reviewed_at'
    ]
    search_fields = ['title', 'introduction', 'source_chapter__title']
    readonly_fields = [
        'source_chapter', 'ai_model_used', 'generation_timestamp',
        'generation_params', 'quality_score', 'created_at', 'updated_at',
        'published_capsule_link'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_chapter', 'title', 'introduction', 'difficulty_level')
        }),
        ('Learning Content', {
            'fields': ('learning_objectives', 'key_concepts', 'estimated_duration')
        }),
        ('Review & Approval', {
            'fields': ('status', 'reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('AI Generation Info', {
            'fields': ('ai_model_used', 'generation_timestamp', 'generation_params', 'quality_score'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('published_capsule_link',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [LessonSectionInline, GeneratedQuestionInline]
    actions = ['approve_lessons', 'reject_lessons', 'publish_lessons']
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'review': 'blue',
            'approved': 'green',
            'published': 'darkgreen',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def subject_display(self, obj):
        return obj.source_chapter.subject.name
    subject_display.short_description = 'Subject'
    
    def grade_display(self, obj):
        return obj.source_chapter.grade.name
    grade_display.short_description = 'Grade'
    
    def sections_count(self, obj):
        return obj.sections.count()
    sections_count.short_description = 'Sections'
    
    def questions_count(self, obj):
        return obj.generated_questions.count()
    questions_count.short_description = 'Questions'
    
    def published_capsule_link(self, obj):
        if obj.published_capsule:
            url = reverse('admin:api_curriculumcapsule_change', args=[obj.published_capsule.id])
            return format_html('<a href="{}">View Capsule #{}</a>', url, obj.published_capsule.id)
        return 'Not published'
    published_capsule_link.short_description = 'Published Capsule'
    
    def approve_lessons(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'Approved {count} lessons.')
    approve_lessons.short_description = 'Approve selected lessons'
    
    def reject_lessons(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'Rejected {count} lessons.')
    reject_lessons.short_description = 'Reject selected lessons'
    
    def publish_lessons(self, request, queryset):
        from api.services import LessonGeneratorService
        generator = LessonGeneratorService()
        
        success = 0
        for lesson in queryset:
            if not lesson.published_capsule and lesson.status in ['approved', 'draft']:
                capsule = generator.publish_lesson_to_capsule(lesson)
                if capsule:
                    success += 1
        
        self.message_user(request, f'Published {success} lessons from {queryset.count()} selected.')
    publish_lessons.short_description = 'Publish selected lessons to capsules'


@admin.register(LessonSection)
class LessonSectionAdmin(admin.ModelAdmin):
    list_display = [
        'lesson', 'section_type', 'title', 'order',
        'has_interactive_elements', 'content_length'
    ]
    list_filter = ['section_type', 'has_interactive_elements', 'lesson__status']
    search_fields = ['title', 'content', 'lesson__title']
    fields = [
        'lesson', 'section_type', 'title', 'content', 'order',
        'has_interactive_elements', 'interactive_data',
        'embedded_questions', 'hints', 'additional_notes'
    ]
    
    def content_length(self, obj):
        length = len(obj.content)
        return f'{length:,} chars'
    content_length.short_description = 'Content Length'


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'get_short_text', 'lesson', 'question_type',
        'difficulty_level', 'points', 'order'
    ]
    list_filter = [
        'question_type', 'difficulty_level',
        'lesson__status', 'lesson__source_chapter__subject'
    ]
    search_fields = ['question_text', 'lesson__title', 'explanation']
    fields = [
        'lesson', 'section', 'question_text', 'question_type',
        'difficulty_level', 'options', 'correct_answer',
        'explanation', 'hints', 'bloom_taxonomy_level',
        'points', 'order'
    ]
    
    def get_short_text(self, obj):
        return obj.question_text[:60] + '...' if len(obj.question_text) > 60 else obj.question_text
    get_short_text.short_description = 'Question'
