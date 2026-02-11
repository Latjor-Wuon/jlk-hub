"""
Serializers for AI-Assisted Lesson Generation
"""
from rest_framework import serializers
from api.models import (
    TextbookChapter,
    GeneratedLesson,
    LessonSection,
    GeneratedQuestion,
    Subject,
    Grade
)


class TextbookChapterSerializer(serializers.ModelSerializer):
    """Serializer for textbook chapter uploads"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = TextbookChapter
        fields = [
            'id', 'title', 'subject', 'subject_name', 'grade', 'grade_name',
            'chapter_number', 'raw_content', 'source_book', 'page_numbers',
            'status', 'uploaded_by', 'uploaded_by_username', 'processing_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'uploaded_by', 'processing_notes', 'created_at', 'updated_at']
    
    def validate_raw_content(self, value):
        """Ensure content is substantial enough"""
        if len(value.split()) < 100:
            raise serializers.ValidationError(
                "Content too short. Minimum 100 words required for lesson generation."
            )
        return value


class TextbookChapterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for chapter lists"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    word_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TextbookChapter
        fields = [
            'id', 'title', 'subject_name', 'grade_name', 'chapter_number',
            'status', 'word_count', 'created_at'
        ]
    
    def get_word_count(self, obj):
        """Calculate word count"""
        return len(obj.raw_content.split())


class LessonSectionSerializer(serializers.ModelSerializer):
    """Serializer for lesson sections"""
    
    class Meta:
        model = LessonSection
        fields = [
            'id', 'section_type', 'title', 'content', 'order',
            'has_interactive_elements', 'interactive_data',
            'embedded_questions', 'hints', 'additional_notes'
        ]


class GeneratedQuestionSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated questions"""
    section_title = serializers.CharField(source='section.title', read_only=True)
    
    class Meta:
        model = GeneratedQuestion
        fields = [
            'id', 'question_text', 'question_type', 'difficulty_level',
            'options', 'correct_answer', 'explanation', 'hints',
            'bloom_taxonomy_level', 'points', 'order', 'section', 'section_title'
        ]


class GeneratedLessonSerializer(serializers.ModelSerializer):
    """Detailed serializer for generated lessons"""
    sections = LessonSectionSerializer(many=True, read_only=True)
    generated_questions = GeneratedQuestionSerializer(many=True, read_only=True)
    source_chapter_title = serializers.CharField(source='source_chapter.title', read_only=True)
    subject_name = serializers.CharField(source='source_chapter.subject.name', read_only=True)
    grade_name = serializers.CharField(source='source_chapter.grade.name', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    published_capsule_id = serializers.IntegerField(source='published_capsule.id', read_only=True)
    sections_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedLesson
        fields = [
            'id', 'source_chapter', 'source_chapter_title', 'subject_name', 'grade_name',
            'title', 'introduction', 'learning_objectives', 'key_concepts',
            'estimated_duration', 'difficulty_level', 'status',
            'ai_model_used', 'generation_timestamp', 'generation_params', 'quality_score',
            'reviewed_by', 'reviewed_by_username', 'review_notes', 'reviewed_at',
            'published_capsule', 'published_capsule_id',
            'sections', 'generated_questions', 'sections_count', 'questions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'ai_model_used', 'generation_timestamp', 'generation_params',
            'quality_score', 'created_at', 'updated_at'
        ]
    
    def get_sections_count(self, obj):
        """Get number of sections"""
        return obj.sections.count()
    
    def get_questions_count(self, obj):
        """Get number of questions"""
        return obj.generated_questions.count()


class GeneratedLessonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lesson lists"""
    subject_name = serializers.CharField(source='source_chapter.subject.name', read_only=True)
    grade_name = serializers.CharField(source='source_chapter.grade.name', read_only=True)
    sections_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedLesson
        fields = [
            'id', 'title', 'subject_name', 'grade_name', 'status',
            'difficulty_level', 'estimated_duration', 'quality_score',
            'sections_count', 'questions_count', 'created_at'
        ]
    
    def get_sections_count(self, obj):
        return obj.sections.count()
    
    def get_questions_count(self, obj):
        return obj.generated_questions.count()


class LessonGenerationRequestSerializer(serializers.Serializer):
    """Serializer for lesson generation requests"""
    chapter_id = serializers.IntegerField(required=True)
    use_openai = serializers.BooleanField(default=False)
    validate_only = serializers.BooleanField(default=False)
    
    def validate_chapter_id(self, value):
        """Ensure chapter exists"""
        try:
            chapter = TextbookChapter.objects.get(id=value)
            if chapter.status == 'processing':
                raise serializers.ValidationError(
                    "Chapter is already being processed."
                )
        except TextbookChapter.DoesNotExist:
            raise serializers.ValidationError("Chapter not found.")
        return value


class LessonPublishSerializer(serializers.Serializer):
    """Serializer for publishing lessons to curriculum capsules"""
    lesson_id = serializers.IntegerField(required=True)
    
    def validate_lesson_id(self, value):
        """Ensure lesson exists and is ready to publish"""
        try:
            lesson = GeneratedLesson.objects.get(id=value)
            if lesson.status not in ['approved', 'draft']:
                raise serializers.ValidationError(
                    f"Lesson must be in 'approved' or 'draft' status to publish. Current: {lesson.status}"
                )
        except GeneratedLesson.DoesNotExist:
            raise serializers.ValidationError("Lesson not found.")
        return value


class LessonReviewSerializer(serializers.Serializer):
    """Serializer for reviewing generated lessons"""
    lesson_id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(
        choices=['approved', 'rejected'],
        required=True
    )
    review_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_lesson_id(self, value):
        """Ensure lesson exists"""
        try:
            GeneratedLesson.objects.get(id=value)
        except GeneratedLesson.DoesNotExist:
            raise serializers.ValidationError("Lesson not found.")
        return value


class BatchGenerationSerializer(serializers.Serializer):
    """Serializer for batch lesson generation"""
    chapter_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=50
    )
    use_openai = serializers.BooleanField(default=False)
    
    def validate_chapter_ids(self, value):
        """Ensure all chapters exist"""
        existing_chapters = TextbookChapter.objects.filter(
            id__in=value
        ).values_list('id', flat=True)
        
        missing = set(value) - set(existing_chapters)
        if missing:
            raise serializers.ValidationError(
                f"Chapters not found: {missing}"
            )
        return value
