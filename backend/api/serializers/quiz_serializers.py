from rest_framework import serializers
from api.models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'options', 'explanation', 'points', 'order']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'instructions', 'passing_score', 'questions', 'created_at']


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers"""
    quiz_id = serializers.IntegerField()
    answers = serializers.DictField(child=serializers.CharField())
