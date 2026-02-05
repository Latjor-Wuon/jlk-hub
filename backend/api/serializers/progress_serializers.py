from rest_framework import serializers
from api.models import LearningProgress, QuizAttempt

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
