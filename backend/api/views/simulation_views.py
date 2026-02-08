"""
Learning Simulation Views

This module provides views for interactive learning simulations
that visually demonstrate science and mathematics concepts.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.utils import timezone
from django.db import models
from api.models import LearningSimulation, SimulationInteraction
from api.serializers.simulation_serializers import (
    LearningSimulationListSerializer, LearningSimulationDetailSerializer,
    SimulationInteractionSerializer, SimulationCompleteSerializer
)


class SimulationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for learning simulations.
    Provides interactive simulations for science and math concepts.
    """
    queryset = LearningSimulation.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LearningSimulationListSerializer
        return LearningSimulationDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter for published simulations unless admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        
        # Optional filters
        subject_id = self.request.query_params.get('subject')
        grade_id = self.request.query_params.get('grade')
        sim_type = self.request.query_params.get('type')
        difficulty = self.request.query_params.get('difficulty')
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        if sim_type:
            queryset = queryset.filter(simulation_type=sim_type)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a simulation and create an interaction record.
        Returns the simulation configuration and interaction ID.
        """
        simulation = self.get_object()
        
        interaction_data = {
            'simulation': simulation,
            'interaction_data': {}
        }
        
        if request.user.is_authenticated:
            interaction_data['learner'] = request.user
            interaction = SimulationInteraction.objects.create(**interaction_data)
            interaction_id = interaction.id
        else:
            interaction_id = None
        
        return Response({
            'simulation': LearningSimulationDetailSerializer(simulation).data,
            'interaction_id': interaction_id,
            'started_at': timezone.now().isoformat()
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a simulation as completed and record interaction data.
        """
        simulation = self.get_object()
        serializer = SimulationCompleteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        interaction_id = data.get('interaction_id')
        
        response_data = {
            'status': 'completed',
            'simulation_id': simulation.id,
            'simulation_title': simulation.title
        }
        
        if request.user.is_authenticated and interaction_id:
            try:
                interaction = SimulationInteraction.objects.get(
                    id=interaction_id,
                    learner=request.user
                )
                interaction.completed_at = timezone.now()
                interaction.time_spent = data.get('time_spent', 0)
                interaction.interaction_data = data.get('interaction_data', {})
                interaction.hints_used = data.get('hints_used', 0)
                interaction.completed_successfully = data.get('completed_successfully', False)
                interaction.save()
                
                response_data['interaction'] = SimulationInteractionSerializer(interaction).data
            except SimulationInteraction.DoesNotExist:
                pass
        
        return response_data
    
    @action(detail=True, methods=['get'])
    def hints(self, request, pk=None):
        """
        Get hints for a simulation.
        Returns hints progressively based on how many have been viewed.
        """
        simulation = self.get_object()
        hint_index = int(request.query_params.get('index', 0))
        
        hints = simulation.hints or []
        
        if hint_index < len(hints):
            return Response({
                'hint': hints[hint_index],
                'hint_number': hint_index + 1,
                'total_hints': len(hints),
                'has_more': hint_index + 1 < len(hints)
            })
        else:
            return Response({
                'hint': None,
                'message': 'No more hints available',
                'total_hints': len(hints)
            })
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available simulation types"""
        return Response({
            'types': [
                {'value': 'math_visualization', 'label': 'Math Visualization'},
                {'value': 'science_experiment', 'label': 'Science Experiment'},
                {'value': 'interactive_diagram', 'label': 'Interactive Diagram'},
                {'value': 'step_by_step', 'label': 'Step by Step Guide'},
            ]
        })
    
    @action(detail=False, methods=['get'])
    def by_capsule(self, request):
        """Get simulations related to a specific capsule"""
        capsule_id = request.query_params.get('capsule_id')
        
        if not capsule_id:
            return Response(
                {'detail': 'capsule_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        simulations = self.get_queryset().filter(related_capsule_id=capsule_id)
        return Response(LearningSimulationListSerializer(simulations, many=True).data)


class SimulationInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing simulation interaction history.
    """
    queryset = SimulationInteraction.objects.all()
    serializer_class = SimulationInteractionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            if not self.request.user.is_staff:
                queryset = queryset.filter(learner=self.request.user)
        else:
            return queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of simulation interactions for current user"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        interactions = SimulationInteraction.objects.filter(learner=request.user)
        
        total_simulations = interactions.values('simulation').distinct().count()
        completed = interactions.filter(completed_successfully=True).count()
        total_time = sum(i.time_spent for i in interactions)
        avg_hints = interactions.aggregate(avg_hints=models.Avg('hints_used'))['avg_hints'] or 0
        
        return Response({
            'total_simulations_tried': total_simulations,
            'completed_successfully': completed,
            'total_time_spent_seconds': total_time,
            'average_hints_used': round(avg_hints, 1)
        })


