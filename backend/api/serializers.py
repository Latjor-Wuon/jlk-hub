from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Subject, Grade, CurriculumCapsule, Quiz, Question,
    LearnerProfile, LearningProgress, QuizAttempt
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'icon', 'created_at']


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'level', 'description']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'options', 'explanation', 'points', 'order']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'instructions', 'passing_score', 'questions', 'created_at']


class CurriculumCapsuleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    
    class Meta:
        model = CurriculumCapsule
        fields = [
            'id', 'title', 'subject', 'subject_name', 'grade', 'grade_name',
            'description', 'content', 'objectives', 'order', 'estimated_duration',
            'is_published', 'quizzes', 'created_at', 'updated_at'
        ]


class CurriculumCapsuleListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing capsules without full content"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    quiz_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CurriculumCapsule
        fields = [
            'id', 'title', 'subject', 'subject_name', 'grade', 'grade_name',
            'description', 'objectives', 'order', 'estimated_duration',
            'is_published', 'quiz_count', 'created_at'
        ]
    
    def get_quiz_count(self, obj):
        return obj.quizzes.count()


class LearnerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    
    class Meta:
        model = LearnerProfile
        fields = ['id', 'username', 'grade', 'grade_name', 'school_name', 'date_of_birth', 'created_at']


class LearningProgressSerializer(serializers.ModelSerializer):
    capsule_title = serializers.CharField(source='capsule.title', read_only=True)
    
    class Meta:
        model = LearningProgress
        fields = [
            'id', 'learner', 'capsule', 'capsule_title', 'is_completed',
            'completion_percentage', 'time_spent', 'last_accessed', 'started_at'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    learner_username = serializers.CharField(source='learner.username', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'learner', 'learner_username', 'quiz', 'quiz_title',
            'score', 'max_score', 'passed', 'answers', 'completed_at'
        ]


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers"""
    quiz_id = serializers.IntegerField()
    answers = serializers.DictField(child=serializers.CharField())
