from rest_framework import serializers
from api.models import LearningSimulation, SimulationInteraction


class LearningSimulationListSerializer(serializers.ModelSerializer):
    """List view serializer for simulations"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    
    class Meta:
        model = LearningSimulation
        fields = [
            'id', 'title', 'description', 'simulation_type',
            'subject', 'subject_name', 'grade', 'grade_name',
            'difficulty_level', 'estimated_time', 'is_published'
        ]


class LearningSimulationDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer with full simulation configuration"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    related_capsule_title = serializers.CharField(
        source='related_capsule.title', read_only=True, allow_null=True
    )
    
    class Meta:
        model = LearningSimulation
        fields = [
            'id', 'title', 'description', 'simulation_type',
            'subject', 'subject_name', 'grade', 'grade_name',
            'related_capsule', 'related_capsule_title',
            'config', 'instructions', 'hints', 'learning_objectives',
            'difficulty_level', 'estimated_time', 'is_published',
            'created_at', 'updated_at'
        ]


class SimulationInteractionSerializer(serializers.ModelSerializer):
    simulation_title = serializers.CharField(source='simulation.title', read_only=True)
    
    class Meta:
        model = SimulationInteraction
        fields = [
            'id', 'learner', 'simulation', 'simulation_title',
            'started_at', 'completed_at', 'time_spent',
            'interaction_data', 'hints_used', 'completed_successfully'
        ]
        read_only_fields = ['learner', 'started_at']


class SimulationStartSerializer(serializers.Serializer):
    """Serializer for starting a simulation"""
    simulation_id = serializers.IntegerField()


class SimulationCompleteSerializer(serializers.Serializer):
    """Serializer for completing a simulation"""
    interaction_id = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    interaction_data = serializers.DictField(required=False, default=dict)
    hints_used = serializers.IntegerField(required=False, default=0)
    completed_successfully = serializers.BooleanField(required=False, default=False)