# Pre-defined simulation configurations for common concepts
SIMULATION_TEMPLATES = {
    'fraction_visualizer': {
        'title': 'Fraction Visualizer',
        'simulation_type': 'math_visualization',
        'config': {
            'type': 'fraction',
            'interactive': True,
            'components': ['numerator_slider', 'denominator_slider', 'pie_chart', 'bar_model'],
            'initial_values': {'numerator': 1, 'denominator': 2}
        },
        'hints': [
            'The numerator (top number) tells you how many parts you have.',
            'The denominator (bottom number) tells you how many equal parts the whole is divided into.',
            'When the numerator equals the denominator, you have one whole.',
            'Try making the numerator larger than the denominator to see an improper fraction.'
        ],
        'learning_objectives': [
            'Understand the relationship between numerator and denominator',
            'Visualize fractions as parts of a whole',
            'Compare fractions using visual models'
        ]
    },
    'water_cycle': {
        'title': 'Water Cycle Simulation',
        'simulation_type': 'science_experiment',
        'config': {
            'type': 'cycle_diagram',
            'interactive': True,
            'stages': ['evaporation', 'condensation', 'precipitation', 'collection'],
            'animations': True,
            'clickable_elements': True
        },
        'hints': [
            'Watch what happens when the sun heats the water.',
            'Notice how water vapor rises and cools to form clouds.',
            'Precipitation can be rain, snow, sleet, or hail.',
            'The cycle repeats continuously in nature.'
        ],
        'learning_objectives': [
            'Understand the four main stages of the water cycle',
            'Explain how the sun drives the water cycle',
            'Describe the process of evaporation and condensation'
        ]
    },
    'simple_circuit': {
        'title': 'Electric Circuit Builder',
        'simulation_type': 'interactive_diagram',
        'config': {
            'type': 'circuit_builder',
            'components': ['battery', 'bulb', 'switch', 'wire'],
            'max_components': 10,
            'show_current_flow': True
        },
        'hints': [
            'A complete circuit needs a power source, like a battery.',
            'The circuit must form a complete loop for electricity to flow.',
            'A switch can break or complete the circuit.',
            'If your bulb doesn\'t light, check if the circuit is complete.'
        ],
        'learning_objectives': [
            'Build a simple electric circuit',
            'Understand that electricity flows in a complete loop',
            'Learn the function of switches in circuits'
        ]
    },
    'multiplication_arrays': {
        'title': 'Multiplication Arrays',
        'simulation_type': 'math_visualization',
        'config': {
            'type': 'array',
            'interactive': True,
            'max_rows': 10,
            'max_columns': 10,
            'show_equation': True,
            'show_skip_counting': True
        },
        'hints': [
            'An array shows equal groups arranged in rows and columns.',
            'Count the number of rows and columns to find the multiplication equation.',
            'Try skip counting by the number in each row.',
            'Notice that 3 × 4 gives the same answer as 4 × 3 (commutative property).'
        ],
        'learning_objectives': [
            'Visualize multiplication as equal groups',
            'Use arrays to understand multiplication facts',
            'Discover the commutative property of multiplication'
        ]
    },
    'plant_growth': {
        'title': 'Plant Growth Experiment',
        'simulation_type': 'science_experiment',
        'config': {
            'type': 'growth_simulation',
            'variables': ['water', 'sunlight', 'soil_type'],
            'time_lapse': True,
            'measurement_tools': ['ruler', 'timer'],
            'stages': ['seed', 'germination', 'seedling', 'mature_plant']
        },
        'hints': [
            'Plants need water, sunlight, and nutrients to grow.',
            'Too much or too little water can harm the plant.',
            'Watch how the plant grows toward the light source.',
            'Different parts of the plant grow at different rates.'
        ],
        'learning_objectives': [
            'Identify what plants need to grow',
            'Observe the stages of plant growth',
            'Understand how changing variables affects plant growth'
        ]
    }
}
