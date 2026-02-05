from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from api.models import LearningProgress, QuizAttempt
from api.serializers import LearningProgressSerializer, QuizAttemptSerializer


class LearningProgressViewSet(viewsets.ModelViewSet):
    """API endpoint for learning progress tracking"""
    queryset = LearningProgress.objects.all()
    serializer_class = LearningProgressSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        learner_id = self.request.query_params.get('learner')
        
        if learner_id:
            queryset = queryset.filter(learner_id=learner_id)
        elif self.request.user.is_authenticated:
            queryset = queryset.filter(learner=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get learning progress summary"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        progress = self.get_queryset().filter(learner=request.user)
        total_capsules = progress.count()
        completed = progress.filter(is_completed=True).count()
        avg_completion = progress.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
        
        return Response({
            'total_capsules_started': total_capsules,
            'completed_capsules': completed,
            'average_completion': round(avg_completion, 2),
            'in_progress': total_capsules - completed
        })


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for quiz attempts"""
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            queryset = queryset.filter(learner=self.request.user)
        
        return queryset
