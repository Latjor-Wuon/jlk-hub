from rest_framework import serializers
from api.models import (
    LearnerDifficultyLevel, LearningRecommendation, 
    RevisionActivity, CurriculumCapsule
)


class LearnerDifficultyLevelSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = LearnerDifficultyLevel
        fields = [
            'id', 'learner', 'subject', 'subject_name', 'current_level',
            'average_score', 'total_attempts', 'consecutive_passes',
            'consecutive_fails', 'updated_at'
        ]
        read_only_fields = ['learner', 'updated_at']


class LearningRecommendationSerializer(serializers.ModelSerializer):
    capsule_title = serializers.CharField(source='capsule.title', read_only=True)
    capsule_subject = serializers.CharField(source='capsule.subject.name', read_only=True)
    suggested_capsule_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningRecommendation
        fields = [
            'id', 'learner', 'capsule', 'capsule_title', 'capsule_subject',
            'recommendation_type', 'reason', 'suggested_capsule_ids',
            'is_active', 'priority', 'created_at', 'dismissed_at'
        ]
        read_only_fields = ['learner', 'created_at']
    
    def get_suggested_capsule_ids(self, obj):
        return list(obj.suggested_capsules.values_list('id', flat=True))


class RevisionActivitySerializer(serializers.ModelSerializer):
    capsule_title = serializers.CharField(source='capsule.title', read_only=True)
    
    class Meta:
        model = RevisionActivity
        fields = [
            'id', 'learner', 'capsule', 'capsule_title', 'quiz',
            'revision_count', 'last_revision', 'improvement_score', 'notes'
        ]
        read_only_fields = ['learner', 'last_revision']


class AdaptivePathwaySerializer(serializers.Serializer):
    """Serializer for the adaptive learning pathway response"""
    current_performance = serializers.DictField()
    recommendations = LearningRecommendationSerializer(many=True)
    next_lessons = serializers.ListField()
    revision_needed = serializers.ListField()
    strengths = serializers.ListField()
    weaknesses = serializers.ListField()
