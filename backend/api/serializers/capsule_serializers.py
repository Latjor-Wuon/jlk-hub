from rest_framework import serializers
from api.models import CurriculumCapsule
from api.serializers.quiz_serializers import QuizSerializer


class CurriculumCapsuleSerializer(serializers.ModelSerializer):
    """Full serializer for capsule detail view with quizzes"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    
    class Meta:
        model = CurriculumCapsule
        fields = [
            'id', 'title', 'subject', 'subject_name', 'grade', 'grade_name',
            'description', 'content', 'objectives', 'order', 'estimated_duration',
            'is_published', 'created_at', 'updated_at', 'quizzes'
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
